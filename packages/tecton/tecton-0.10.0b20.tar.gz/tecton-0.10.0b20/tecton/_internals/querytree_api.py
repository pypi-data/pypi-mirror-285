import heapq
import logging
from datetime import datetime
from datetime import timedelta
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import numpy
import pandas
import pendulum
from pyspark import sql as pyspark_sql

import tecton_core.query.dialect
from tecton import types as sdk_types
from tecton._internals import errors
from tecton._internals import rewrite
from tecton._internals import time_utils
from tecton._internals import type_utils
from tecton._internals import utils
from tecton._internals.rewrite import MockDataRewrite
from tecton.framework.data_frame import TectonDataFrame
from tecton_core import conf
from tecton_core import data_types
from tecton_core import errors as core_errors
from tecton_core import feature_set_config
from tecton_core import schema
from tecton_core import specs
from tecton_core.compute_mode import ComputeMode
from tecton_core.feature_definition_wrapper import FeatureDefinitionWrapper
from tecton_core.feature_set_config import FeatureDefinitionAndJoinConfig
from tecton_core.query import builder
from tecton_core.query import node_interface
from tecton_core.query import nodes
from tecton_core.query.builder import build_materialization_querytree
from tecton_core.query.builder import build_pipeline_querytree
from tecton_core.query.dialect import Dialect
from tecton_core.query.node_interface import NodeRef
from tecton_core.schema import Schema
from tecton_core.time_utils import align_time_downwards
from tecton_proto.common import schema__client_pb2 as schema_pb2
from tecton_spark.spark_helper import check_spark_version
from tecton_spark.time_utils import convert_epoch_to_datetime
from tecton_spark.time_utils import convert_timestamp_to_epoch


logger = logging.getLogger(__name__)


def get_historical_features_for_feature_service_with_spine_split(
    dialect: Dialect,
    compute_mode: ComputeMode,
    feature_service_spec: specs.FeatureServiceSpec,
    feature_set_config: feature_set_config.FeatureSetConfig,
    spine: Union[pyspark_sql.DataFrame, pandas.DataFrame, TectonDataFrame, str],
    timestamp_key: Optional[str],
    from_source: Optional[bool],
) -> TectonDataFrame:
    spine_split = _split_spine(spine, feature_set_config.join_keys)
    dfs = []
    for spine_df in spine_split:
        df = get_historical_features_for_feature_service(
            dialect=dialect,
            compute_mode=compute_mode,
            feature_service_spec=feature_service_spec,
            feature_set_config=feature_set_config,
            spine=spine_df,
            timestamp_key=timestamp_key,
            from_source=from_source,
        )
        dfs.append(df)
    return TectonDataFrame._create_from_dataframes(dfs)


def get_historical_features_for_feature_service(
    dialect: Dialect,
    compute_mode: ComputeMode,
    feature_service_spec: specs.FeatureServiceSpec,
    feature_set_config: feature_set_config.FeatureSetConfig,
    spine: Union[pyspark_sql.DataFrame, pandas.DataFrame, TectonDataFrame, str],
    timestamp_key: Optional[str],
    from_source: Optional[bool],
) -> TectonDataFrame:
    timestamp_required = spine is not None and any(
        _should_infer_timestamp_of_spine(fd, timestamp_key) for fd in feature_set_config.feature_definitions
    )

    _validate_sql_string_support(dialect, spine)

    if timestamp_required:
        timestamp_key = timestamp_key or utils.infer_timestamp(spine)

    spine = _create_tecton_df_spine(
        spine_schema=feature_set_config.spine_schema, spine=spine, timestamp_key=timestamp_key
    )

    if spine:
        utils.validate_spine_dataframe(spine, timestamp_key, feature_set_config.request_context_keys)

    user_data_node_metadata = {}
    # TODO: Create a SpineNode with a param of timestamp_key instead of using UserSpecifiedNode.
    user_data_node = nodes.UserSpecifiedDataNode(dialect, compute_mode, spine, user_data_node_metadata)

    if timestamp_key:
        user_data_node_metadata["timestamp_key"] = timestamp_key
        user_data_node = nodes.ConvertTimestampToUTCNode(dialect, compute_mode, user_data_node.as_ref(), timestamp_key)

    tree = builder.build_feature_set_config_querytree(
        dialect,
        compute_mode,
        feature_set_config,
        user_data_node.as_ref(),
        timestamp_key,
        from_source,
    )

    df = TectonDataFrame._create(tree)
    return df


