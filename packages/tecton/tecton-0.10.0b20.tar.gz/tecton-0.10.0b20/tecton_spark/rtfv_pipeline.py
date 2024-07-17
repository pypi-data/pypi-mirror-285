import re
from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import numpy
import pandas
from pyspark.sql.types import ArrayType
from pyspark.sql.types import MapType
from pyspark.sql.types import StructType
from pyspark.sql.types import TimestampType

from tecton_core import conf
from tecton_core import specs
from tecton_core.compute_mode import ComputeMode
from tecton_core.errors import UDF_ERROR
from tecton_core.errors import UDF_TYPE_ERROR
from tecton_core.id_helper import IdHelper
from tecton_core.pipeline_common import constant_node_to_value
from tecton_core.query_consts import udf_internal
from tecton_core.realtime_context import RealtimeContext
from tecton_proto.args.pipeline__client_pb2 import Pipeline
from tecton_proto.args.pipeline__client_pb2 import PipelineNode
from tecton_proto.args.pipeline__client_pb2 import TransformationNode
from tecton_proto.args.transformation__client_pb2 import TransformationMode
from tecton_spark import feature_view_spark_utils
from tecton_spark.spark_pipeline import SparkFeaturePipeline
from tecton_spark.type_annotations import PySparkDataFrame


# TODO(TEC-8978): remove \. from namespace regex when FWv3 FVs are no longer supported.
_NAMESPACE_SEPARATOR_REGEX = re.compile(r"__|\.")


def feature_name(namespaced_feature_name: str) -> str:
    """Gets the base feature name from a namespaced_feature_name (e.g. feature_view__feature)

    Supports both `__` (fwv5) and `.` (fwv3) separators. Does two attempts at
    getting the feature name since `__` was allowed in feature view names in
    fwv3.
    """

    spl = _NAMESPACE_SEPARATOR_REGEX.split(namespaced_feature_name)
    if len(spl) == 2:
        return spl[1]

    return namespaced_feature_name.split(".")[1]


