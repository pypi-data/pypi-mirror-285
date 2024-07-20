""" pynchon.plugins.compose
"""

from fleks import cli

from fleks.util import tagging  # noqa

from pynchon import abcs, events, models  # noqa
from pynchon.util import lme, typing  # noqa

LOGGER = lme.get_logger(__name__)


class Compose(models.DockerWrapper, models.Planner):
    """
    Wrapper around docker-compose
    """

    class config_class(models.DockerWrapper.BaseConfig):
        config_key: typing.ClassVar[str] = "compose"
        compose_args: typing.List = typing.Field(default=[])
        # docker_image: str = typing.Field(default="pandoc/extra:latest")
        goals: typing.List[typing.Dict] = typing.Field(default=[], help="")

    name = "compose"
    cli_name = "compose"
    # cli_label = "Docs Tools"
    # contribute_plan_apply = False

    @cli.click.command(
        context_settings=dict(
            ignore_unknown_options=True,
            allow_extra_args=True,
        )
    )
    def run(self, *args, **kwargs):
        # command = self._get_docker_command(self.command_extra)
        raise Exception(locals())
        # command = self._get_docker_command_base(
        #     self.command_extra,
        #     # docker_args='-it',
        #     entrypoint="pdflatex",
        # )
        # LOGGER.warning(command)
        # result = self._run_docker(command)
        # result = self.apply(plan=super().plan(
        #     goals=[
        #         self.goal(
        #             type="?",
        #             # resource=kwargs.get("output", kwargs.get("o", None)),
        #             command=command,
        #         )
        #     ]
        # ))
        # if result.ok:
        #     raise SystemExit(0)
        # else:
        #     LOGGER.critical(f"Action failed: {result.actions[0].dict()}")
        #     raise SystemExit(1)

    # @cli.click.argument("file")
    # @cli.click.option('--output', help='output file', default='')
    # # @tagging.tags(click_aliases=["markdown.to-pdf"])
    # def md_to_pdf(
    #     self,
    #     file: str = None,
    #     output: str = '',
    # ):
    #     """
    #     Converts markdown files to PDF with pandoc
    #     """
    #     output = abcs.Path(output or f"{abcs.Path(file).stem}.pdf")
    #     docker_image = self['docker_image']
    #     docker_args = ' '.join(self['docker_args'] or [])
    #     cmd = f"docker run -v `pwd`:/workspace -w /workspace {docker_image} {file} {docker_args} -o {output}"
    #     plan = super().plan(
    #         goals=[
    #             self.goal(resource=output.absolute(),
    #             type="render", command=cmd)]
    #     )
    #     return self.apply(plan=plan,fail_fast=True)
