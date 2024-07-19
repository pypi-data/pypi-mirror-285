from typing import Any

import aiohttp
import orjson
from pydantic import BaseModel, Field, HttpUrl, SecretStr

from supavisor.types import AddTenantParams


class Supavisor(BaseModel):
    supavisor_url: HttpUrl = Field(
        description="Supavisor base url",
    )
    supavisor_api_key: SecretStr = Field(
        description="Supavisor API key",
    )

    async def add_tenant(self, tenant: str, params: AddTenantParams) -> dict[str, Any]:
        """
        Endpoint to add a tenant
        Example:

        ```python
        from supavisor.client import Supavisor
        from supavisor.types import AddTenantParams, TenantParams, TenantUser
        from pydantic import SecretStr

        >>> supavisor = Supavisor(
        ...     supavisor_url="http://localhost:4000",
        ...     supavisor_api_key=SecretStr("secret"),
        ... )
        >>> tenant = "tenant1"

        >>> params = AddTenantParams(
        ...     tenant=TenantParams(
        ...         db_database=tenant,
        ...         db_host="roundhouse.proxy.rlwy.net",
        ...         db_port=17072,
        ...         enforce_ssl=False,
        ...         require_user=True,
        ...         users=[
        ...             TenantUser(db_user="user", db_password="********")
        ...         ],
        ...     )
        ... )

        >>> await supavisor.add_tenant(tenant, params)
        """

        url = f"{self.supavisor_url.unicode_string()}/api/tenants/{tenant}"
        headers: dict[str, str] = {
            "Authorization": f"Bearer {self.supavisor_api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=90),
            json_serialize=orjson.dumps,  # type: ignore[arg-type]
        ) as session:
            async with session.put(
                url, headers=headers, data=params.model_dump_json()
            ) as response:
                res: dict[str, Any] = await response.json(
                    content_type=None, loads=orjson.loads
                )

                if response.status != 200:
                    raise Exception(response.status)

                data = res.get("data")

                if data is None:
                    raise Exception("Data is None")

                return data
