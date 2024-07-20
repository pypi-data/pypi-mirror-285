import logging
from typing import Any, Optional
from warnings import warn

from pydantic import BaseModel, Field, computed_field

from ipfabric.models.table import Table

logger = logging.getLogger("ipfabric")


class Sdwan(BaseModel):
    client: Any = Field(None, exclude=True)
    sn: Optional[str] = None

    @computed_field
    @property
    def sites(self) -> Table:
        # TODO: Remove 7.0
        warn("Sdwan.sites will be moved to Sdwan.versa_sites in 7.0", DeprecationWarning, stacklevel=2)
        return Table(client=self.client, endpoint="tables/sdwan/sites", sn=self.sn)

    @computed_field
    @property
    def links(self) -> Table:
        # TODO: Remove 7.0
        warn("Sdwan.links will be moved to Sdwan.versa_links in 7.0", DeprecationWarning, stacklevel=2)
        return Table(client=self.client, endpoint="tables/sdwan/links", sn=self.sn)

    @computed_field
    @property
    def versa_sites(self) -> Table:
        return Table(client=self.client, endpoint="tables/sdwan/links", sn=self.sn)

    @computed_field
    @property
    def versa_links(self) -> Table:
        return Table(client=self.client, endpoint="tables/sdwan/links", sn=self.sn)
