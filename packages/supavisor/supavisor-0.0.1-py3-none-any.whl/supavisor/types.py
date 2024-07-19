import enum

from pydantic import BaseModel, Field, PositiveInt


class ModeType(str, enum.Enum):
    session = "session"
    transaction = "transaction"


class TenantUser(BaseModel):
    db_password: str = Field(
        description="Database password",
    )
    db_user: str = Field(
        description="Database user",
    )
    max_clients: PositiveInt = Field(
        default=25000,
        description="Max clients",
    )
    mode_type: ModeType = Field(
        default=ModeType.session,
        description="Mode type",
    )
    pool_checkout_timeout: PositiveInt = Field(
        default=1000,
        description="Pool checkout timeout",
    )
    pool_size: PositiveInt = Field(
        default=10,
        description="Pool size",
    )


class TenantParams(BaseModel):
    allow_list: list[str] = Field(
        default=["0.0.0.0/0", "::/0"],
        description="List of allowed IP addresses",
    )
    db_database: str = Field(
        description="Database name",
    )
    db_host: str = Field(
        description="Database host",
    )
    db_port: int = Field(
        default=5432,
        description="Database port",
    )
    enforce_ssl: bool = Field(
        default=False,
        description="Enforce SSL",
    )
    upstream_tls_ca: str | None = Field(
        default=None,
        description="Upstream TLS CA",
    )
    ip_version: str = Field(
        default="auto",
        description="IP version",
    )
    require_user: bool = Field(
        default=True,
        description="Require user",
    )
    auth_query: str | None = Field(
        default=None,
        description="SELECT rolname, rolpassword FROM pg_authid WHERE rolname=$1;",
    )
    default_max_clients: PositiveInt = Field(
        default=200,
        description="Default max clients",
    )
    default_pool_size: PositiveInt = Field(
        default=10,
        description="Default pool size",
    )
    users: list[TenantUser] = Field(
        default_factory=list,
        description="List of users",
    )


class AddTenantParams(BaseModel):
    tenant: TenantParams
