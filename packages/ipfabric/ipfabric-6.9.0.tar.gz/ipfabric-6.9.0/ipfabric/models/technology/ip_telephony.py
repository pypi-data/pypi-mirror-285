import logging
from typing import Any, Optional

from pydantic import BaseModel, Field, computed_field

from ipfabric.models.table import Table

logger = logging.getLogger("ipfabric")


class IpTelephony(BaseModel):
    client: Any = Field(None, exclude=True)
    sn: Optional[str] = None

    @computed_field
    @property
    def phones(self) -> Table:
        return Table(client=self.client, endpoint="tables/inventory/phones", sn=self.sn)
