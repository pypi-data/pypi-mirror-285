from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional

import click

from tecton import tecton_context
from tecton._internals import metadata_service
from tecton.cli import cli_utils
from tecton.cli import printer
from tecton.cli.command import TectonGroup
from tecton.cli.engine import EngineCommand
from tecton_core.id_helper import IdHelper
from tecton_core.specs.utils import get_timestamp_field_or_none
from tecton_proto.data import state_update__client_pb2 as state_update_pb2
from tecton_proto.metadataservice import metadata_service__client_pb2 as metadata_service_pb2


def format_date(datetime: datetime.datetime):
    return datetime.strftime("%Y-%m-%d %H:%M:%S %Z")


@dataclass
class IntegrationTestSummaries:
    statuses: Dict[str, List[state_update_pb2.IntegrationTestJobStatus]]

    @staticmethod
    def summarize_status(integration_status_list: List) -> str:
        """Given a list of integration test statuses, summarize the state of the entire bunch."""
        if not integration_status_list:
            return "No Tests"
        elif all(
            integration_status == state_update_pb2.IntegrationTestJobStatus.JOB_STATUS_SUCCEED
            for integration_status in integration_status_list
        ):
            return "Succeeded"
        elif any(
            integration_status == state_update_pb2.IntegrationTestJobStatus.JOB_STATUS_FAILED
            for integration_status in integration_status_list
        ):
            return "Failed"
        elif any(
            integration_status == state_update_pb2.IntegrationTestJobStatus.JOB_STATUS_CANCELLED
            for integration_status in integration_status_list
        ):
            return "Canceled"
        elif any(
            integration_status == state_update_pb2.IntegrationTestJobStatus.JOB_STATUS_RUNNING
            for integration_status in integration_status_list
        ):
            return "Running"
        elif any(
            integration_status == state_update_pb2.IntegrationTestJobStatus.JOB_STATUS_NOT_STARTED
            for integration_status in integration_status_list
        ):
            return "Not Started"
        else:
            return "Unknown Status"

    def summarize_status_for_all_tests(self):
        all_test_statuses = []
        for _, status_list in self.statuses.items():
            all_test_statuses.extend(status_list)
        return self.summarize_status(all_test_statuses)

    def summarize_status_by_fv(self):
        return {fv_name: self.summarize_status(status_list) for fv_name, status_list in self.statuses.items()}

    @classmethod
    def from_protobuf(cls, successful_plan_output: state_update_pb2.SuccessfulPlanOutput):
        statuses = {}
        for test_summary in successful_plan_output.test_summaries:
            test_job_statuses = [job_summary.status for job_summary in test_summary.job_summaries]
            statuses[test_summary.feature_view_name] = test_job_statuses
        return cls(statuses=statuses)


@dataclass
class PlanListItem:
    plan_id: str
    applied_by: Optional[str]
    applied_at: Optional[datetime.datetime]
    created_by: str
    created_at: datetime.datetime
    workspace: str
    sdk_version: str
    integration_test_statuses: IntegrationTestSummaries

    @property
    def applied(self):
        if bool(self.applied_by):
            return "Applied"
        else:
            return "Created"

    @classmethod
    def from_proto(cls, state_update_entry: state_update_pb2.StateUpdateEntry):
        applied_by = cli_utils.display_principal(state_update_entry.applied_by_principal, state_update_entry.applied_by)
        applied_at = get_timestamp_field_or_none(state_update_entry, "applied_at")
        created_at = get_timestamp_field_or_none(state_update_entry, "created_at")
        return cls(
            # commit_id is called plan_id in public facing UX. Re-aliasing here.
            plan_id=state_update_entry.commit_id,
            applied_by=applied_by,
            applied_at=applied_at,
            created_by=state_update_entry.created_by,
            created_at=created_at,
            workspace=state_update_entry.workspace,
            sdk_version=state_update_entry.sdk_version,
            integration_test_statuses=IntegrationTestSummaries.from_protobuf(state_update_entry.successful_plan_output),
        )


@dataclass
class PlanSummary:
    applied_at: Optional[datetime.datetime]
    applied_by: Optional[str]
    applied: bool
    created_at: datetime.datetime
    created_by: str
    workspace: str
    sdk_version: str

    @classmethod
    def from_proto(cls, state_update_summary: state_update_pb2.StateUpdatePlanSummary):
        applied_at = get_timestamp_field_or_none(state_update_summary, "applied_at")
        applied_by = cli_utils.display_principal(
            state_update_summary.applied_by_principal, state_update_summary.applied_by
        )
        applied = bool(applied_at)
        created_at = get_timestamp_field_or_none(state_update_summary, "created_at")
        return cls(
            applied=applied,
            applied_at=applied_at,
            applied_by=applied_by,
            created_at=created_at,
            created_by=state_update_summary.created_by,
            workspace=state_update_summary.workspace,
            sdk_version=state_update_summary.sdk_version,
        )


def get_plans_list_items(workspace: str, limit: int):
    request = metadata_service_pb2.GetStateUpdatePlanListRequest(workspace=workspace, limit=limit)
    response = metadata_service.instance().GetStateUpdatePlanList(request)
    return [PlanListItem.from_proto(entry) for entry in response.entries]


def get_plan(plan_id):
    plan_id = IdHelper.from_string(plan_id)
    request = metadata_service_pb2.GetStateUpdatePlanSummaryRequest(plan_id=plan_id)
    response = metadata_service.instance().GetStateUpdatePlanSummary(request)
    return PlanSummary.from_proto(response.plan)


@click.group("plan", cls=TectonGroup)
def plan():
    r"""⚠️  Command has moved: Use `tecton plan create` to create a plan.\n
    Manage Tecton Plans in a Workspace
    """


create = EngineCommand(
    name="create",
    apply=False,
    allows_suppress_recreates=True,
    help="Create a plan: Compare your local feature definitions with remote state and show the plan to bring them in sync.",
    has_integration_test=True,
)


plan.add_command(create)


@plan.command(uses_workspace=True)
@click.option("--limit", default=10, type=int, help="Number of log entries to return.")
def list(limit):
    """List previous tecton plans in this workspace."""
    workspace = tecton_context.get_current_workspace()
    entries = get_plans_list_items(workspace, limit)
    table_rows = [
        (
            entry.plan_id,
            entry.applied,
            entry.integration_test_statuses.summarize_status_for_all_tests(),
            entry.created_by,
            format_date(entry.created_at),
            entry.sdk_version,
        )
        for entry in entries
    ]
    cli_utils.display_table(
        ["Plan Id", "Plan Status", "Test Status", "Created by", "Creation Date", "SDK Version"], table_rows
    )


@plan.command()
@click.argument("plan-id", required=True)
def show(plan_id):
    """Show details of a Tecton Plan"""
    plan = get_plan(plan_id=plan_id)
    printer.safe_print(f"Showing current status for Plan {plan_id}")
    printer.safe_print()
    printer.safe_print(f"Created at: {format_date(plan.created_at)}")
    printer.safe_print(f"Created by: {plan.created_by}")
    printer.safe_print(f"Applied: {plan.applied}")
    if plan.applied:
        printer.safe_print(f"Applied at: {format_date(plan.applied_at)}")
        printer.safe_print(f"Applied by: {plan.applied_by}")

    # TODO: Add integration test information here
