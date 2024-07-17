import time
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from functools import partial
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pandas

from tecton._internals import ingest_utils
from tecton._internals import metadata_service
from tecton._internals import utils
from tecton._internals.display import Displayable
from tecton_core import specs
from tecton_core.compute_mode import BatchComputeMode
from tecton_proto.args.feature_view__client_pb2 import ClusterConfig
from tecton_proto.common import id__client_pb2 as id_pb2
from tecton_proto.data.materialization_status__client_pb2 import MaterializationStatus
from tecton_proto.materialization.spark_cluster__client_pb2 import TaskType
from tecton_proto.materializationjobservice.materialization_job_service__client_pb2 import CancelDatasetJobRequest
from tecton_proto.materializationjobservice.materialization_job_service__client_pb2 import CancelJobRequest
from tecton_proto.materializationjobservice.materialization_job_service__client_pb2 import DatasetJob
from tecton_proto.materializationjobservice.materialization_job_service__client_pb2 import GetDataframeInfoRequest
from tecton_proto.materializationjobservice.materialization_job_service__client_pb2 import GetDatasetJobRequest
from tecton_proto.materializationjobservice.materialization_job_service__client_pb2 import GetJobRequest
from tecton_proto.materializationjobservice.materialization_job_service__client_pb2 import GetLatestReadyTimeRequest
from tecton_proto.materializationjobservice.materialization_job_service__client_pb2 import GetLatestReadyTimeResponse
from tecton_proto.materializationjobservice.materialization_job_service__client_pb2 import JobAttempt
from tecton_proto.materializationjobservice.materialization_job_service__client_pb2 import ListJobsRequest
from tecton_proto.materializationjobservice.materialization_job_service__client_pb2 import MaterializationJob
from tecton_proto.materializationjobservice.materialization_job_service__client_pb2 import MaterializationJobRequest
from tecton_proto.materializationjobservice.materialization_job_service__client_pb2 import StartDatasetJobRequest
from tecton_proto.metadataservice.metadata_service__client_pb2 import GetMaterializationStatusRequest


class JobTimeoutException(Exception):
    pass


class JobFailedException(Exception):
    pass


WAIT_INTERVAL = timedelta(seconds=60)


@dataclass
class MaterializationAttemptData:
    """
    Data representation of the materialization job attempt.

    Materialization job may have multiple attempts to materialize features.

    :param id: ID string of the materialization attempt.
    :param run_url: URL to track materialization attempt.
    :param state: State of the materialization attempt.
    :param created_at: Materialization attempt creation timestamp.
    :param updated_at: Materialization attempt update timestamp.
    """

    id: str
    run_url: str
    state: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_proto(cls, proto: JobAttempt):
        created_at = datetime.utcfromtimestamp(proto.created_at.seconds)
        updated_at = datetime.utcfromtimestamp(proto.updated_at.seconds)
        return cls(id=proto.id, run_url=proto.run_url, state=proto.state, created_at=created_at, updated_at=updated_at)


@dataclass
class MaterializationJobData:
    """
    Data representation of the materialization job

    :param id: ID string of the materialization job.
    :param workspace: Name of the project workspace.
    :param feature_view: Name of the Feature View.
    :param state: State of the materialization job.
    :param online: Whether the job materializes features to the online store.
    :param offline: Whether the job materializes features to the offline store.
    :param start_time: Start timestamp of the batch materialization window.
    :param end_time: End timestamp of the batch materialization window.
    :param created_at: Job creation timestamp.
    :param updated_at: Job update timestamp.
    :param attempts: Materialization attempts. List of :class:`MaterializationAttemptData`
    :param next_attempt_at: If job needs another attempt, Start timestamp the next materialization attempt.
    :param job_type: Type of materialization. One of 'BATCH' or 'STREAM'.
    """

    id: str
    workspace: str
    feature_view: str
    state: str
    online: bool
    offline: bool
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    attempts: List[MaterializationAttemptData]
    next_attempt_at: Optional[datetime]
    job_type: str

    @classmethod
    def from_proto(cls, proto: MaterializationJob):
        start_time = datetime.utcfromtimestamp(proto.start_time.seconds) if proto.HasField("start_time") else None
        end_time = datetime.utcfromtimestamp(proto.end_time.seconds) if proto.HasField("end_time") else None
        created_at = datetime.utcfromtimestamp(proto.created_at.seconds)
        updated_at = datetime.utcfromtimestamp(proto.updated_at.seconds)
        attempts = [MaterializationAttemptData.from_proto(attempt_proto) for attempt_proto in proto.attempts]
        next_attempt_at = (
            datetime.utcfromtimestamp(proto.next_attempt_at.seconds) if proto.HasField("next_attempt_at") else None
        )
        return cls(
            id=proto.id,
            workspace=proto.workspace,
            feature_view=proto.feature_view,
            state=proto.state,
            online=proto.online,
            offline=proto.offline,
            start_time=start_time,
            end_time=end_time,
            created_at=created_at,
            updated_at=updated_at,
            attempts=attempts,
            next_attempt_at=next_attempt_at,
            job_type=proto.job_type,
        )


