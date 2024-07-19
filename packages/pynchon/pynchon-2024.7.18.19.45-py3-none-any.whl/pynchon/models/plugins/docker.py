""" pynchon.models.plugins.docker
"""

from pynchon import abcs
from pynchon.cli import click
from pynchon.util.os import invoke

from .tool import ToolPlugin

from pynchon.util import lme, typing  # noqa

from . import validators  # noqa

LOGGER = lme.get_logger("DOCKER")

import sys


class DockerWrapper(ToolPlugin):
    """
    Wrappers for dockerized tools
    """

    class BaseConfig(abcs.Config):
        docker_image: str = typing.Field(
            default="docker/hello-world", description="docker container to use"
        )
        docker_args: typing.List = typing.Field(
            default=[], description="Array of arguments to pass to docker command"
        )

    cli_label = "Docker Wrappers"
    cli_description = "Plugins that wrap invocations on containers"
    contribute_plan_apply = False
    priority = 2
    __class_validators__ = [
        validators.require_conf_key,
    ]

    @property
    def command_extra(self):
        name = self.click_group.name
        try:
            index = sys.argv.index(name) + 2
        except (ValueError,) as exc:
            index = 0
        command = sys.argv[index + 2 :]
        return " ".join(command)

    def _get_docker_command_base(self, *args, **kwargs):
        docker_image = kwargs.pop("docker_image", self["docker_image"])
        docker_args = kwargs.pop("docker_args", [])
        docker_args = (
            " ".join(docker_args)
            + " "
            + " ".join(f'--{k}="{v}"' for k, v in kwargs.items())
        )
        return (
            "docker run -v `pwd`:/workspace -w /workspace "
            f"{docker_args} {docker_image} {' '.join(args)}"
        )

    def _stop_container(self, name: str = "", strict=True):
        if name:
            filtered = invoke(f'docker ps -q -f "name={name}"')
            if filtered.succeeded:
                did = filtered.stdout.strip()
                if did:
                    return invoke(f"docker stop {did}", strict=True).succeeded
                else:
                    LOGGER.warning(f"could not find container: name={name}")
                    return False
            else:
                LOGGER.warning(f"failed to find container: name={name}")
                if strict:
                    raise SystemExit(filtered.stderr)
                else:
                    return False

    def _get_docker_command(self, *args, **kwargs):
        """ """
        cmd_t = self._get_docker_command_base(" ".join(args))
        dargs = self["docker_args"] or []
        docker_args = " ".join(dargs)
        zip_kws = " ".join(["{k}={v}" for k, v in kwargs.items()])
        cmd_t += f" {docker_args} {zip_kws}"
        return cmd_t

    @click.command(
        context_settings=dict(
            ignore_unknown_options=True,
            allow_extra_args=True,
        )
    )
    def run(self, *args, **kwargs):
        """Passes given command through to docker-image this plugin wraps"""
        # raise Exception('bonk')
        command = self._get_docker_command(self.command_extra)
        LOGGER.warning(command)
        plan = super().plan(
            goals=[
                self.goal(
                    type="render",
                    resource=kwargs.get("output", kwargs.get("o", "")),
                    command=command,
                )
            ]
        )
        result = self.apply(plan=plan)
        if result.ok:
            raise SystemExit(0)
        else:
            LOGGER.critical(f"Action failed: {result.actions[0].error}")
            raise SystemExit(1)

    def _run_docker(self, cmd, **kwargs):
        """ """
        LOGGER.critical(cmd)
        result = invoke(cmd, **kwargs)
        LOGGER.warning(result.stdout)
        return result


class DockerComposeWrapper(DockerWrapper):
    class config_class(DockerWrapper.BaseConfig):
        service_name: str = typing.Field(
            default="service_name", description="compose service name to use"
        )
        compose_args: typing.List = typing.Field(
            default=[], description="Array of arguments to pass to docker command"
        )


class DiagramTool(DockerWrapper):
    cli_label = "Diagramming Tools"
    cli_description = "View and render technical diagrams from source, in several formats.  (Usually these require docker, but no other system dependencies.)"