# For Pandas-mode:
# A pandas udf takes as inputs List[pandas.Series] and outputs List[pandas.Series]
# However, the user-defined transforms take as input pandas.DataFrame and output
# pandas.DataFrame. RealtimeFeaturePipeline will construct a UDF Wrapper functions
# that translates the inputs and outputs and performs some type checking.
#
# The general idea is that each Node of the pipeline evaluates to a pandas.DataFrame.
# This is what we want since the user-defined transforms take pandas.DataFrame
# as inputs both from RequestDataSourceNode or FeatureViewNode.
# pandas_udf_wrapper then typechecks and translates the final pandas.DataFrame into a
# jsonized pandas.Series to match what spark expects.
#
# For Python-mode, we can use a simpler wrapper function for the udf because we don't do
# any spark<->pandas type conversions.
class RealtimeFeaturePipeline(SparkFeaturePipeline):
    _VALID_MODES = ["pipeline", "python", "pandas"]

    def __init__(
        self,
        name: str,
        pipeline: Pipeline,
        transformations: List[specs.TransformationSpec],
        # maps input + feature name to arg index that udf function wrapper will be called with.
        # this is needed because we need to know which pandas.Series that are inputs to this
        # function correspond to the desired request context fields or dependent fv features
        # that the customer-defined udf uses.
        udf_arg_idx_map: Dict[str, int],
        output_schema: Optional[StructType],
        events_df_timestamp_field: Optional[str] = None,
        # the id of this OnDemandFeatureView; only required to be set when reading from source data
        fv_id: Optional[str] = None,
        data_source_inputs: Optional[Dict[str, Union[Dict[str, Any], pandas.DataFrame, RealtimeContext]]] = None,
    ) -> None:
        self._pipeline = pipeline
        self._name = name
        self._fv_id = fv_id
        self.udf_arg_idx_map = udf_arg_idx_map
        self._id_to_transformation = {t.id: t for t in transformations}
        self._output_schema = output_schema
        self._data_source_inputs = data_source_inputs
        self._events_df_timestamp_field = events_df_timestamp_field
        # In Spark, the UDF cannot reference a proto enum, so instead save mode as a string
        self.mode = (
            "python"
            if self._id_to_transformation[
                IdHelper.to_string(self._pipeline.root.transformation_node.transformation_id)
            ].transformation_mode
            == TransformationMode.TRANSFORMATION_MODE_PYTHON
            else "pandas"
        )
        # Access this conf value outside of the UDF to avoid doing it many times and avoiding any worker/driver state issues.
        self._should_check_output_schema = conf.get_bool("TECTON_PYTHON_ODFV_OUTPUT_SCHEMA_CHECK_ENABLED")

    def is_pandas_mode(self):
        return self.mode == "pandas"

    def is_python_mode(self):
        return self.mode == "python"

    def get_dataframe(self) -> PySparkDataFrame:
        df = self._node_to_value(self._pipeline.root)
        return df

    def py_wrapper(self, *args):
        assert self.is_python_mode()
        self._udf_args: List = args
        res = self._node_to_value(self._pipeline.root)
        if self._should_check_output_schema:
            feature_view_spark_utils.check_python_odfv_output_schema(res, self._output_schema, self._name)
        return res

    def pandas_udf_wrapper(self, *args):
        assert self.is_pandas_mode()

        import json

        import pandas

        # self.udf_arg_idx_map tells us which of these pandas.Series correspond to a given
        # RequestDataSource or FeatureView input
        self._udf_args: List[pandas.Series] = args

        output_df = self._node_to_value(self._pipeline.root)

        assert isinstance(
            output_df, pandas.DataFrame
        ), f"Transformer returns {str(output_df)}, but must return a pandas.DataFrame instead."

        for field in self._output_schema:
            assert field.name in output_df.columns, (
                f"Expected output schema field '{field.name}' not found in columns of DataFrame returned by "
                f"'{self._name}': [" + ", ".join(output_df.columns) + "]"
            )
            if isinstance(field.dataType, (ArrayType, MapType, StructType, TimestampType)):
                output_df[field.name] = output_df[field.name].apply(
                    RealtimeFeaturePipeline._convert_object_to_serializable_format
                )

        output_strs = []

        # itertuples() is used instead of iterrows() to preserve type safety.
        # See notes in https://pandas.pydata.org/pandas-docs/version/0.17.1/generated/pandas.DataFrame.iterrows.html.
        for row in output_df.itertuples(index=False):
            output_strs.append(json.dumps(row._asdict()))
        return pandas.Series(output_strs)

    @staticmethod
    def _convert_object_to_serializable_format(item):
        if isinstance(item, numpy.ndarray):
            return [RealtimeFeaturePipeline._convert_object_to_serializable_format(value) for value in item.tolist()]
        elif isinstance(item, dict):
            return {
                key: RealtimeFeaturePipeline._convert_object_to_serializable_format(value)
                for key, value in item.items()
            }
        elif isinstance(item, list):
            return [RealtimeFeaturePipeline._convert_object_to_serializable_format(value) for value in item]
        elif isinstance(item, TimestampType):
            return item.fromInternal()
        elif isinstance(item, datetime):
            return item.isoformat()
        else:
            return item

    def _node_to_value(
        self, pipeline_node: PipelineNode
    ) -> Union[
        str, int, float, bool, datetime, None, Dict[str, Any], pandas.DataFrame, PySparkDataFrame, pandas.Series
    ]:
        if pipeline_node.HasField("constant_node"):
            return constant_node_to_value(pipeline_node.constant_node)
        elif pipeline_node.HasField("feature_view_node"):
            if self._data_source_inputs is not None:
                return self._data_source_inputs[pipeline_node.feature_view_node.input_name]
            elif self.is_python_mode():
                fields_dict = {}
                # The input name of this FeatureViewNode tells us which of the udf_args
                # correspond to the Dict we should generate that the parent TransformationNode
                # expects as an input. It also expects the DataFrame to have its columns named
                # by the feature names.
                for feature in self.udf_arg_idx_map:
                    if not feature.startswith(
                        f"{udf_internal(ComputeMode.SPARK)}_{pipeline_node.feature_view_node.input_name}_{self._fv_id}"
                    ):
                        continue
                    idx = self.udf_arg_idx_map[feature]
                    value = self._udf_args[idx]
                    if isinstance(value, datetime):
                        value = value.replace(tzinfo=timezone.utc)
                    fields_dict[feature_name(feature)] = value
                return fields_dict
            elif self.is_pandas_mode():
                all_series = []
                features = []
                # The input name of this FeatureViewNode tells us which of the udf_args
                # correspond to the pandas.DataFrame we should generate that the parent TransformationNode
                # expects as an input. It also expects the DataFrame to have its columns named
                # by the feature names.
                for feature in self.udf_arg_idx_map:
                    if not feature.startswith(
                        f"{udf_internal(ComputeMode.SPARK)}_{pipeline_node.feature_view_node.input_name}_{self._fv_id}"
                    ):
                        continue
                    idx = self.udf_arg_idx_map[feature]
                    all_series.append(self._udf_args[idx])
                    features.append(feature_name(feature))
                df = pandas.concat(all_series, keys=features, axis=1)
                return df
            else:
                msg = "Transform mode {self.mode} is not yet implemented"
                raise NotImplementedError(msg)
        elif pipeline_node.HasField("request_data_source_node"):
            if self._data_source_inputs is not None:
                return self._data_source_inputs[pipeline_node.request_data_source_node.input_name]
            elif self.is_python_mode():
                request_context = pipeline_node.request_data_source_node.request_context
                field_names = [c.name for c in request_context.tecton_schema.columns]
                fields_dict = {}
                for input_col in field_names:
                    idx = self.udf_arg_idx_map[input_col]
                    value = self._udf_args[idx]
                    if isinstance(value, datetime):
                        value = value.replace(tzinfo=timezone.utc)
                    fields_dict[input_col] = value
                return fields_dict
            elif self.is_pandas_mode():
                all_series = []
                request_context = pipeline_node.request_data_source_node.request_context
                field_names = [c.name for c in request_context.tecton_schema.columns]
                for input_col in field_names:
                    idx = self.udf_arg_idx_map[input_col]
                    all_series.append(self._udf_args[idx])
                df = pandas.concat(all_series, keys=field_names, axis=1)
                return df
            else:
                msg = "Transform mode {self.mode} is not yet implemented"
                raise NotImplementedError(msg)
        elif pipeline_node.HasField("transformation_node"):
            return self._transformation_node_to_value(pipeline_node.transformation_node)
        elif pipeline_node.HasField("context_node"):
            # Used for `run_transformation` with a mock Context
            if self._data_source_inputs is not None:
                return self._data_source_inputs[pipeline_node.context_node.input_name]

            if self._events_df_timestamp_field not in self.udf_arg_idx_map:
                msg = f"Could not extract field '{self._events_df_timestamp_field}' from events data frame."
                raise Exception(msg)

            timestamp_index = self.udf_arg_idx_map[self._events_df_timestamp_field]
            request_timestamp = self._udf_args[timestamp_index]

            if self.is_python_mode():
                request_timestamp = request_timestamp.replace(tzinfo=timezone.utc)
                realtime_context = RealtimeContext(request_timestamp)
            elif self.is_pandas_mode():
                realtime_context = request_timestamp.to_frame(name="request_timestamp")
            return realtime_context
        elif pipeline_node.HasField("materialization_context_node"):
            msg = "MaterializationContext is unsupported for pandas pipelines"
            raise ValueError(msg)
        else:
            msg = "This is not yet implemented"
            raise NotImplementedError(msg)

    def _transformation_node_to_value(
        self, transformation_node: TransformationNode
    ) -> Union[Dict[str, Any], pandas.DataFrame, PySparkDataFrame]:
        """Recursively translates inputs to values and then passes them to the transformation."""
        args: List[Union[PySparkDataFrame, str, int, float, bool]] = []
        kwargs = {}
        for transformation_input in transformation_node.inputs:
            input_node = transformation_input.node
            node_value = self._node_to_value(input_node)
            if transformation_input.HasField("arg_index"):
                assert len(args) == transformation_input.arg_index
                args.append(node_value)
            elif transformation_input.HasField("arg_name"):
                kwargs[transformation_input.arg_name] = node_value
            else:
                msg = f"Unknown argument type for Input node: {transformation_input}"
                raise KeyError(msg)

        return self._apply_transformation_function(transformation_node, args, kwargs)

    def _apply_transformation_function(
        self, transformation_node: TransformationNode, args: List[Any], kwargs: Dict[str, Any]
    ) -> Union[Dict[str, Any], pandas.DataFrame, PySparkDataFrame]:
        """For the given transformation node, returns the corresponding DataFrame transformation.

        If needed, resulted function is wrapped with a function that translates mode-specific input/output types to DataFrames.
        """
        transformation = self.get_transformation_by_id(transformation_node.transformation_id)
        mode = transformation.transformation_mode
        user_function = transformation.user_function

        if (
            mode != TransformationMode.TRANSFORMATION_MODE_PANDAS
            and mode != TransformationMode.TRANSFORMATION_MODE_PYTHON
        ):
            msg = f"Unsupported transformation mode({transformation.transformation_mode}) for Realtime Feature Views."
            raise KeyError(msg)

        try:
            return user_function(*args, **kwargs)
        except TypeError as e:
            raise UDF_TYPE_ERROR(e)
        except Exception as e:
            raise UDF_ERROR(e, feature_definition_name=transformation.metadata.name)
