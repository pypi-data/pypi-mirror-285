import logging
import re
from http.cookiejar import CookieJar
from importlib import metadata
from typing import Optional, Union, Generator, Any, Type, Tuple, Literal, Mapping, List, Dict

from httpx import Client, BaseTransport, URL, Request, Response, Auth, Timeout, post, Proxy
from httpx._client import EventHook
from httpx._types import CertTypes, VerifyTypes, URLTypes
from pydantic import field_validator, Field, AliasChoices, PrivateAttr, InstanceOf
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource, InitSettingsSource

from ipfabric.tools import raise_for_status, valid_snapshot

logger = logging.getLogger("ipfabric")

RE_VERSION = re.compile(r"v?(\d(\.\d)?)")
ProxyTypes = Union[None, URLTypes, InstanceOf[Proxy]]
ProxiesTypes = Union[ProxyTypes, Dict[URLTypes, Union[None, ProxyTypes]]]
TimeoutTypes = Union[
    Optional[float], Tuple[Optional[float], Optional[float], Optional[float], Optional[float]], Timeout, None
]


def log_request(request: Request):
    logger.debug(f"Request event hook: {request.method} {request.url} - Waiting for response")


def log_response(response: Response):
    request = response.request
    logger.debug(f"Response event hook: {request.method} {request.url} - Status {response.status_code}")


class TokenAuth(Auth):
    def __init__(self, token: str) -> None:
        self._auth_header = token

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        request.headers["X-API-Token"] = self._auth_header
        yield request


class AccessToken(Auth):
    def __init__(self, cookie_jar: CookieJar, username: str, password: str, base_url: URL, verify: VerifyTypes):
        self.cookie_jar = cookie_jar
        self._login(username, password, base_url, verify)

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        response = yield request

        if response.status_code == 401:
            response.read()
            if "API_EXPIRED_ACCESS_TOKEN" in response.text:
                # Use refreshToken in Cookies to get new accessToken & Response updates accessToken in shared CookieJar
                resp = raise_for_status(post(response.url.join("/api/auth/token"), cookies=self.cookie_jar))
                request.headers["Cookie"] = "accessToken=" + resp.cookies["accessToken"]  # Update request
                yield request
        return response

    def _login(self, username: str, password: str, base_url: URL, verify: VerifyTypes) -> None:
        raise_for_status(
            post(
                base_url.join("auth/login"),
                json=dict(username=username, password=password),
                cookies=self.cookie_jar,
                verify=verify,
            )
        )


class MyInitSettingsSource(InitSettingsSource):
    def __init__(self, settings_cls, init_kwargs: Dict[str, Any]):
        timeout = init_kwargs.pop("timeout", "DEFAULT")
        init_kwargs = {k: v for k, v in init_kwargs.items() if v is not None}
        if timeout != "DEFAULT":
            init_kwargs["timeout"] = timeout
        super().__init__(settings_cls, init_kwargs)


