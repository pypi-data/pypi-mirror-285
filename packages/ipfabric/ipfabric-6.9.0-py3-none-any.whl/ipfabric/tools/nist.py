from time import sleep
from typing import List, Optional, Union

from httpx import Client, ReadTimeout, HTTPStatusError
from httpx._types import ProxiesTypes
from pydantic import BaseModel, ConfigDict, field_validator


class CveMetricV2(BaseModel):
    model_config = ConfigDict(extra="ignore")
    version: str
    accessVector: str
    accessComplexity: str
    confidentialityImpact: str
    integrityImpact: str
    availabilityImpact: str
    baseScore: float
    baseSeverity: str
    exploitabilityScore: float
    impactScore: float
    acInsufInfo: bool
    obtainAllPrivilege: bool
    obtainUserPrivilege: bool
    obtainOtherPrivilege: bool
    userInteractionRequired: Optional[bool] = None


class CveMetricV3(BaseModel):
    model_config = ConfigDict(extra="ignore")
    version: str
    attackVector: str
    attackComplexity: str
    privilegesRequired: str
    userInteraction: str
    scope: str
    confidentialityImpact: str
    integrityImpact: str
    availabilityImpact: str
    baseScore: float
    baseSeverity: str
    exploitabilityScore: float
    impactScore: float


class CVE(BaseModel):
    cve_id: str
    description: str
    url: str
    metric_v2: Optional[Union[CveMetricV2, dict]] = None
    metric_v3: Optional[Union[CveMetricV3, dict]] = None

    @field_validator("metric_v3")
    @classmethod
    def create_metric_v3(cls, metric: Union[dict, CveMetricV3]) -> Union[None, CveMetricV3]:
        if isinstance(metric, CveMetricV3):
            return metric
        elif not metric:
            return None
        metrics = sorted([_ for _ in metric.keys() if "cvssMetricV3" in _], reverse=True)
        if not metrics:
            return None
        return CveMetricV3(**metric[metrics[0]][0], **metric[metrics[0]][0]["cvssData"])

    @field_validator("metric_v2")
    @classmethod
    def create_metric_v2(cls, metric: Union[dict, CveMetricV2]) -> Union[None, CveMetricV2]:
        if isinstance(metric, CveMetricV2):
            return metric
        elif not metric:
            return None
        metrics = sorted([_ for _ in metric.keys() if "cvssMetricV2" in _], reverse=True)
        if not metrics:
            return None
        return CveMetricV2(**metric[metrics[0]][0], **metric[metrics[0]][0]["cvssData"])

    @property
    def base_score(self) -> Union[float, None]:
        if self.metric_v3:
            return self.metric_v3.baseScore
        elif self.metric_v2:
            return self.metric_v2.baseScore
        return None

    def __repr__(self):
        return self.cve_id

    def __hash__(self):
        return hash(self.cve_id)


class CVEs(BaseModel):
    total_results: int
    cves: List[CVE]
    error: Optional[str] = None


class NIST(Client):
    def __init__(self, nvd_api_key: str, timeout, proxies: Optional[ProxiesTypes] = None):
        """
        NIST updated to API v2.0.  You must request and pass an API Key which can be obtained at
        https://nvd.nist.gov/developers/request-an-api-key

        Args:
            nvd_api_key: str: https://nvd.nist.gov/developers/request-an-api-key
            timeout: int:
        """
        super().__init__(
            base_url="https://services.nvd.nist.gov/rest/json/cves/2.0",
            timeout=timeout,
            headers={"apiKey": nvd_api_key},
            proxy=proxies,
        )

    @property
    def params(self):
        return {"virtualMatchString": "cpe:2.3:*:", "startIndex": 0}

    @staticmethod
    def _check_cisco(family, version, vendor, params):
        if family == "wlc-air":
            family = "wireless_lan_controller_software"
        elif family == "ftd":
            family = "firepower"
            version = (version.replace("(Bu", ".Bu")).replace(")", ".").split(" .", 1)[0]
        elif family != "nx-os":
            family = family.replace("-", "_")
        version = (version.replace("(", ".")).replace(")", ".")
        params["virtualMatchString"] += vendor + ":" + family + ":" + version
        return params

    def check_cve(self, vendor: str, family: str, version: str) -> CVEs:  # noqa: C901
        """returns CVE data about a specific product line

        Args:
        vendor: Vendor for the device to be checked
        family: Family of the device to be checked
        version: Software version of the device to be checked
        Returns:
            a list of CVEs
        """
        params = self.params
        if vendor in ["azure", "aws", "gcp"] or family == "meraki":
            return CVEs(total_results=0, cves=[], error="Unsupported")
        elif vendor == "juniper":
            version = version[: version.rfind("R") + 2].replace("R", ":r")
            params["virtualMatchString"] += vendor + ":" + family + ":" + version
        elif vendor == "paloalto":
            params["virtualMatchString"] += "palo_alto" + ":" + family + ":" + version
        elif vendor == "extreme":
            family = "extremexos" if "xos" in family else family
            params["virtualMatchString"] += "extremenetworks" + ":" + family + ":" + version
        elif family and "aruba" in family:
            params["virtualMatchString"] += "arubanetworks:arubaos" + ":" + version
        elif vendor == "f5" and family == "big-ip":
            params["virtualMatchString"] += vendor + ":" + "big-ip_access_policy_manager" + ":" + version
        elif vendor == "cisco":
            params = self._check_cisco(family, version, vendor, params)
        elif vendor == "fortinet" and family == "fortigate":
            params["virtualMatchString"] += "fortinet:fortios:" + version.replace(",", ".")
        elif vendor == "checkpoint" and family == "gaia":
            params["virtualMatchString"] += vendor + ":" + "gaia_os" + version.replace("R", ":r")
        elif vendor == "arista":
            params["virtualMatchString"] += vendor + ":" + family + ":" + version.lower()
        else:
            return CVEs(total_results=0, cves=[], error="Unsupported")
        return self._query_cve(params)

    def _query_cve(self, params):
        try:
            sleep(0.3)  # NIST Rate Limit: 50 requests/30 seconds
            res = self.get("", params=params)
            res.raise_for_status()
            data = res.json()

            cves = CVEs(
                total_results=data["totalResults"],
                cves=[
                    CVE(
                        cve_id=i["cve"]["id"],
                        description=i["cve"]["descriptions"][0]["value"],
                        url=i["cve"]["references"][0]["url"],
                        metric_v2=i["cve"].get("metrics", {}),
                        metric_v3=i["cve"].get("metrics", {}),
                    )
                    for i in data["vulnerabilities"]
                ],
            )
            return cves
        except ReadTimeout:
            return CVEs(total_results=0, cves=[], error="Timeout")
        except HTTPStatusError:
            return CVEs(total_results=0, cves=[], error="HTTP Error")
