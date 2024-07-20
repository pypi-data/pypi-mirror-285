from blok import blok, InitContext, ExecutionContext, CLIOption
from blok.tree import YamlFile, Repo
from pydantic import BaseModel
from typing import Dict, Any

from blok import blok, InitContext


DEFAULT_PUBLIC_URLS = ["127.0.0.1"]
DEFAULT_PUBLIC_HOSTS = ["localhost"]


class ExposedHost(BaseModel):
    host: str
    port: int
    stip_prefix: bool = True


class ExposedPort(BaseModel):
    port: int
    host: str
    tls: bool = False


@blok("live.arkitekt.gateway")
class GatewayBlok:
    def __init__(self) -> None:
        self.exposed_hosts = {}
        self.http_expose_default = None
        self.exposed_ports = {}
        self.with_certer = True
        self.with_tailscale = True
        self.http_port = 80
        self.https_port = 443

    def get_identifier(self):
        return "live.arkitekt.gateway"

    def get_dependencies(self):
        return []

    def init(self, init: InitContext):
        for key, value in init.kwargs.items():
            setattr(self, key, value)

    def build(self, context: ExecutionContext):
        caddyfile = """
{
    auto_https off
}
        """

        for key, port in self.exposed_ports.items():
            if port.tls:
                caddyfile += f"""
:{port.port} {{
    tls /certs/caddy.crt /certs/caddy.key
    reverse_proxy {port.host}:{port.port}
}}
                """
            else:
                caddyfile += f"""
:{port.port} {{
    reverse_proxy {port.host}:{port.port}
}}
                """

        caddyfile += """
https:// {
    tls /certs/caddy.crt /certs/caddy.key

    header {
        -Server
        X-Forwarded-Proto {scheme}
        X-Forwarded-For {remote}
        X-Forwarded-Port {server_port}
        X-Forwarded-Host {host}
    }
        """

        for path_name, exposed_host in self.exposed_hosts.items():
            if exposed_host.stip_prefix:
                caddyfile += f"""
    @{path_name} path /{path_name} {{
        uri strip_prefix /{path_name}
        reverse_proxy {exposed_host.host}:{exposed_host.port}
    }}
                """
            else:
                caddyfile += f"""
    @{path_name} path /{path_name}{{
        reverse_proxy {exposed_host.host}:{exposed_host.port}
    }}
                """

        caddyfile += """
}
        """

        context.file_tree.set_nested("config", "Caddyfile", caddyfile)

        caddy_depends_on = []
        if self.with_certer:
            caddy_depends_on.append("certer")

        caddy_container = {
            "image": "caddy:latest",
            "volumes": ["./config/Caddyfile:/etc/caddy/Caddyfile"],
            "ports": [f"{self.http_port}:80", f"{self.https_port}:443"],
            "depends_on": caddy_depends_on,
        }

        context.docker_compose.set_nested("services", "caddy", caddy_container)

        if self.with_certer:
            context.file_tree.set_nested("certs", {})
            caddy_container = {
                "image": "jhnnsrs/certer:latest",
                "volumes": ["./certs:/certs"],
                "ports": [f"{self.http_port}:80", f"{self.https_port}:443"],
                "depends_on": caddy_depends_on,
            }

    def expose(self, path_name: str, port: int, host: str, strip_prefix: bool = True):
        self.exposed_hosts[path_name] = ExposedHost(
            host=host, port=port, stip_prefix=strip_prefix
        )

    def expose_default(self, port: int, host: str):
        self.http_expose_default = ExposedHost(host=host, port=port, stip_prefix=False)

    def expose_port(self, port: int, host: str, tls: bool = False):
        self.exposed_ports[port] = ExposedPort(port=port, host=host, tls=tls)

    def get_options(self):
        with_public_urls = CLIOption(
            subcommand="public_url",
            help="Which public urls to use",
            type=str,
            multiple=True,
            default=DEFAULT_PUBLIC_URLS,
            show_default=True,
        )
        with_public_services = CLIOption(
            subcommand="public_hosts",
            help="Which public hosts to use",
            type=str,
            multiple=True,
            default=DEFAULT_PUBLIC_HOSTS,
            show_default=True,
        )

        return [with_public_urls, with_public_services]
