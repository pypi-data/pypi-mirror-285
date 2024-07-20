import click

from pydantic import BaseModel
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from typing import Dict
import yaml
import secrets

from blok import blok, InitContext, ExecutionContext, CLIOption
from blok.tree import YamlFile, Repo
from blok import blok, InitContext


DEFAULT_ARKITEKT_URL = "http://localhost:8000"


class LokCredentials(BaseModel):
    issuer: str
    key_type: str
    public_key: str


# Define a custom user type that will parse and validate the user input
class UserParamType(click.ParamType):
    name = "user"

    def convert(self, value, param, ctx):
        if isinstance(value, dict):
            return value
        try:
            name, password = value.split(":")
            return {"name": name, "password": password}
        except ValueError:
            self.fail(
                f"User '{value}' is not in the correct format. It should be 'name:password'.",
                param,
                ctx,
            )


USER = UserParamType()


# Define a custom user type that will parse and validate the user input
class GroupParamType(click.ParamType):
    name = "group"

    def convert(self, value, param, ctx):
        if isinstance(value, dict):
            return value
        try:
            name, description = value.split(":")
            return {"name": name, "description": description}
        except ValueError:
            self.fail(
                f"User '{value}' is not in the correct format. It should be 'name:password'.",
                param,
                ctx,
            )


GROUP = GroupParamType()


class RedeemTokenParamType(click.ParamType):
    name = "redeem_token"

    def convert(self, value, param, ctx):
        if isinstance(value, dict):
            assert "user" in value, f"scope is required {value}"
            assert "token" in value, f"description is required {value}"
            return value

        try:
            user, token = value.split(":")
            return {"user": user, "token": token}
        except ValueError:
            self.fail(
                f"RedeemToken '{value}' is not in the correct format. It should be 'username:token'.",
                param,
                ctx,
            )


TOKEN = RedeemTokenParamType()


class ScopeParamType(click.ParamType):
    name = "scope"

    def convert(self, value, param, ctx):
        if isinstance(value, dict):
            assert "scope" in value, f"scope is required {value}"
            assert "description" in value, f"description is required {value}"
            return value

        try:
            name, description = value.split(":")
            return {"scope": name, "description": description}
        except ValueError:
            self.fail(
                f"Scopes '{value}' is not in the correct format. It should be 'scope:description'.",
                param,
                ctx,
            )


SCOPE = ScopeParamType()


