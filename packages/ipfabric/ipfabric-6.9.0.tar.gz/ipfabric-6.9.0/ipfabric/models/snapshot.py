from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ipfabric import IPFClient

import logging
from datetime import datetime
from time import sleep
from typing import Optional, List, Union, Set, Dict, Literal, Any
from pathlib import Path
from ipfabric.models import Device
from ipfabric.tools import validate_ip_network_str, VALID_IP, raise_for_status
from ipfabric.settings.attributes import Attributes

from pydantic import BaseModel, Field, PrivateAttr
from .jobs import Jobs

logger = logging.getLogger("ipfabric")

SNAPSHOT_COLUMNS = {
    "id",
    "creatorUsername",
    "status",
    "finishStatus",
    "loadedSize",
    "unloadedSize",
    "name",
    "note",
    "sites",
    "fromArchive",
    "loading",
    "locked",
    "deviceAddedCount",
    "deviceRemovedCount",
    "interfaceActiveCount",
    "interfaceCount",
    "interfaceEdgeCount",
    "totalDevCount",
    "isLastSnapshot",
    "tsChange",
    "tsEnd",
    "tsStart",
    "userCount",
}


def loaded_status(func):
    def _decorator(self, *args, **kwargs):
        if not self.loaded:
            logger.error(f"Snapshot {self.snapshot_id} is not loaded.")
            return False
        return func(self, *args, **kwargs)

    return _decorator


def snapshot_upload(ipf: IPFClient, filename: str):
    data = {"file": (Path(filename).name, open(filename, "rb"), "application/x-tar")}
    resp = ipf.post("snapshots/upload", files=data)
    if resp.status_code == 400:
        if resp.json()["code"] == "API_SNAPSHOT_CONFLICT":
            logger.warning(f"SNAPSHOT ID {resp.json()['data']['snapshot']} already uploaded")
            return
    raise_for_status(resp)
    return resp.json()


class Error(BaseModel):
    error_type: str = Field(None, alias="errorType")
    count: int