def get_features_in_range(
    dialect: Dialect,
    compute_mode: ComputeMode,
    feature_definition: FeatureDefinitionWrapper,
    start_time: Union[pendulum.DateTime, datetime],
    end_time: Union[pendulum.DateTime, datetime],
    max_lookback: Optional[timedelta],
    entities: Optional[Union[pyspark_sql.DataFrame, pandas.DataFrame, TectonDataFrame]],
    from_source: Optional[bool],
    mock_data_sources: Dict[str, NodeRef],
) -> TectonDataFrame:
    if not feature_definition.is_realtime:
        check_spark_version(feature_definition.fv_spec.batch_cluster_config)

    if entities is not None:
        if not isinstance(entities, TectonDataFrame):
            entities = TectonDataFrame._create(entities)
        assert set(entities._dataframe.columns).issubset(
            set(feature_definition.join_keys)
        ), f"Entities should only contain columns that can be used as Join Keys: {feature_definition.join_keys}"

    start_time = pendulum.instance(start_time)
    if feature_definition.feature_start_timestamp is not None:
        start_time = max(start_time, feature_definition.feature_start_timestamp)
    query_time_range = pendulum.Period(start_time, pendulum.instance(end_time))

    if feature_definition.is_temporal or feature_definition.is_feature_table:
        lookback_time_range = time_utils.temporal_fv_get_feature_data_time_limits(
            feature_definition, query_time_range, max_lookback
        )
        qt = builder.build_temporal_time_range_validity_query(
            dialect=dialect,
            compute_mode=compute_mode,
            fd=feature_definition,
            from_source=from_source,
            query_time_range=query_time_range,
            lookback_time_range=lookback_time_range,
            entities=entities,
        )
    else:
        feature_data_time_limits = time_utils.get_feature_data_time_limits(
            fd=feature_definition,
            spine_time_limits=query_time_range,
        )
        qt = builder.build_aggregated_time_range_validity_query(
            dialect,
            compute_mode,
            feature_definition,
            feature_data_time_limits=feature_data_time_limits,
            query_time_range=query_time_range,
            from_source=from_source,
            entities=entities,
        )

    rewrite.MockDataRewrite(mock_data_sources).rewrite(qt)

    df = TectonDataFrame._create(qt)

    return df


def get_partial_aggregates(
    dialect: Dialect,
    compute_mode: ComputeMode,
    feature_definition: FeatureDefinitionWrapper,
    start_time: Union[pendulum.DateTime, datetime],
    end_time: Union[pendulum.DateTime, datetime],
    entities: Optional[TectonDataFrame],
    from_source: Optional[bool],
    mock_data_sources: Dict[str, NodeRef],
) -> TectonDataFrame:
    check_spark_version(feature_definition.fv_spec.batch_cluster_config)

    start_time = pendulum.instance(start_time)
    if feature_definition.feature_start_timestamp is not None:
        start_time = max(start_time, feature_definition.feature_start_timestamp)

    start_time = align_time_downwards(start_time, feature_definition.min_scheduling_interval)
    end_time = (
        align_time_downwards(end_time, feature_definition.min_scheduling_interval)
        + feature_definition.min_scheduling_interval
    )
    limits = pendulum.Period(start_time, end_time)

    qt = builder.build_get_partial_aggregates_query(
        dialect,
        compute_mode,
        feature_definition,
        limits=limits,
        from_source=from_source,
        entities=entities,
    )

    rewrite.MockDataRewrite(mock_data_sources).rewrite(qt)

    df = TectonDataFrame._create(qt)

    return df


