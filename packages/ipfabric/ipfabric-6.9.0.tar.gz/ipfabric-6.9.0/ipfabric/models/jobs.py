import logging
from time import sleep
from typing import Any, Literal

from pydantic import BaseModel, Field

from .table import BaseTable

logger = logging.getLogger("ipfabric")

SNAP_JOBS = {
    "load": "snapshotLoad",
    "unload": "snapshotUnload",
    "download": "snapshotDownload",
    "add": "discoveryAdd",
    "refresh": "discoveryRefresh",
    "delete": "deleteDevice",
    "recalculate": "recalculateSites",
}

SNAP_ACTIONS = Literal["load", "unload", "download", "add", "refresh", "delete"]


class Jobs(BaseModel):
    client: Any = Field(exclude=True)

    @property
    def all_jobs(self):
        return BaseTable(client=self.client, endpoint="tables/jobs")

    @property
    def columns(self):
        return [
            "id",
            "downloadFile",
            "finishedAt",
            "isDone",
            "name",
            "scheduledAt",
            "snapshot",
            "startedAt",
            "status",
            "username",
        ]

    def _return_job_when_done(self, job_filter: dict, retry: int = 5, timeout: int = 5):
        """
        Returns the finished job. Only supports Snapshot related Jobs
        Args:
            job_filter: table filter for jobs
            retry: how many times to query the table
            timeout: how long to wait in-between retries

        Returns:
            job: list[dict[str, str]]: a job that has a status of done
        """
        if "name" not in job_filter and "snapshot" not in job_filter:
            raise SyntaxError("Must provide a Snapshot ID and name for a filter.")
        sleep(1)  # give the IPF server a chance to start the job
        # find the running snapshotDownload job (i.e. not done)
        jobs = self.all_jobs.fetch(
            filters=job_filter,
            sort={"order": "desc", "column": "startedAt"},
            columns=self.columns,
        )
        logger.debug(f"job filter: {job_filter}\nlist of jobs:{jobs}")
        if jobs:
            # if the job is already completed, we return it
            if jobs[0]["isDone"]:
                return jobs[0]
            # use the start time of this job to identify this specific job
            start_time = jobs[0]["startedAt"]
            job_filter["startedAt"] = ["eq", start_time]
            logger.debug(f"new job_filter: {job_filter}")

            for retries in range(retry):
                jobs = self.all_jobs.fetch(
                    filters=job_filter, sort={"order": "desc", "column": "startedAt"}, columns=self.columns
                )
                logger.debug(f"Current job: {jobs}")
                if jobs and jobs[0]["isDone"]:
                    return jobs[0]
                logger.info(
                    f"{job_filter['name'][1]} job is not ready for snapshot"
                    f" {job_filter['snapshot'][1]} ({retries}/{retry})"
                )
                sleep(timeout)
        else:
            logger.debug(f"job not found: {job_filter}")
        return None

    def check_snapshot_job(
        self, snapshot_id: str, started: int, action: SNAP_ACTIONS, retry: int = 5, timeout: int = 5
    ):
        """Checks to see if a snapshot load job is completed.

        Args:
            snapshot_id: UUID of a snapshot
            started: Integer time since epoch in milliseconds
            action: Type of job to filter on
            timeout: How long in seconds to wait before retry
            retry: how many retries to use when looking for a job, increase for large downloads

        Returns:
            Job dictionary if load is completed, None if still loading
        """
        j_filter = dict(snapshot=["eq", snapshot_id], name=["eq", SNAP_JOBS[action]], startedAt=["gte", started - 100])
        return self._return_job_when_done(j_filter, retry=retry, timeout=timeout)

    def check_snapshot_assurance_jobs(
        self, snapshot_id: str, assurance_settings: dict, started: int, retry: int = 5, timeout: int = 5
    ):
        """Checks to see if a snapshot Assurance Engine calculation jobs are completed.

        Args:
            snapshot_id: UUID of a snapshot
            assurance_settings: Dictionary from Snapshot.get_assurance_engine_settings
            started: Integer time since epoch in milliseconds
            timeout: How long in seconds to wait before retry
            retry: how many retries to use when looking for a job, increase for large downloads

        Returns:
            True if load is completed, False if still loading
        """
        j_filter = dict(snapshot=["eq", snapshot_id], name=["eq", "loadGraphCache"], startedAt=["gte", started - 100])
        if (
            assurance_settings["disabled_graph_cache"] is False
            and self._return_job_when_done(j_filter, retry=retry, timeout=timeout) is None
        ):
            logger.error("Graph Cache did not finish loading; Snapshot is not fully loaded yet.")
            return False
        j_filter["name"] = ["eq", "saveHistoricalData"]
        if (
            assurance_settings["disabled_historical_data"] is False
            and self._return_job_when_done(j_filter, retry=retry, timeout=timeout) is None
        ):
            logger.error("Historical Data did not finish loading; Snapshot is not fully loaded yet.")
            return False
        j_filter["name"] = ["eq", "report"]
        if (
            assurance_settings["disabled_intent_verification"] is False
            and self._return_job_when_done(j_filter, retry=retry, timeout=timeout) is None
        ):
            logger.error("Intent Calculations did not finish loading; Snapshot is not fully loaded yet.")
            return False
        return True