class Snapshot(BaseModel):
    client: Any = Field(exclude=True)
    snapshot_id: str = Field(None, alias="id")
    name: Optional[str] = None
    note: Optional[str] = None
    creator_username: Optional[str] = Field(None, alias="creatorUsername")
    total_dev_count: int = Field(None, alias="totalDevCount")
    licensed_dev_count: Optional[int] = Field(None, alias="licensedDevCount")
    user_count: int = Field(None, alias="userCount")
    interface_active_count: int = Field(None, alias="interfaceActiveCount")
    interface_count: int = Field(None, alias="interfaceCount")
    interface_edge_count: int = Field(None, alias="interfaceEdgeCount")
    device_added_count: int = Field(None, alias="deviceAddedCount")
    device_removed_count: int = Field(None, alias="deviceRemovedCount")
    status: str
    finish_status: str = Field(None, alias="finishStatus")
    loading: bool
    locked: bool
    from_archive: bool = Field(None, alias="fromArchive")
    start: datetime = Field(None, alias="tsStart")
    end: Optional[datetime] = Field(None, alias="tsEnd")
    change: Optional[datetime] = Field(None, alias="tsChange")
    version: Optional[str] = None
    initial_version: Optional[str] = Field(None, alias="initialVersion")
    sites: List[str]
    errors: Optional[List[Error]] = None
    loaded_size: int = Field(None, alias="loadedSize")
    unloaded_size: int = Field(None, alias="unloadedSize")
    disabled_graph_cache: Optional[bool] = None
    disabled_historical_data: Optional[bool] = None
    disabled_intent_verification: Optional[bool] = None
    __jobs: Jobs = PrivateAttr()
    _local_attributes: Optional[Union[Attributes, bool]] = None

    @property
    def _jobs(self):
        if not getattr(self, "__jobs", None):
            self.__jobs = Jobs(client=self.client)
        return self.__jobs

    def discovery_errors(self, filters: dict = None, columns: List[str] = None, sort: dict = None) -> List[dict]:
        return self.client.fetch_all(
            "tables/reports/discovery-errors", snapshot_id=self.snapshot_id, filters=filters, columns=columns, sort=sort
        )

    def discovery_tasks(self, filters: dict = None, columns: List[str] = None, sort: dict = None) -> List[dict]:
        return self.client.fetch_all(
            "tables/reports/discovery-tasks", snapshot_id=self.snapshot_id, filters=filters, columns=columns, sort=sort
        )

    @property
    @loaded_status
    def errors_dict(self):
        return {_.error_type: _.count for _ in self.errors}

    @loaded_status
    def lock(self) -> bool:
        if not self.locked:
            raise_for_status(self.client.post(f"snapshots/{self.snapshot_id}/lock"))
            self.locked = True
        else:
            logger.warning(f"Snapshot {self.snapshot_id} is already locked.")
        return True

    def unlock(self) -> bool:
        if self.locked and self.loaded:
            raise_for_status(self.client.post(f"snapshots/{self.snapshot_id}/unlock"))
            self.locked = False
        else:
            logger.warning(f"Snapshot {self.snapshot_id} is already unlocked.")
        return True

    @property
    def loaded(self):
        return self.status == "done" and self.finish_status == "done" and self.loading is False

    @property
    def running(self):
        return not self.loading and self.status in ["run", "ready", "finishing"]

    def unload(self, wait_for_unload: bool = False, timeout: int = 60, retry: int = 5) -> bool:
        if not self.loaded:
            logger.warning(f"Snapshot {self.snapshot_id} is already unloaded.")
            return True
        ts = int(datetime.now().timestamp() * 1000)
        raise_for_status(self.client.post("snapshots/unload", json=[dict(jobDetail=ts, id=self.snapshot_id)]))
        if wait_for_unload:
            if not self._jobs.check_snapshot_job(self.snapshot_id, ts, "unload", retry, timeout):
                logger.error("Snapshot Unload did not finish.")
                return False
        self._refresh_status()
        return True

    def load(
        self,
        wait_for_load: bool = True,
        wait_for_assurance: bool = True,
        timeout: int = 60,
        retry: int = 5,
    ) -> bool:
        if self.loaded:
            logger.warning(f"Snapshot {self.snapshot_id} is already loaded.")
            return True
        ts = int(datetime.now().timestamp() * 1000)
        raise_for_status(self.client.post("snapshots/load", json=[dict(jobDetail=ts, id=self.snapshot_id)]))
        if wait_for_load or wait_for_assurance:
            if not self._check_load_status(ts, wait_for_assurance, timeout, retry):
                return False
        self._refresh_status()
        return True

    def _refresh_status(self):
        results = self.client.fetch(
            "tables/management/snapshots",
            columns=["status", "finishStatus", "loading"],
            filters={"id": ["eq", self.snapshot_id]},
            snapshot=False,
        )[0]
        self.status, self.finish_status, self.loading = (
            results["status"],
            results["finishStatus"],
            results["loading"],
        )

    def _check_load_status(
        self,
        ts: int,
        wait_for_assurance: bool = True,
        timeout: int = 60,
        retry: int = 5,
        action: str = "load",
    ):
        load_job = self._jobs.check_snapshot_job(
            self.snapshot_id, started=ts, action=action, timeout=timeout, retry=retry
        )
        if load_job and wait_for_assurance:
            return self._check_assurance_status(load_job["startedAt"], timeout, retry)
        elif not load_job:
            logger.error("Snapshot Load did not complete.")
            return False
        return True

    def _check_assurance_status(
        self,
        ts: int,
        timeout: int = 60,
        retry: int = 5,
    ):
        ae_settings = self.get_assurance_engine_settings()
        ae_status = False
        if ae_settings:
            ae_status = self._jobs.check_snapshot_assurance_jobs(
                self.snapshot_id, ae_settings, started=ts, timeout=timeout, retry=retry
            )
            if not ae_status:
                logger.error("Assurance Engine tasks did not complete")
        elif not ae_settings:
            logger.error("Could not get Assurance Engine tasks please check permissions.")
        if not ae_settings or not ae_status:
            self._change_snapshot()
            return False
        else:
            self.client.update()
            return True

    @loaded_status
    def attributes(self):
        return self.local_attributes.all()

    @property
    @loaded_status
    def local_attributes(self):
        if self._local_attributes is None:
            self._local_attributes = Attributes(client=self.client, snapshot_id=self.snapshot_id)
        return self._local_attributes

    def download(self, path: str = None, timeout: int = 60, retry: int = 5):
        if not path:
            path = Path(f"{self.snapshot_id}.tar")
        elif not isinstance(path, Path):
            path = Path(f"{path}")
        if not path.name.endswith(".tar"):
            path = Path(f"{path.name}.tar")

        # start download job
        ts = int(datetime.now().timestamp() * 1000)
        raise_for_status(self.client.get(f"/snapshots/{self.snapshot_id}/download"))

        # waiting for download job to process
        job = self._jobs.check_snapshot_job(
            self.snapshot_id, started=ts, action="download", retry=retry, timeout=timeout
        )
        if job:
            filename = self.client.get(f"jobs/{job['id']}/download")
            with open(path, "wb") as fp:
                fp.write(filename.read())
            return path
        logger.error(f"Download job did not finish within {retry * timeout} seconds, could not get file.")
        return None

    @loaded_status
    def get_snapshot_settings(self) -> Union[dict, None]:
        settings = None
        msg = "API_INSUFFICIENT_RIGHTS to `snapshots/:key/settings` " + self.client.user.error_msg

        if self.client.user.snapshots_settings is False:
            logger.debug(f"Could not get Snapshot {self.snapshot_id} Settings:" + msg)
            return settings

        res = self.client.get(f"/snapshots/{self.snapshot_id}/settings")
        if res.status_code == 200:
            settings = res.json()
            if self.client.user.snapshots_settings is None:
                self.client.user.snapshots_settings = True

        else:
            logger.debug(f"Could not get Snapshot {self.snapshot_id} Settings:" + msg)
            logger.warning(msg)
            self.client.user.snapshots_settings = False
        return settings

    @loaded_status
    def get_assurance_engine_settings(self) -> Union[dict, bool]:
        settings = self.get_snapshot_settings()
        if settings is None:
            logger.debug(f"Could not get Snapshot {self.snapshot_id} Settings to verify Assurance Engine tasks.")
            return False
        disabled = settings.get("disabledPostDiscoveryActions", list())
        self.disabled_graph_cache = True if "graphCache" in disabled else False
        self.disabled_historical_data = True if "historicalData" in disabled else False
        self.disabled_intent_verification = True if "intentVerification" in disabled else False
        return dict(
            disabled_graph_cache=self.disabled_graph_cache,
            disabled_historical_data=self.disabled_historical_data,
            disabled_intent_verification=self.disabled_intent_verification,
        )

    @loaded_status
    def update_assurance_engine_settings(
        self,
        disabled_graph_cache: bool = False,
        disabled_historical_data: bool = False,
        disabled_intent_verification: bool = False,
        wait_for_assurance: bool = True,
        timeout: int = 60,
        retry: int = 5,
    ) -> bool:
        settings = self.get_snapshot_settings(self.client)
        if settings is None:
            logger.error(
                f"Could not get Snapshot {self.snapshot_id} Settings and cannot update Assurance Engine tasks."
            )
            return False
        current = set(settings.get("disabledPostDiscoveryActions", list()))
        disabled, ae_settings = self._calculate_new_ae_settings(
            current, disabled_graph_cache, disabled_historical_data, disabled_intent_verification
        )
        if disabled == current:
            logger.info("No changes to Assurance Engine Settings required.")
            return True
        ts = int(datetime.now().timestamp() * 1000)
        raise_for_status(
            self.client.patch(
                f"/snapshots/{self.snapshot_id}/settings", json=dict(disabledPostDiscoveryActions=list(disabled))
            )
        )
        if wait_for_assurance and current - disabled:
            ae_status = self._jobs.check_snapshot_assurance_jobs(
                self.snapshot_id, ae_settings, started=ts, timeout=timeout, retry=retry
            )
            if not ae_status:
                logger.error("Assurance Engine tasks did not complete")
                return False
        return True

    @staticmethod
    def _calculate_new_ae_settings(
        current: set,
        disabled_graph_cache: bool = False,
        disabled_historical_data: bool = False,
        disabled_intent_verification: bool = False,
    ):
        disabled = set()
        if disabled_graph_cache:
            disabled.add("graphCache")
        if disabled_historical_data:
            disabled.add("historicalData")
        if disabled_intent_verification:
            disabled.add("intentVerification")
        enabled = current - disabled

        ae_settings = dict(
            disabled_graph_cache=False if "graphCache" in enabled else True,
            disabled_historical_data=False if "historicalData" in enabled else True,
            disabled_intent_verification=False if "intentVerification" in enabled else True,
        )

        return disabled, ae_settings

    @staticmethod
    def _dev_to_sn(devices: Union[List[str], List[Device], Set[str], str, Device]) -> Set[str]:
        sns = set()
        if not isinstance(devices, (list, set)):
            devices = {devices}
        for device in devices:
            if isinstance(device, str):
                sns.add(device)
            elif isinstance(device, Device):
                sns.add(device.sn)
        return sns

    @loaded_status
    def verify_snapshot_devices(
        self, devices: Union[List[str], List[Device], Set[str], str, Device]
    ) -> Dict[str, Set[str]]:
        """Checks to ensure that the Vendor is enabled for the devices.

        Args:
            devices: IP Fabric Device Serial Number, Device object, or list of either

        Returns: bool
        """
        sn = self._dev_to_sn(devices)
        payload = {
            "columns": ["id", "isApiTask", "sn", "settingsStates", "vendor"],
            "filters": {"isSelected": ["eq", True]},
            "bindVariables": {"selected": list(sn), "isDelete": False},
            "snapshot": self.snapshot_id,
        }
        snap_devs = self.client._ipf_pager("tables/snapshot-devices", payload)
        disabled = {dev["sn"] for dev in snap_devs if "noApiSettings" in dev["settingsStates"] and dev["isApiTask"]}
        valid = {dev["sn"] for dev in snap_devs if "ok" in dev["settingsStates"]}
        invalid = sn - valid - disabled
        if disabled:
            logger.warning(f"Vendor API(s) disabled for devices: {list(disabled)}.")
        if invalid:
            logger.warning(f"Invalid snapshot devices: {list(invalid)}.")
        return {"disabled": disabled, "invalid": invalid, "valid": valid}

    @loaded_status
    def delete_devices(
        self,
        devices: Union[List[str], List[Device], Set[str], str, Device],
        wait_for_discovery: bool = True,
        wait_for_assurance: bool = True,
        timeout: int = 60,
        retry: int = 5,
        skip_invalid_devices: bool = True,
    ) -> bool:
        """Rediscover device(s) based on a serial number or Device object.

        Args:
            devices: IP Fabric Device Serial Number, Device object, or list of either
            wait_for_discovery: Default True to wait before returning
            wait_for_assurance:  Default True to wait before returning
            timeout: How long to wait, larger snapshots will take longer times
            retry: Number of retries to wait ( (timeout X retry = total length) X 2) Will check for Discovery
                   and then use same times for Assurance.
            skip_invalid_devices: If a Vendor API device is included and the vendor is disabled it will be skipped
                                  instead of not refreshing devices.

        Returns: bool
        """
        return self._rediscover_delete_devices(
            "delete", devices, wait_for_discovery, wait_for_assurance, timeout, retry, skip_invalid_devices
        )

    @loaded_status
    def rediscover_devices(
        self,
        devices: Union[List[str], List[Device], Set[str], str, Device],
        wait_for_discovery: bool = True,
        wait_for_assurance: bool = True,
        timeout: int = 60,
        retry: int = 5,
        skip_invalid_devices: bool = True,
    ) -> bool:
        """Rediscover device(s) based on a serial number or Device object.

        Args:
            devices: IP Fabric Device Serial Number, Device object, or list of either
            wait_for_discovery: Default True to wait before returning
            wait_for_assurance:  Default True to wait before returning
            timeout: How long to wait, larger snapshots will take longer times
            retry: Number of retries to wait ( (timeout X retry = total length) X 2) Will check for Discovery
                   and then use same times for Assurance.
            skip_invalid_devices: If a Vendor API device is included and the vendor is disabled it will be skipped
                                  instead of not refreshing devices.

        Returns: bool
        """
        return self._rediscover_delete_devices(
            "refresh", devices, wait_for_discovery, wait_for_assurance, timeout, retry, skip_invalid_devices
        )

    @loaded_status
    def _rediscover_delete_devices(
        self,
        action: Literal["refresh", "delete"],
        devices: Union[List[str], List[Device], Set[str], str, Device],
        wait_for_discovery: bool = True,
        wait_for_assurance: bool = True,
        timeout: int = 60,
        retry: int = 5,
        skip_invalid_devices: bool = True,
    ) -> bool:
        """Rediscover device(s) based on a serial number or Device object.

        Args:
            devices: IP Fabric Device Serial Number, Device object, or list of either
            wait_for_discovery: Default True to wait before returning
            wait_for_assurance:  Default True to wait before returning
            timeout: How long to wait, larger snapshots will take longer times
            retry: Number of retries to wait ( (timeout X retry = total length) X 2) Will check for Discovery
                   and then use same times for Assurance.
            skip_invalid_devices: If a Vendor API device is included and the vendor is disabled it will be skipped
                                  instead of not refreshing devices.

        Returns: bool
        """
        sn = self._dev_to_sn(devices)
        devices = self.verify_snapshot_devices(sn)
        if not skip_invalid_devices and (devices["disabled"] or devices["invalid"]):
            return False
        sn = list(devices["valid"])
        if not sn:
            return False

        ts = int(datetime.now().timestamp() * 1000)
        if action == "delete":
            resp = self.client.request("DELETE", f"snapshots/{self.snapshot_id}/devices", json=sn)
        else:
            resp = self.client.post(
                f"snapshots/{self.snapshot_id}/devices", json=dict(snList=sn, vendorSettingsMap=dict())
            )
        raise_for_status(resp)
        if not wait_for_discovery:
            self._change_snapshot()
            return resp.json()["success"]

        return self._check_modification_status(wait_for_assurance, ts, timeout, retry, action)

    def _vendor_apis(self):
        vendors = list()
        for vendor in self.client.get(f"snapshots/{self.snapshot_id}/available-vendor-settings").json():
            vendor.pop("details", None)
            if vendor["type"] not in ["juniper-mist", "ruckus-vsz"]:
                vendor.pop("apiVersion", None)
            if vendor["type"] == "aws-ec2":
                vendor.pop("baseUrl", None)
            vendors.append(vendor)
        return vendors

    @loaded_status
    def add_devices(
        self,
        ip: Union[List[str], List[VALID_IP], str, VALID_IP] = None,
        refresh_vendor_api: bool = True,
        retry_timed_out: bool = True,
        wait_for_discovery: bool = True,
        wait_for_assurance: bool = True,
        timeout: int = 60,
        retry: int = 5,
    ) -> bool:
        """Add device(s) based on a IP address or subnet.

        Args:
            ip: Single IP or list of IPs
            refresh_vendor_api: Default True to refresh Vendor API devices that are enabled in snapshot settings.
            retry_timed_out: IP Default True to retry devices that timed out.
            wait_for_discovery: Default True to wait before returning
            wait_for_assurance:  Default True to wait before returning
            timeout: How long to wait, larger snapshots will take longer times
            retry: Number of retries to wait ( (timeout X retry = total length) X 2) Will check for Discovery
                   and then use same times for Assurance.

        Returns: bool
        """
        if not ip and not refresh_vendor_api and not retry_timed_out:
            raise SyntaxError("No snapshot modification selected.")
        elif not ip and not refresh_vendor_api and not self.errors_dict.get("ABCommandTimeout", 0):
            logger.warning(f"No Command Timeout Errors found in {self.snapshot_id}, not refreshing snapshot.")
            return True
        vendors = self._vendor_apis() if refresh_vendor_api else list()
        ips = list()
        ip = list() if ip is None else ip
        for i in [ip] if isinstance(ip, str) else ip:
            i = validate_ip_network_str(i)
            if int(i.split("/")[1]) < 23:
                raise ValueError(f"IP Network {i} is larger than /23.")
            ips.append(i)

        payload = {"ipList": ips, "retryTimedOut": retry_timed_out, "vendorApi": vendors}

        ts = int(datetime.now().timestamp() * 1000)
        resp = self.client.post(f"snapshots/{self.snapshot_id}/devices", json=payload)
        raise_for_status(resp)
        if not wait_for_discovery:
            self._change_snapshot()
            return resp.json()["success"]
        return self._check_modification_status(wait_for_assurance, ts, timeout, retry, "add")

    def _change_snapshot(self):
        logger.warning(f"Snapshot {self.snapshot_id} is discovering switching to $last.")
        sleep(2)
        self.client.update()

    def _check_modification_status(self, wait_for_assurance, ts, timeout, retry, action):
        job = self._jobs.check_snapshot_job(self.snapshot_id, started=ts, action=action, timeout=timeout, retry=retry)
        if job and wait_for_assurance:
            return self._check_assurance_status(job["startedAt"], timeout, retry)
        elif not job:
            logger.error(f"Snapshot Discovery {action.capitalize()} did not complete.")
        self.client.update()
        return True if job else False

    @loaded_status
    def add_ip_devices(
        self,
        ip: Union[List[str], List[VALID_IP], str, VALID_IP],
        wait_for_discovery: bool = True,
        wait_for_assurance: bool = True,
        timeout: int = 60,
        retry: int = 5,
    ) -> bool:
        """Refreshes Vendor API devices.

        Args:
            ip: Single IP or list of IPs
            wait_for_discovery: Default True to wait before returning
            wait_for_assurance:  Default True to wait before returning
            timeout: How long to wait, larger snapshots will take longer times
            retry: Number of retries to wait ( (timeout X retry = total length) X 2) Will check for Discovery
                   and then use same times for Assurance.

        Returns: bool
        """
        return self.add_devices(ip, False, False, wait_for_discovery, wait_for_assurance, timeout, retry)

    @loaded_status
    def refresh_vendor_api(
        self,
        wait_for_discovery: bool = True,
        wait_for_assurance: bool = True,
        timeout: int = 60,
        retry: int = 5,
    ) -> bool:
        """Refreshes Vendor API devices.

        Args:
            wait_for_discovery: Default True to wait before returning
            wait_for_assurance:  Default True to wait before returning
            timeout: How long to wait, larger snapshots will take longer times
            retry: Number of retries to wait ( (timeout X retry = total length) X 2) Will check for Discovery
                   and then use same times for Assurance.

        Returns: bool
        """
        return self.add_devices(None, True, False, wait_for_discovery, wait_for_assurance, timeout, retry)

    @loaded_status
    def retry_timed_out_devices(
        self,
        wait_for_discovery: bool = True,
        wait_for_assurance: bool = True,
        timeout: int = 60,
        retry: int = 5,
    ) -> bool:
        """Retries devices that timed out in Snapshot.

        Args:
            wait_for_discovery: Default True to wait before returning
            wait_for_assurance:  Default True to wait before returning
            timeout: How long to wait, larger snapshots will take longer times
            retry: Number of retries to wait ( (timeout X retry = total length) X 2) Will check for Discovery
                   and then use same times for Assurance.

        Returns: bool
        """
        return self.add_devices(None, False, True, wait_for_discovery, wait_for_assurance, timeout, retry)