def _key_to_int(s: Union[str, int]) -> int:
    if isinstance(s, int):
        return s
    # Convert a string to an integer by concatenating the ASCII values of the characters
    # TODO: This may break when the string is too long
    result = 0
    for i, char in enumerate(s):
        result += ord(char) << (8 * (len(s) - i - 1))
    return result


def _split_spine(spine: pandas.DataFrame, join_keys: List[str]) -> List[pandas.DataFrame]:
    """
    This is an experimental feature that splits the spine DataFrame into multiple DataFrames based on the spine split
    strategy specified in the configuration. The split strategy can be one of the following:
    - even: Splits the spine into equal-sized chunks
    - minimize_distance: Splits the spine at points where the distance between consecutive keys is maximized
    - agglomerative_clustering: Splits the spine using Agglomerative Clustering based on the bitwise distance between keys
    """
    split_count = int(conf.get_or_none("DUCKDB_SPINE_SPLIT_COUNT"))
    strategy = conf.get_or_none("DUCKDB_SPINE_SPLIT_STRATEGY")

    if strategy == "even":
        return _even_split(spine, join_keys, split_count)
    elif strategy == "minimize_distance":
        return _minimize_distance_split(spine, join_keys, split_count)
    elif strategy == "agglomerative_clustering":
        return _agglomerative_clustering_split(spine, join_keys, split_count)
    else:
        error = f"Unknown spine split strategy: {strategy}"
        raise ValueError(error)


def _even_split(spine: pandas.DataFrame, join_keys: List[str], split_count: int) -> List[pandas.DataFrame]:
    spine_sorted = spine.sort_values(by=join_keys).reset_index(drop=True)

    # Calculate the number of rows per split
    total_rows = len(spine_sorted)
    rows_per_split = total_rows // split_count
    extra_rows = total_rows % split_count

    # Calculate the split indices
    split_indices = []
    start_idx = 0
    for i in range(split_count):
        end_idx = start_idx + rows_per_split + (1 if i < extra_rows else 0)
        split_indices.append((start_idx, end_idx))
        start_idx = end_idx

    # Split the DataFrame into smaller DataFrames
    split_dfs = [spine_sorted.iloc[start:end].reset_index(drop=True) for start, end in split_indices]

    return split_dfs


def _minimize_distance_split(spine: pandas.DataFrame, join_keys: List[str], split_count: int) -> List[pandas.DataFrame]:
    # Check join_keys type, we only support str and int now
    if not all(
        pandas.api.types.is_integer_dtype(spine[join_key]) or pandas.api.types.is_string_dtype(spine[join_key])
        for join_key in join_keys
    ):
        error = "The join keys must be of type int or str for the minimize_distance spine split strategy."
        raise ValueError(error)

    # Sort the dataframe by the join_key
    spine_sorted = spine.sort_values(by=join_keys).reset_index(drop=True)

    # Compute distances between consecutive keys
    keys = spine_sorted[join_keys[0]].tolist()

    int_keys = [_key_to_int(key) for key in keys]
    distances = [abs(int_keys[i + 1] - int_keys[i]) for i in range(len(int_keys) - 1)]

    # Determine split points using heapq for efficiency with small split_count
    if split_count > 1 and distances:
        largest_indices = heapq.nlargest(split_count - 1, range(len(distances)), distances.__getitem__)
        split_points = sorted([index + 1 for index in largest_indices])
    else:
        split_points = []

    # Split the dataframe into chunks
    start_idx = 0
    split_dfs = []

    for idx in split_points:
        split_dfs.append(spine_sorted.iloc[start_idx:idx].reset_index(drop=True))
        start_idx = idx

    split_dfs.append(spine_sorted.iloc[start_idx:].reset_index(drop=True))  # Add the last chunk

    return split_dfs


