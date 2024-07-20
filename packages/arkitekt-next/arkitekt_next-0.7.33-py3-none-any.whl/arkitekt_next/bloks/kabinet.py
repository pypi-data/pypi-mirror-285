from typing import Dict, Any
import secrets

from blok import blok, InitContext, ExecutionContext
from blok.tree import Repo, YamlFile


@blok("live.arkitekt.kabinet")
class KabinetBlok:
    def __init__(self) -> None:
        self.host = "kabinet"
        self.command = "bash run-debug.sh"
        self.repo = "https://github.com/jhnnsrs/kabinet-server"
        self.scopes = {"read_image": "Read image from the database"}
        self.mount_repo = True
        self.build_repo = True
        self.secret_key = secrets.token_hex(16)
        self.ensured_repos = []

    def get_dependencies(self):
        return [
            "live.arkitekt.gateway",
            "live.arkitekt.postgres",
            "live.arkitekt.lok",
            "live.arkitekt.admin",
            "live.arkitekt.redis",
            "live.arkitekt.s3",
        ]

    def init(self, init: InitContext):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

        deps = init.dependencies

        deps["live.arkitekt.lok"].register_scopes(self.scopes)

        self.gateway_access = deps["live.arkitekt.gateway"].expose(
            self.host, 80, self.host
        )

        self.postgress_access = deps["live.arkitekt.postgres"].register_db(self.host)
        self.redis_access = deps["live.arkitekt.redis"].register()
        self.lok_access = deps["live.arkitekt.lok"].retrieve_credentials()
        self.admin_access = deps["live.arkitekt.admin"].retrieve()
        self.minio_access = deps["live.arkitekt.s3"].retrieve_credentials(["media"])
        self.initialized = True

    def build(self, context: ExecutionContext):
        depends_on = []

        if self.redis_access.dependency:
            depends_on.append(self.redis_access.dependency)

        if self.postgress_access.dependency:
            depends_on.append(self.postgress_access.dependency)

        db_service = {
            "labels": [
                "fakts.service=live.arkitekt.mikro",
                "fakts.builder=arkitekt.mikro",
            ],
            "depends_on": depends_on,
        }

        if self.mount_repo:
            context.file_tree.set_nested("mounts", self.host, Repo(self.repo))
            db_service["volumes"] = [f"./mounts/{self.host}:/workspace"]

        if self.build_repo:
            context.file_tree.set_nested("mounts", self.host, Repo(self.repo))
            db_service["build"] = f"./mounts/{self.host}"

        db_service["command"] = self.command

        configuration = YamlFile(
            **{
                "db": self.postgress_access.dict(),
                "django": {
                    "admin": self.admin_access.dict(),
                    "debug": True,
                    "hosts": ["*"],
                    "secret_key": self.secret_key,
                },
                "redis": self.redis_access.dict(),
                "lok": self.lok_access.dict(),
                "s3": self.minio_access.dict(),
                "scopes": self.scopes,
            }
        )

        context.file_tree.set_nested("configs", "kabinet.yaml", configuration)

        context.docker_compose.set_nested("services", self.host, db_service)

    def get_options(self):
        with_repo = CLIOptions(
            subcommand="with_repo",
            help="Which repo should we use when building the service? Only active if build_repo or mount_repo is active",
            default=self.repo,
        )
        with_command = CLIOptions(
            subcommand="command",
            help="Which command should be run when starting the service",
            default=self.command,
        )
        mount_repo = CLIOptions(
            subcommand="mount_repo",
            help="Should we mount the repo into the container?",
            is_flag=True,
            default=True,
        )
        build_repo = CLIOptions(
            subcommand="build_repo",
            help="Should we build the container from the repo?",
            is_flag=True,
            default=True,
        )
        with_host = CLIOptions(
            subcommand="host",
            help="How should the service be named inside the docker-compose file?",
            default=self.host,
        )
        with_secret_key = CLIOptions(
            subcommand="secret_key",
            help="The secret key to use for the django service",
            default=self.secret_key,
        )
        with_repos = CLIOptions(
            subcommand="repos",
            help="The default repos to enable for the service",
            default=self.secret_key,
        )

        return [
            with_repo,
            mount_repo,
            build_repo,
            with_host,
            with_command,
            with_secret_key,
            with_repos,
        ]
