from abc import ABC
from datetime import timedelta
from typing import Optional

from tecton._internals import materialization_api
from tecton._internals import metadata_service
from tecton._internals.display import Displayable
from tecton.framework.dataset import SavedDataset
from tecton_proto.metadataservice.metadata_service__client_pb2 import GetSavedFeatureDataFrameRequest


class TectonJob(ABC):
    def cancel_job(self) -> bool:
        pass

    # wait for all sub-tasks to complete
    def wait_for_completion(self, timeout: Optional[timedelta] = None):
        pass

    def get_job_status_for_display(self) -> Displayable:
        pass


class DatasetJob(TectonJob):
    _job: materialization_api.DatasetJobData

    def __init__(self, job: materialization_api.DatasetJobData):
        self._job = job

    @classmethod
    def _from_job_data(cls, job: materialization_api.DatasetJobData):
        return cls(job)

    # cancel all sub-tasks
    def cancel_job(self) -> bool:
        materialization_api.cancel_dataset_job(self._job.dataset, self._job.workspace, self._job.id)

    # wait for all sub-tasks to complete
    def wait_for_completion(self, timeout: Optional[timedelta] = None):
        self._job = materialization_api.wait_for_dataset_job(
            self._job.dataset, self._job.workspace, self._job.id, timeout=timeout
        )

    # return dataset object, if job is completed
    def get_dataset(self) -> Optional[SavedDataset]:
        if self._job.state != "SUCCESS":
            return

        request = GetSavedFeatureDataFrameRequest(
            saved_feature_dataframe_name=self._job.dataset, workspace=self._job.workspace
        )
        response = metadata_service.instance().GetSavedFeatureDataFrame(request)
        return SavedDataset._from_proto(response.saved_feature_dataframe)

    def get_job_status_for_display(self) -> Displayable:
        pass
