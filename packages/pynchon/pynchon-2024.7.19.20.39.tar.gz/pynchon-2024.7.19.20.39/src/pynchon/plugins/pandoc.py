""" pynchon.plugins.pandoc
"""

from fleks import cli

from fleks.util import tagging  # noqa

from pynchon import abcs, events, models  # noqa
from pynchon.util import lme, typing  # noqa

LOGGER = lme.get_logger(__name__)


class Pandoc(models.DockerComposeWrapper, models.Planner):
    """
    Wrapper around `pandoc` docker image
    """

    class config_class(models.DockerWrapper.BaseConfig):
        config_key: typing.ClassVar[str] = "pandoc"
        docker_args: typing.List = typing.Field(
            default=["--toc", "--variable fontsize=10pt"]
        )
        docker_image: str = typing.Field(default="pandoc/extra:latest")
        goals: typing.List[typing.Dict] = typing.Field(default=[], help="")
        service_name: str = typing.Field(default="pandoc")

    name = "pandoc"
    cli_name = "pandoc"
    cli_label = "Docs Tools"
    # contribute_plan_apply = False

    @cli.click.command(
        context_settings=dict(
            ignore_unknown_options=True,
            allow_extra_args=True,
        )
    )
    def pdflatex(self, *args, **kwargs):
        command = self._get_docker_command_base(
            self.command_extra,
            # docker_args='-it',
            entrypoint="pdflatex",
        )
        LOGGER.warning(command)
        result = self._run_docker(command)

    def shell(self):
        """Starts interactive shell for pandoc container"""
        command = ""
        command = self._get_docker_command_base(docker_args=["-it"], entrypoint="sh")
        LOGGER.warning(command)
        result = self.apply(
            plan=super().plan(
                goals=[
                    self.goal(
                        type="interactive",
                        command=command,
                    )
                ]
            )
        )
        if result.ok:
            raise SystemExit(0)
        else:
            LOGGER.critical(f"Action failed: {result.actions[0].error}")
            raise SystemExit(1)

    @cli.click.argument("file")
    @cli.click.option("--output", help="output file", default="")
    @tagging.tags(click_aliases=["markdown.to-pdf"])
    def md_to_pdf(
        self,
        file: str = None,
        output: str = "",
    ):
        """
        Converts markdown files to PDF with pandoc
        """
        output = abcs.Path(output or f"{abcs.Path(file).stem}.pdf")
        docker_image = self["docker_image"]
        docker_args = " ".join(self["docker_args"] or [])
        cmd = f"docker compose run {self.config.service_name} {file} {docker_args} -o {output}"
        plan = super().plan(
            goals=[self.goal(resource=output.absolute(), type="render", command=cmd)]
        )
        return self.apply(plan=plan, fail_fast=True, strict=True)
