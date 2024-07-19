from contextlib import asynccontextmanager
from typing import Any, override

import aiohttp
import orjson
from pydantic import BaseModel, Field, HttpUrl, PrivateAttr, SecretStr

from supavisor.types import AddTenantParams


class Supavisor(BaseModel):
    __headers: dict[str, str] = PrivateAttr(default_factory=dict)
    supavisor_url: HttpUrl = Field(
        description="Supavisor base url",
    )
    supavisor_api_key: SecretStr = Field(
        description="Supavisor API key",
    )
    
    @override
    def __init__(self, supavisor_url: HttpUrl, supavisor_api_key: SecretStr):
        super().__init__(supavisor_url=supavisor_url, supavisor_api_key=supavisor_api_key)
        self.__headers = {
            "Authorization": f"Bearer {self.supavisor_api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }

    @asynccontextmanager
    async def session(self):
        session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=90),
            json_serialize=orjson.dumps,  # type: ignore[arg-type]
        )
        
        try:
            yield session
        finally:
            await session.close()
            
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
        async with self.session() as session:
            async with session.put(
                url, headers=self.__headers, data=params.model_dump_json()
            ) as response:
                res: dict[str, Any] = await response.json(
                    content_type=None, loads=orjson.loads
                )

                if response.status >= 400:
                    raise Exception(response.status)

                data = res.get("data")

                if data is None:
                    raise Exception("Data is None")

                return data

    async def delete_tenant(self, tenant: str) -> bool:
        """
        Endpoint to delete a tenant
        Example:

        ```python
        from supavisor.client import Supavisor
        from pydantic import SecretStr

        >>> supavisor = Supavisor(
        ...     supavisor_url="http://localhost:4000",
        ...     supavisor_api_key=SecretStr("secret"),
        ... )
        >>> tenant = "tenant1"

        >>> await supavisor.delete_tenant(tenant)
        True
        """
        url = f"{self.supavisor_url.unicode_string()}/api/tenants/{tenant}"
        async with self.session() as session:
            async with session.delete(url, headers=self.__headers) as response:
                return response.status == 204
            
            
    async def get_tenant(self, tenant: str) -> dict[str, Any]:
        """
        Endpoint to get a tenant
        Example:

        ```python
        from supavisor.client import Supavisor
        from pydantic import SecretStr

        >>> supavisor = Supavisor(
        ...     supavisor_url="http://localhost:4000",
        ...     supavisor_api_key=SecretStr("secret"),
        ... )
        >>> tenant = "tenant1"

        >>> await supavisor.get_tenant(tenant)
        """
        url = f"{self.supavisor_url.unicode_string()}/api/tenants/{tenant}"
        async with self.session() as session:
            async with session.get(url, headers=self.__headers) as response:
                res: dict[str, Any] = await response.json(
                    content_type=None, loads=orjson.loads
                )

                if response.status >= 400:
                    raise Exception(response.status)

                data = res.get("data")

                if data is None:
                    raise Exception("Data is None")

                return data
            
    async def terminate_tenant(self, tenant: str) -> bool:
        """
        Endpoint to terminate a tenant
        Example:

        ```python
        from supavisor.client import Supavisor
        from pydantic import SecretStr

        >>> supavisor = Supavisor(
        ...     supavisor_url="http://localhost:4000",
        ...     supavisor_api_key=SecretStr("secret"),
        ... )
        >>> tenant = "tenant1"

        >>> await supavisor.terminate_tenant(tenant)
        True
        """
        url = f"{self.supavisor_url.unicode_string()}/api/tenants/{tenant}/terminate"
        async with self.session() as session:
            async with session.get(url, headers=self.__headers) as response:
                return response.status == 204