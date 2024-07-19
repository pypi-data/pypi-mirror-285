# Supavisor Library README

## Overview

The Supavisor library is a Python client for interacting with the Supavisor API. It simplifies the process of managing tenants on a Supavisor server, including adding, deleting, retrieving, and terminating tenants.

## Features

- **Add Tenant:** Easily add new tenants with specified parameters.
- **Delete Tenant:** Remove tenants from the Supavisor server.
- **Get Tenant:** Retrieve information about existing tenants.
- **Terminate Tenant:** Terminate tenant sessions.

## Installation

To install the Supavisor library, you can use pip:

```bash
pip install supavisor
```

## Getting Started

### Prerequisites

- Python 3.7 or higher
- An active Supavisor server instance
- Supavisor API key

### Initialization

First, import the necessary modules and initialize the Supavisor client:

```python
from supavisor.client import Supavisor
from pydantic import SecretStr

supavisor = Supavisor(
    supavisor_url="http://your-supavisor-url",
    supavisor_api_key=SecretStr("your-api-key"),
)
```

### Add Tenant

To add a tenant, you need to specify the tenant name and parameters:

```python
from supavisor.types import AddTenantParams, TenantParams, TenantUser

tenant = "tenant1"

params = AddTenantParams(
    tenant=TenantParams(
        db_database=tenant,
        db_host="your-db-host",
        db_port=your-db-port,
        enforce_ssl=False,
        require_user=True,
        users=[
            TenantUser(db_user="user", db_password="password")
        ],
    )
)

await supavisor.add_tenant(tenant, params)
```

### Delete Tenant

To delete a tenant, simply call the `delete_tenant` method with the tenant name:

```python
tenant = "tenant1"
await supavisor.delete_tenant(tenant)
```

### Get Tenant

To retrieve information about a tenant, use the `get_tenant` method:

```python
tenant = "tenant1"
tenant_info = await supavisor.get_tenant(tenant)
print(tenant_info)
```

### Terminate Tenant

To terminate a tenant session, call the `terminate_tenant` method with the tenant name:

```python
tenant = "tenant1"
await supavisor.terminate_tenant(tenant)
```

## Benefits

- **Ease of Use:** Simplifies interactions with the Supavisor API using Python.
- **Asynchronous Support:** Utilizes aiohttp for efficient asynchronous HTTP requests.
- **JSON Serialization:** Uses orjson for fast and efficient JSON serialization.
- **Type Safety:** Leverages Pydantic for data validation and type checking.

## API Reference

### `Supavisor` Class

#### `__init__(supavisor_url: HttpUrl, supavisor_api_key: SecretStr)`

- Initializes the Supavisor client with the base URL and API key.

#### `session()`

- Creates an asynchronous context manager for aiohttp sessions.

#### `add_tenant(tenant: str, params: AddTenantParams) -> dict[str, Any]`

- Adds a new tenant with the specified parameters.

#### `delete_tenant(tenant: str) -> bool`

- Deletes the specified tenant.

#### `get_tenant(tenant: str) -> dict[str, Any]`

- Retrieves information about the specified tenant.

#### `terminate_tenant(tenant: str) -> bool`

- Terminates the session of the specified tenant.

## Example Usage

Here is an example of how to use the Supavisor library to add, get, delete, and terminate a tenant:

```python
from supavisor.client import Supavisor
from supavisor.types import AddTenantParams, TenantParams, TenantUser
from pydantic import SecretStr

supavisor = Supavisor(
    supavisor_url="http://your-supavisor-url",
    supavisor_api_key=SecretStr("your-api-key"),
)

tenant = "tenant1"

params = AddTenantParams(
    tenant=TenantParams(
        db_database=tenant,
        db_host="your-db-host",
        db_port=your-db-port,
        enforce_ssl=False,
        require_user=True,
        users=[
            TenantUser(db_user="user", db_password="password")
        ],
    )
)

# Add Tenant
await supavisor.add_tenant(tenant, params)

# Get Tenant
tenant_info = await supavisor.get_tenant(tenant)
print(tenant_info)

# Delete Tenant
await supavisor.delete_tenant(tenant)

# Terminate Tenant
await supavisor.terminate_tenant(tenant)
```

## Conclusion

The Supavisor library provides a convenient and efficient way to manage tenants on a Supavisor server. With its asynchronous support and type-safe approach, it is an excellent choice for developers looking to integrate Supavisor functionality into their Python applications.