def _agglomerative_clustering_split(
    spine: pandas.DataFrame, join_keys: List[str], split_count: int
) -> List[pandas.DataFrame]:
    # Check join_keys type, we only support str and int now
    if not all(
        pandas.api.types.is_integer_dtype(spine[join_key]) or pandas.api.types.is_string_dtype(spine[join_key])
        for join_key in join_keys
    ):
        error = "The join keys must be of type int or str for the agglomerative_clustering spine split strategy."
        raise ValueError(error)
    try:
        from sklearn.cluster import AgglomerativeClustering
    except ImportError:
        error = "Please install the scikit-learn package to use the agglomerative_clustering spine split strategy."
        raise ImportError(error)

    # Function to compute pairwise distances using the bitwise approach
    def bitwise_distance_matrix(keys: List[str]) -> numpy.ndarray:
        int_keys = numpy.array([_key_to_int(key) for key in keys])
        dist_matrix = numpy.abs(int_keys[:, None] - int_keys)
        return dist_matrix

    # Compute the distance matrix using the custom weighted distance function
    keys = spine[join_keys[0]].tolist()
    dist_matrix = bitwise_distance_matrix(keys)

    # Apply Agglomerative Clustering using the precomputed distance matrix
    clustering = AgglomerativeClustering(n_clusters=split_count, metric="precomputed", linkage="complete")
    spine["cluster"] = clustering.fit_predict(dist_matrix)

    # Split the DataFrame into multiple DataFrames based on the clusters
    grouped = spine.groupby("cluster")
    split_dfs = [group.drop(columns="cluster").reset_index(drop=True) for _, group in grouped]

    spine.drop(columns="cluster", inplace=True)

    return split_dfs


def get_features_for_events(
    dialect: Dialect,
    compute_mode: ComputeMode,
    feature_definition: FeatureDefinitionWrapper,
    spine: Optional[Union[pyspark_sql.DataFrame, pandas.DataFrame, TectonDataFrame, str]],
    timestamp_key: Optional[str],
    from_source: Optional[bool],
    mock_data_sources: Dict[str, NodeRef],
):
    if not feature_definition.is_realtime:
        check_spark_version(feature_definition.fv_spec.batch_cluster_config)

    _validate_sql_string_support(dialect, spine)

    if _should_infer_timestamp_of_spine(feature_definition, timestamp_key):
        timestamp_key = utils.infer_timestamp(spine)

    if conf.get_bool("DUCKDB_ENABLE_SPINE_SPLIT") and compute_mode == ComputeMode.RIFT:
        spine_split = _split_spine(spine, feature_definition.join_keys)
        dfs = []
        for spine_df in spine_split:
            tecton_spine_df = _create_tecton_df_spine(
                spine_schema=feature_definition.spine_schema, spine=spine_df, timestamp_key=timestamp_key
            )

            qt = _point_in_time_get_historical_features_for_feature_definition(
                dialect, compute_mode, feature_definition, tecton_spine_df, timestamp_key, from_source
            )

            rewrite.MockDataRewrite(mock_data_sources).rewrite(qt)

            df = TectonDataFrame._create(qt)
            dfs.append(df)

        return TectonDataFrame._create_from_dataframes(dfs)

    tecton_spine_df = _create_tecton_df_spine(
        spine_schema=feature_definition.spine_schema, spine=spine, timestamp_key=timestamp_key
    )

    qt = _point_in_time_get_historical_features_for_feature_definition(
        dialect, compute_mode, feature_definition, tecton_spine_df, timestamp_key, from_source
    )

    rewrite.MockDataRewrite(mock_data_sources).rewrite(qt)

    df = TectonDataFrame._create(qt)
    return df