def trigger_materialization_job(
    feature_view: str,
    workspace: str,
    start_time: datetime,
    end_time: datetime,
    online: bool,
    offline: bool,
    use_tecton_managed_retries: bool = True,
    overwrite: bool = False,
) -> str:
    """
    Starts a batch materialization job for this Feature View.

    :param start_time: The job will materialize feature values between the start_time and end_time.
    :param end_time: The job will materialize feature values between the start_time and end_time.
    :param online: Whether the job will materialize features to the online store.
        The Feature View must be configured with online=True in order to materialize features online.
    :param offline: Whether the job will materialize features to the offline store.
        The Feature View must be configured with offline=True in order to materialize features offline.
    :param use_tecton_managed_retries: If enabled, Tecton will automatically retry failed attempts.
        Disable to manage your own retry behavior.
    :param overwrite: If enabled, you will be able to run materialization jobs for periods that previously have materialized data.
        This operation can be sensitive for feature views with existing materialized online data.
        For the offline store, all previously materialized data between the start time and end time will be dropped.
        For the online store, all previous data will remain, but may be overwritten by this job.
    :return: ID string of the created materialization job.
    :raises TectonValidationError: If job params are not valid.
    """
    request = MaterializationJobRequest()
    request.feature_view = feature_view
    request.workspace = workspace
    request.start_time.FromDatetime(start_time)
    request.end_time.FromDatetime(end_time)
    request.online = online
    request.offline = offline
    request.use_tecton_managed_retries = use_tecton_managed_retries
    request.overwrite = overwrite

    mds_instance = metadata_service.instance()
    response = mds_instance.SubmitMaterializationJob(request)
    return response.job.id


def list_materialization_jobs(feature_view: str, workspace: str) -> List[MaterializationJobData]:
    """
    Retrieves the list of all materialization jobs for this Feature View.

    :return: List of :class:`MaterializationJobData` objects.
    """
    request = ListJobsRequest()
    request.feature_view = feature_view
    request.workspace = workspace

    mds_instance = metadata_service.instance()
    response = mds_instance.ListMaterializationJobs(request)
    return [MaterializationJobData.from_proto(job) for job in response.jobs]


def get_materialization_job(feature_view: str, workspace: str, job_id: str) -> MaterializationJobData:
    """
    Retrieves data about the specified materialization job for this Feature View.

    This data includes information about job attempts.

    :param job_id: ID string of the materialization job.
    :return: :class:`MaterializationJobData` object for the job.
    """
    request = GetJobRequest()
    request.feature_view = feature_view
    request.workspace = workspace
    request.job_id = job_id

    mds_instance = metadata_service.instance()
    response = mds_instance.GetMaterializationJob(request)
    return MaterializationJobData.from_proto(response.job)


def get_latest_ready_time(feature_view: str, workspace: str) -> GetLatestReadyTimeResponse:
    request = GetLatestReadyTimeRequest()
    request.feature_view = feature_view
    request.workspace = workspace

    mds_instance = metadata_service.instance()
    return mds_instance.GetLatestReadyTime(request)