class Setup(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_prefix="ipf_", extra="allow")
    base_url: Union[str, URL] = Field(None, validation_alias=AliasChoices("base_url", "ipf_url"))
    api_version: Optional[Union[int, float, str]] = Field(
        None, validation_alias=AliasChoices("api_version", "ipf_version")
    )
    auth: Optional[Any] = Field(None, alias="auth", exclude=True)
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    snapshot_id: Optional[Union[str, None]] = Field(
        "$last", validation_alias=AliasChoices("snapshot_id", "ipf_snapshot")
    )
    verify: Optional[VerifyTypes] = True
    timeout: Union[TimeoutTypes, Literal["DEFAULT"]] = Timeout(timeout=5.0)
    nvd_api_key: Optional[str] = Field(None, alias="nvd_api_key")
    debug: Optional[bool] = False
    http2: Optional[bool] = True
    proxy: Optional[Union[ProxyTypes, None]] = None
    proxies: Optional[Union[ProxiesTypes, None]] = None
    mounts: Optional[Mapping[str, Optional[BaseTransport]]] = None
    cert: Optional[Union[CertTypes, None]] = None
    event_hooks: Optional[Mapping[str, List[EventHook]]] = None
    _cookie_jar: CookieJar = PrivateAttr(default_factory=CookieJar)
    client: Optional[Client] = Field(None, exclude=True)
    os_version: Optional[str] = Field(None)
    _os_api_version: Optional[str] = PrivateAttr(None)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            MyInitSettingsSource(settings_cls, init_settings.init_kwargs),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    def model_post_init(self, __context):
        event_hooks = {"request": [log_request], "response": [log_response]} if self.debug else self.event_hooks
        self.client = Client(
            base_url=self.base_url,
            cookies=self._cookie_jar,
            http2=self.http2,
            verify=self.verify,
            timeout=self.timeout,
            headers={"User-Agent": f'python-ipfabric-sdk/{metadata.version("ipfabric")}'},
            event_hooks=event_hooks,
            proxy=self.proxy,
            proxies=self.proxies,
            mounts=self.mounts,
            cert=self.cert,
        )
        if not (self.auth or self.token) and not (self.username and self.password):
            raise RuntimeError("IP Fabric Authentication not provided.")
        self.api_version, self.os_version, self._os_api_version = self.check_version()
        self.base_url = self.base_url.join(f"api/{self.api_version}/")
        self.client.base_url = self.base_url
        if self.auth:
            if isinstance(self.auth, str):
                self.client.auth = TokenAuth(self.auth)
            elif isinstance(self.auth, tuple):
                self.client.auth = AccessToken(self._cookie_jar, self.auth[0], self.auth[1], self.base_url, self.verify)
            else:
                self.client.auth = self.auth
        elif self.token:
            self.client.auth = TokenAuth(self.token)
        elif self.username and self.password:
            self.client.auth = AccessToken(self._cookie_jar, self.username, self.password, self.base_url, self.verify)

    @property
    def update_attrs(self) -> dict:
        return {
            "base_url": self.base_url,
            "api_version": self.api_version,
            "_os_version": self.os_version,
            "_os_api_version": self._os_api_version,
            "debug": self.debug,
            "_client": self.client,
            "timeout": self.client.timeout,
        }

    def check_version(self) -> tuple:
        """Checks API Version and returns the version to use in the URL and the OS Version

        Returns:
            api_version, os_version
        """
        cfg_version = self.api_version.lstrip("v").split(".")

        resp = raise_for_status(self.client.get("/api/version"))
        os_api_version = resp.json()["apiVersion"].lstrip("v").split(".")
        api_version = f"v{cfg_version[0]}.{cfg_version[1]}" if len(cfg_version) > 1 else f"v{cfg_version[0]}"
        if len(cfg_version) == 1 and cfg_version[0] > os_api_version[0]:
            logger.warning(
                f"Specified API or SDK Version (v{cfg_version[0]}) is greater then "
                f"OS API Version. Using OS Version:  (v{os_api_version[0]})"
            )
            api_version = f"v{os_api_version[0]}"
        elif cfg_version[0:2] > os_api_version:
            logger.warning(
                f"Specified API or SDK Version (v{'.'.join(cfg_version)}) is greater then "
                f"OS API Version. Using OS Version:  (v{'.'.join(os_api_version)})"
            )
            api_version = f"v{os_api_version[0]}.{os_api_version[1]}"
        elif os_api_version[0] > cfg_version[0]:
            raise RuntimeError(
                f"OS Major Version v{os_api_version[0]} is greater then SDK Version "
                f"v{cfg_version[0]}.  Please upgrade the Python SDK to the new major version."
            )

        return api_version, resp.json()["releaseVersion"], resp.json()["apiVersion"]

    @field_validator("api_version")
    @classmethod
    def _valid_version(cls, v: Union[None, int, float, str]) -> Union[None, str]:
        if not v:
            return metadata.version("ipfabric")
        elif RE_VERSION.match(str(v)):
            return "v" + RE_VERSION.match(str(v)).group(1)
        else:
            raise ValueError(f"IPF_VERSION ({v}) is not valid, must be like `v#` or `v#.#`.")

    @field_validator("base_url")
    @classmethod
    def _convert_url(cls, v: Union[URL, str]) -> URL:
        if isinstance(v, str):
            v = URL(v)
        return v

    @field_validator("snapshot_id")
    @classmethod
    def _valid_snapshot(cls, v: Union[None, str]) -> str:
        return valid_snapshot(v, init=True)

    @field_validator("verify")
    @classmethod
    def _verify(cls, v: Union[bool, int, str]) -> Union[bool, str]:
        if isinstance(v, bool):
            return v
        elif isinstance(v, int):
            return bool(v)
        elif v.lower() in {"0", "off", "f", "false", "n", "no", "1", "on", "t", "true", "y", "yes"}:
            return False if v.lower() in {0, "0", "off", "f", "false", "n", "no"} else True
        else:
            return v

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Needed for context"""
        pass