def get_historical_features_for_feature_definition(
    dialect: Dialect,
    compute_mode: ComputeMode,
    feature_definition: FeatureDefinitionWrapper,
    spine: Optional[Union[pyspark_sql.DataFrame, pandas.DataFrame, TectonDataFrame, str]],
    timestamp_key: Optional[str],
    start_time: Optional[Union[pendulum.DateTime, datetime]],
    end_time: Optional[Union[pendulum.DateTime, datetime]],
    entities: Optional[Union[pyspark_sql.DataFrame, pandas.DataFrame, TectonDataFrame]],
    from_source: Optional[bool],
    mock_data_sources: Dict[str, NodeRef],
) -> TectonDataFrame:
    if not feature_definition.is_realtime:
        check_spark_version(feature_definition.fv_spec.batch_cluster_config)

    if spine is not None:
        logger.warning(errors.GET_HISTORICAL_FEATURES_DEPRECATED_SPINE)

        _validate_sql_string_support(dialect, spine)

        if _should_infer_timestamp_of_spine(feature_definition, timestamp_key):
            timestamp_key = utils.infer_timestamp(spine)

        tecton_spine_df = _create_tecton_df_spine(
            spine_schema=feature_definition.spine_schema, spine=spine, timestamp_key=timestamp_key
        )
        qt = _point_in_time_get_historical_features_for_feature_definition(
            dialect, compute_mode, feature_definition, tecton_spine_df, timestamp_key, from_source
        )
    else:
        logger.warning(errors.GET_HISTORICAL_FEATURES_DEPRECATED_TIME_RANGE)

        if entities is not None:
            if not isinstance(entities, TectonDataFrame):
                entities = TectonDataFrame._create(entities)
            assert set(entities._dataframe.columns).issubset(
                set(feature_definition.join_keys)
            ), f"Entities should only contain columns that can be used as Join Keys: {feature_definition.join_keys}"

        query_time_range = _get_feature_data_time_range(feature_definition, start_time, end_time)
        tecton_spine_df = None

        if feature_definition.is_temporal or feature_definition.is_feature_table:
            qt = builder.build_temporal_time_range_query(
                dialect=dialect,
                compute_mode=compute_mode,
                fd=feature_definition,
                from_source=from_source,
                query_time_range=query_time_range,
                entities=entities,
            )
        else:
            feature_data_time_limits = time_utils.get_feature_data_time_limits(
                fd=feature_definition,
                spine_time_limits=query_time_range,
            )
            qt = builder.build_aggregated_time_range_ghf_query(
                dialect,
                compute_mode,
                feature_definition,
                from_source=from_source,
                feature_data_time_limits=feature_data_time_limits,
                query_time_range=query_time_range,
                entities=entities,
            )

    rewrite.MockDataRewrite(mock_data_sources).rewrite(qt)

    df = TectonDataFrame._create(qt)
    return df


def _validate_sql_string_support(dialect: Dialect, spine):
    """
    Checks that the spine is a supported type for the given dialect.
    """
    if isinstance(spine, str) and dialect not in (
        tecton_core.query.dialect.Dialect.SNOWFLAKE,
        tecton_core.query.dialect.Dialect.DUCKDB,
    ):
        msg = "Using SQL str as `spine` is only supported with Snowflake."
        raise TypeError(msg)


def _should_infer_timestamp_of_spine(
    feature_definition: FeatureDefinitionWrapper,
    timestamp_key: Optional[str],
) -> bool:
    if feature_definition.is_realtime:
        # We need to infer the spine timestamp for a RTFV if the user doesn't pass an explicit timestamp key and
        # 1. It has a dependent materialized feature view or
        # 2. It uses a realtime context
        return timestamp_key is None and (
            utils.get_num_dependent_fv(feature_definition.pipeline.root, visited_inputs={}) > 0
            or feature_definition.uses_realtime_context
        )
    else:
        return timestamp_key is None