def cancel_materialization_job(feature_view: str, workspace: str, job_id: str) -> MaterializationJobData:
    """
    Cancels the scheduled or running batch materialization job for this Feature View specified by the job identifier.
    Once cancelled, a job will not be retried further.

    Job run state will be set to MANUAL_CANCELLATION_REQUESTED.
    Note that cancellation is asynchronous, so it may take some time for the cancellation to complete.
    If job run is already in MANUAL_CANCELLATION_REQUESTED or in a terminal state then it'll return the job.

    :param job_id: ID string of the materialization job.
    :return: :class:`MaterializationJobData` object for the cancelled job.
    """
    request = CancelJobRequest()
    request.feature_view = feature_view
    request.workspace = workspace
    request.job_id = job_id

    mds_instance = metadata_service.instance()
    response = mds_instance.CancelMaterializationJob(request)
    return MaterializationJobData.from_proto(response.job)


def wait_for_materialization_job(
    feature_view: str,
    workspace: str,
    job_id: str,
    timeout: Optional[timedelta] = None,
) -> MaterializationJobData:
    """
    Blocks until the specified job has been completed.

    :param job_id: ID string of the materialization job.
    :param timeout: (Optional) timeout for this function.
        An exception is raised if the job does not complete within the specified time.
    :return: :class:`MaterializationJobData` object for the successful job.
    :raises JobTimeoutException:
        If timeout param is specified and job does not complete within the specified time.
    :raises MaterializationJobFailedException: If materialization job did not reach a successful state.
    """
    return _wait_for_job(
        partial(get_materialization_job, feature_view, workspace),
        job_id,
        timeout,
    )


def _wait_for_job(
    job_retriever: Callable[[str], Union[MaterializationJobData, "DatasetJobData"]],
    job_id: str,
    timeout: timedelta,
) -> Union[MaterializationJobData, "DatasetJobData"]:
    wait_start_time = datetime.now()
    while True:
        job_data = job_retriever(job_id)
        run_state = job_data.state

        if run_state == "SUCCESS":
            return job_data
        elif timeout and ((datetime.now() - wait_start_time) > timeout):
            msg = f"job {job_id} timed out, last job state {run_state}"
            raise JobTimeoutException(msg)
        elif run_state == "RUNNING":
            time.sleep(WAIT_INTERVAL.total_seconds())
        else:
            msg = f"job {job_id} failed, last job state {run_state}"
            raise JobFailedException(msg)


def get_materialization_status_response(id_proto: id_pb2.Id, workspace: str) -> MaterializationStatus:
    """Returns MaterializationStatus proto for the FeatureView."""
    request = GetMaterializationStatusRequest()
    request.feature_package_id.CopyFrom(id_proto)
    request.workspace = workspace

    response = metadata_service.instance().GetMaterializationStatus(request)
    return response.materialization_status


@dataclass
class DatasetJobData:
    id: str
    workspace: str
    dataset: str
    state: str
    created_at: datetime
    updated_at: datetime
    attempts: List[MaterializationAttemptData]

    @classmethod
    def from_proto(cls, proto: DatasetJob):
        created_at = datetime.utcfromtimestamp(proto.created_at.seconds)
        updated_at = datetime.utcfromtimestamp(proto.updated_at.seconds)
        attempts = [MaterializationAttemptData.from_proto(attempt_proto) for attempt_proto in proto.attempts]
        return cls(
            id=proto.id,
            workspace=proto.workspace,
            dataset=proto.saved_feature_data_frame,
            state=proto.state,
            created_at=created_at,
            updated_at=updated_at,
            attempts=attempts,
        )


@dataclass
class SpineInput:
    path: str
    timestamp_key: str
    column_names: str


@dataclass
class DateTimeRangeInput:
    start_time: datetime
    end_time: datetime
    max_loopback: Optional[timedelta] = None
    entities_path: Optional[str] = None


