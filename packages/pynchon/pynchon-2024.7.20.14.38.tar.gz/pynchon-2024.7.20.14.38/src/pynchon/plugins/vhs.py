""" pynchon.plugins.vhs
"""

from fleks import cli, tagging

from pynchon import abcs, api, events, models  # noqa
from pynchon.util import lme, typing  # noqa

LOGGER = lme.get_logger(__name__)


@tagging.tags(click_aliases=["v"])
class Vhs(models.Planner):
    """
    Finds and renders .tape files with vhs
    """

    class config_class(abcs.Config):
        config_key: typing.ClassVar[str] = "vhs"
        file: str = typing.Field(default=None)
        file_glob: str = typing.Field(default="*.tape")
        vhs_command: str = typing.Field(default="vhs")
        # @property
        # def file(self):
        #     # from pynchon.config import project
        #     tmp = abcs.Path(".").absolute()
        #     return tmp / "vhs"

    priority = 6
    name = "vhs"
    cli_name = "vhs"
    cli_label = "Project Tools"

    @property
    def docs_root(self):
        return abcs.Path(self[:"docs.root":])

    @tagging.tags(click_aliases=["ls"])
    @cli.click.flag("--raw", "-r", help="raw output (default is json)")
    def list(self, changes=False, raw=False, **kwargs):
        """
        Lists affected resources for this project
        """
        out = self._list(changes=changes, **kwargs)
        if raw:
            out = "\n".join(map(str, out))
            print(out)
        else:
            return out

    COMMAND_TEMPLATE = "vhs {src}"

    def plan(self):
        """Runs a plan for this plugin"""
        plan = super(self.__class__, self).plan()
        for src in self.list():
            plan.append(
                self.goal(
                    type="render",
                    resource="?",
                    command=self.COMMAND_TEMPLATE.format(src=src),
                )
            )
        return plan.finalize()

    # # allows `pynchon jinja apply --var ...`,
    # # which can then be passed-through to `pynchon jinja plan`
    # apply = cli.extends_super(
    #     RenderingPlugin, "apply", extra_options=[cli.options.extra_jinja_vars]
    # )