def _point_in_time_get_historical_features_for_feature_definition(
    dialect: Dialect,
    compute_mode: ComputeMode,
    feature_definition: FeatureDefinitionWrapper,
    spine: TectonDataFrame,
    timestamp_key: Optional[str],
    from_source: Optional[bool],
) -> node_interface.NodeRef:
    if feature_definition.is_realtime:
        utils.validate_spine_dataframe(spine, timestamp_key, feature_definition.request_context_keys)
    else:
        utils.validate_spine_dataframe(spine, timestamp_key)

    dac = FeatureDefinitionAndJoinConfig.from_feature_definition(feature_definition)
    user_data_node_metadata = {}
    user_data_node = nodes.UserSpecifiedDataNode(dialect, compute_mode, spine, user_data_node_metadata)

    if timestamp_key:
        user_data_node_metadata["timestamp_key"] = timestamp_key
        user_data_node = nodes.ConvertTimestampToUTCNode(dialect, compute_mode, user_data_node.as_ref(), timestamp_key)

    qt = builder.build_spine_join_querytree(
        dialect,
        compute_mode,
        dac,
        user_data_node.as_ref(),
        timestamp_key,
        from_source,
        use_namespace_feature_prefix=dialect != tecton_core.query.dialect.Dialect.SNOWFLAKE,
    )

    return qt


def _most_recent_tile_end_time(fd: FeatureDefinitionWrapper, timestamp: datetime) -> int:
    """Computes the most recent tile end time which is ready to be computed.

    :param timestamp: The timestamp in python datetime format
    :return: The timestamp in seconds of the greatest ready tile end time <= timestamp.
    """
    # Account for data delay
    timestamp = timestamp - fd.max_source_data_delay
    if fd.min_scheduling_interval:
        timestamp = align_time_downwards(timestamp, fd.min_scheduling_interval)
    return convert_timestamp_to_epoch(timestamp, fd.get_feature_store_format_version)


def _get_feature_data_time_range(
    fd: FeatureDefinitionWrapper,
    start_time: Optional[Union[pendulum.DateTime, datetime]],
    end_time: Optional[Union[pendulum.DateTime, datetime]],
) -> pendulum.Period:
    if start_time is not None and isinstance(start_time, datetime):
        start_time = pendulum.instance(start_time)

    if end_time is not None and isinstance(end_time, datetime):
        end_time = pendulum.instance(end_time)

    if start_time is not None and fd.feature_start_timestamp is not None and start_time < fd.feature_start_timestamp:
        logger.warning(
            f'The provided start_time ({start_time}) is before "{fd.name}"\'s feature_start_time ({fd.feature_start_timestamp}). No feature values will be returned before the feature_start_time.'
        )
        start_time = fd.feature_start_timestamp

    # TODO(brian): construct the timestamps a bit more directly. This code in
    # general reuses utilities not really meant for the semantics of this API.
    if fd.is_temporal_aggregate or fd.is_temporal:
        # Feature views where materialization is not enabled may not have a feature_start_time.
        _start = start_time or fd.feature_start_timestamp or pendulum.datetime(1970, 1, 1)
        # we need to add 1 to most_recent_anchor since we filter end_time exclusively
        if end_time:
            _end = end_time
        else:
            anchor_time = _most_recent_tile_end_time(fd, pendulum.now("UTC") - fd.min_scheduling_interval)
            _end = convert_epoch_to_datetime(anchor_time, fd.get_feature_store_format_version) + pendulum.duration(
                microseconds=1
            )
    else:
        _start = start_time or pendulum.datetime(1970, 1, 1)
        _end = end_time or pendulum.now("UTC")

    if _start >= _end:
        # TODO(felix): Move this and other instances of validating user inputs to top-level get_historical_features() methods.
        raise core_errors.START_TIME_NOT_BEFORE_END_TIME(_start, _end)

    return pendulum.Period(_start, _end)