def start_dataset_job(
    fco: Union[specs.FeatureServiceSpec, specs.FeatureViewSpec],
    input_: Union[SpineInput, DateTimeRangeInput],
    dataset: str,
    compute_mode: BatchComputeMode,
    from_source: Optional[bool] = None,
    cluster_config: Optional[ClusterConfig] = None,
    tecton_materialization_runtime: Optional[str] = None,
    environment: Optional[str] = None,
    extra_config: Optional[Dict[str, Any]] = None,
) -> DatasetJobData:
    request = StartDatasetJobRequest()
    request.workspace = fco.workspace
    request.compute_mode = compute_mode.value
    request.dataset_name = dataset
    if from_source is not None:
        request.from_source = from_source

    if isinstance(fco, specs.FeatureViewSpec):
        request.feature_view_id.CopyFrom(fco.id_proto)
    elif isinstance(fco, specs.FeatureServiceSpec):
        request.feature_service_id.CopyFrom(fco.id_proto)
    else:
        msg = f"unexpected fco type {type(fco)} for start_dataset_job"
        raise RuntimeError(msg)

    if isinstance(input_, SpineInput):
        request.spine.path = input_.path

        request.spine.timestamp_key = input_.timestamp_key
        request.spine.column_names.extend(input_.column_names)
    elif isinstance(input_, DateTimeRangeInput):
        request.datetime_range.start.FromDatetime(input_.start_time)
        request.datetime_range.end.FromDatetime(input_.end_time)
        if input_.max_loopback:
            request.datetime_range.max_loopback.FromTimedelta(input_.max_loopback)
        if input_.entities_path:
            request.datetime_range.entities_path = input_.entities_path
    else:
        msg = f"unexpected input type {type(input_)} for start_dataset_jon"
        raise RuntimeError(msg)

    if cluster_config:
        request.cluster_config.CopyFrom(cluster_config)

    if tecton_materialization_runtime:
        request.tecton_materialization_runtime = tecton_materialization_runtime

    if environment:
        request.environment = environment

    if extra_config:
        request.extra_config.update(extra_config)

    response = metadata_service.instance().StartDatasetJob(request)
    return DatasetJobData.from_proto(response.job)


def get_dataset_job(dataset: str, workspace: str, job_id: str):
    request = GetDatasetJobRequest()
    request.workspace = workspace
    request.saved_feature_data_frame = dataset
    request.job_id = job_id

    response = metadata_service.instance().GetDatasetJob(request)
    return DatasetJobData.from_proto(response.job)


def wait_for_dataset_job(dataset: str, workspace: str, job_id: str, timeout: Optional[timedelta] = None):
    return _wait_for_job(
        partial(get_dataset_job, dataset, workspace),
        job_id,
        timeout,
    )


def cancel_dataset_job(dataset: str, workspace: str, job_id: str) -> DatasetJobData:
    request = CancelDatasetJobRequest()
    request.workspace = workspace
    request.saved_feature_data_frame = dataset
    request.job_id = job_id

    response = metadata_service.instance().CancelDatasetJob(request)
    return DatasetJobData.from_proto(response.job)


def upload_dataframe_for_dataset_job(
    df: "pandas.DataFrame", fco: Union[specs.FeatureServiceSpec, specs.FeatureViewSpec]
) -> str:
    request = GetDataframeInfoRequest()
    request.workspace = fco.workspace
    if isinstance(fco, specs.FeatureViewSpec):
        request.feature_view = fco.name
    elif isinstance(fco, specs.FeatureServiceSpec):
        request.feature_service = fco.name
    else:
        msg = f"unexpected fco type {type(fco)}"
        raise RuntimeError(msg)
    request.task_type = TaskType.DATASET_GENERATION

    response = metadata_service.instance().GetDataframeInfo(request)
    ingest_utils.upload_df_pandas(response.signed_url_for_df_upload, df, parquet=True)
    return response.df_path


def _create_materialization_table(column_names: List[str], materialization_status_rows: List[List]) -> Displayable:
    # Setting `max_width=0` creates a table with an unlimited width.
    table = Displayable.from_table(headings=column_names, rows=materialization_status_rows, max_width=0)
    # Align columns in the middle horizontally
    table._text_table.set_cols_align(["c" for _ in range(len(column_names))])

    return table


def get_materialization_status_for_display(
    id_proto: id_pb2.Id, workspace: str, verbose: bool, limit: int, sort_columns: Optional[str], errors_only: bool
) -> Displayable:
    materialization_attempts = get_materialization_status_response(id_proto, workspace).materialization_attempts
    column_names, materialization_status_rows = utils.format_materialization_attempts(
        materialization_attempts, verbose, limit, sort_columns, errors_only
    )

    return _create_materialization_table(column_names, materialization_status_rows)