@blok("live.arkitekt.lok")
class LokBlok:
    db_name: str

    def __init__(self) -> None:
        self.db_name = "lok_db"
        self.mount_repo = False
        self.build_repo = False
        self.private_key = None
        self.public_key = None
        self.host = "lok"
        self.with_repo = False
        self.command = "bash run-debug.sh"
        self.repo = "https://github.com/jhnnsrs/lok-server-next"
        self.users = []
        self.tokens = []
        self.groups = []
        self.secret_key = secrets.token_hex(16)
        self.scopes = {"hallo": "welt"}
        self.key = None

    def get_dependencies(self):
        return [
            "live.arkitekt.postgres",
            "live.arkitekt.redis",
            "live.arkitekt.admin",
            "live.arkitekt.gateway",
        ]

    def retrieve_credentials(self) -> LokCredentials:
        return LokCredentials(
            public_key=self.public_key, key_type="RS256", issuer="lok"
        )

    def register_scopes(self, scopes_dict: Dict[str, str]) -> LokCredentials:
        self.scopes = self.scopes | scopes_dict

    def init(self, init: InitContext):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

        assert self.public_key, "Public key is required"
        assert self.private_key, "Private key is required"

        kwargs = init.kwargs
        deps = init.dependencies
        scopes = kwargs.get("scopes", [])
        self.scopes = {scope["scope"]: scope["description"] for scope in scopes}

        self.postgress_access = deps["live.arkitekt.postgres"].register_db(self.host)
        self.redis_access = deps["live.arkitekt.redis"].register()
        self.admin_access = deps["live.arkitekt.admin"].retrieve()
        self.initialized = True

    def build(self, context: ExecutionContext):
        depends_on = []

        if self.redis_access.dependency:
            depends_on.append(self.redis_access.dependency)

        if self.postgress_access.dependency:
            depends_on.append(self.postgress_access.dependency)

        db_service = {
            "labels": ["fakts.service=live.arkitekt.lok", "fakts.builder=arkitekt.lok"],
            "depends_on": depends_on,
        }

        if self.mount_repo:
            context.file_tree.set_nested("mounts", "lok", Repo(self.repo))
            db_service["volumes"] = ["./mounts/lok:/lok"]

        if self.build_repo:
            context.file_tree.set_nested("mounts", "lok", Repo(self.repo))
            db_service["build"] = "./mounts/lok"

        db_service["command"] = self.command

        configuration = YamlFile(
            **{
                "db": self.postgress_access.dict(),
                "users": [user for user in self.users],
                "django": {
                    "admin": self.admin_access.dict(),
                    "debug": True,
                    "hosts": ["*"],
                    "secret_key": self.secret_key,
                },
                "redis": self.redis_access.dict(),
                "lok": self.retrieve_credentials().dict(),
                "private_key": self.private_key,
                "public_key": self.public_key,
                "scopes": self.scopes,
                "redeem_tokens": [token for token in self.tokens],
                "groups": [group for group in self.groups],
            }
        )

        context.file_tree.set_nested("configs", "lok.yaml", configuration)

        context.docker_compose.set_nested("services", self.host, db_service)

    def get_options(self):
        key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=crypto_default_backend()
        )

        private_key = key.private_bytes(
            crypto_serialization.Encoding.PEM,
            crypto_serialization.PrivateFormat.PKCS8,
            crypto_serialization.NoEncryption(),
        ).decode()

        public_key = (
            key.public_key()
            .public_bytes(
                crypto_serialization.Encoding.OpenSSH,
                crypto_serialization.PublicFormat.OpenSSH,
            )
            .decode()
        )

        with_fakts_url = CLIOption(
            subcommand="db_name",
            help="The fakts url for connection",
            default="db_name",
        )
        with_users = CLIOption(
            subcommand="users",
            help="The fakts url for connection",
            default=["admin:admin"],
            multiple=True,
            type=USER,
        )
        with_groups = CLIOption(
            subcommand="groups",
            help="The fakts url for connection",
            default=["admin:admin_group"],
            multiple=True,
            type=GROUP,
        )
        with_redeem_token = CLIOption(
            subcommand="tokens",
            help="The fakts url for connection",
            default=[],
            multiple=True,
            type=TOKEN,
        )
        with_scopes = CLIOption(
            subcommand="scopes",
            help="The scopes",
            default=[f"{key}:{value}" for key, value in self.scopes.items()],
            multiple=True,
            type=SCOPE,
        )
        with_repo = CLIOption(
            subcommand="with_repo",
            help="The fakts url for connection",
            default=self.repo,
        )
        with_repo = CLIOption(
            subcommand="command",
            help="The fakts url for connection",
            default=self.command,
        )
        mount_repo = CLIOption(
            subcommand="mount_repo",
            help="The fakts url for connection",
            is_flag=True,
            default=False,
        )
        build_repo = CLIOption(
            subcommand="build_repo",
            help="The fakts url for connection",
            is_flag=True,
            default=False,
        )
        with_host = CLIOption(
            subcommand="host",
            help="The fakts url for connection",
            default=self.host,
        )
        #
        with_public_key = CLIOption(
            subcommand="public_key",
            help="The fakts url for connection",
            default=public_key,
            required=True,
            callback=validate_public_key,
        )
        with_private_key = CLIOption(
            subcommand="private_key",
            help="The fakts url for connection",
            default=private_key,
            callback=validate_private_key,
            required=True,
        )
        with_secret_key = CLIOption(
            subcommand="secret_key",
            help="The fakts url for connection",
            default=self.secret_key,
        )

        return [
            with_fakts_url,
            with_users,
            with_repo,
            mount_repo,
            with_groups,
            build_repo,
            with_host,
            with_redeem_token,
            with_private_key,
            with_public_key,
            with_scopes,
            with_secret_key,
        ]


def validate_public_key(ctx, param, value):
    if not value.startswith("ssh-rsa"):
        raise click.BadParameter(
            f"Public key must be in ssh-rsa format. Started with {value}"
        )
    return value


def validate_private_key(ctx, param, value):
    if not value.startswith("-----BEGIN PRIVATE KEY-----"):
        raise click.BadParameter(
            f"Private key must be in PEM format. Started with {value}"
        )
    return value