def get_fields_list_from_tecton_schema(tecton_schema: schema_pb2.Schema) -> List[sdk_types.Field]:
    """Convert TectonSchema into a list of Tecton Fields."""
    columns_and_types = schema.Schema(tecton_schema).column_name_and_data_types()
    request_schema = []
    for c_and_t in columns_and_types:
        name = c_and_t[0]
        data_type = type_utils.sdk_type_from_tecton_type(c_and_t[1])
        request_schema.append(sdk_types.Field(name, data_type))
    return request_schema


def _create_tecton_df_spine(
    spine_schema: Schema,
    spine: Optional[Union[pyspark_sql.DataFrame, pandas.DataFrame, TectonDataFrame, str]],
    timestamp_key: Optional[str],
) -> TectonDataFrame:
    if isinstance(spine, pandas.DataFrame):
        if timestamp_key is not None:
            spine_schema += schema.Schema.from_dict({timestamp_key: data_types.TimestampType()})
        spine = TectonDataFrame._create_from_pandas_with_schema(spine, schema=spine_schema)
    elif isinstance(spine, str):
        spine = TectonDataFrame._create_with_snowflake_sql(spine)
    elif not isinstance(spine, TectonDataFrame):
        spine = TectonDataFrame._create(spine)

    return spine


def get_dataframe_for_data_source(
    dialect: Dialect,
    compute_mode: ComputeMode,
    data_source: specs.DataSourceSpec,
    start_time: Optional[datetime],
    end_time: Optional[datetime],
    apply_translator: bool,
) -> TectonDataFrame:
    if isinstance(data_source.batch_source, (specs.SparkBatchSourceSpec, specs.PandasBatchSourceSpec)):
        if not data_source.batch_source.supports_time_filtering and (start_time or end_time):
            raise errors.DS_INCORRECT_SUPPORTS_TIME_FILTERING

        node = builder.build_datasource_scan_node(
            dialect=dialect,
            compute_mode=compute_mode,
            ds=data_source,
            for_stream=False,
            start_time=start_time,
            end_time=end_time,
        )
        return TectonDataFrame._create(node)
    elif apply_translator:
        timestamp_key = data_source.batch_source.timestamp_field
        if not timestamp_key and (start_time or end_time):
            raise errors.DS_DATAFRAME_NO_TIMESTAMP

        node = builder.build_datasource_scan_node(
            dialect=dialect,
            compute_mode=compute_mode,
            ds=data_source,
            for_stream=False,
            start_time=start_time,
            end_time=end_time,
        )
        return TectonDataFrame._create(node)
    else:
        if start_time is not None or end_time is not None:
            raise errors.DS_RAW_DATAFRAME_NO_TIMESTAMP_FILTER

        node = nodes.RawDataSourceScanNode(dialect, compute_mode, data_source).as_ref()
        return TectonDataFrame._create(node)


def run_transformation_batch(
    dialect: Dialect,
    compute_mode: ComputeMode,
    fd: FeatureDefinitionWrapper,
    feature_start_time: datetime,
    feature_end_time: datetime,
    mock_data_sources: Dict[str, NodeRef],
) -> TectonDataFrame:
    if not fd.is_realtime:
        check_spark_version(fd.fv_spec.batch_cluster_config)

    feature_time_limits_aligned = pendulum.period(feature_start_time, feature_end_time)

    if fd.is_temporal:
        qt = build_materialization_querytree(
            dialect,
            compute_mode,
            fd,
            for_stream=False,
            feature_data_time_limits=feature_time_limits_aligned,
            use_timestamp_key=True,
        )
    elif fd.is_temporal_aggregate:
        qt = build_pipeline_querytree(
            dialect, compute_mode, fd, for_stream=False, feature_data_time_limits=feature_time_limits_aligned
        )
    else:
        msg = "Unsupported FV Type"
        raise Exception(msg)

    MockDataRewrite(mock_data_sources).rewrite(qt)

    return TectonDataFrame._create(qt)
