""" pynchon.plugins.makefile
"""

from fleks import cli, tagging

from pynchon.util.makefile import parse as makefile_parse

from pynchon import abcs, api, events, models  # noqa
from pynchon.util import lme, typing  # noqa

LOGGER = lme.get_logger(__name__)


class Make(models.Planner):
    """Visualization and parsing tools for inspecting Makefiles"""

    class config_class(abcs.Config):
        config_key: typing.ClassVar[str] = "makefile"
        file: str = typing.Field(default=None)

        @property
        def file(self):
            # from pynchon.config import project
            tmp = abcs.Path(".").absolute()
            return tmp / "Makefile"

    priority = 6  # before mermaid
    name = "makefile"
    cli_name = "makefile"
    cli_label = "Project Tools"

    def _get_template_file(self, relpath: str = ""):
        tfile = self.plugin_templates_root / relpath
        return api.render.get_template(str(tfile))

    @property
    def diagrams_root(self):
        return abcs.Path(self[:"docs.root":]) / "diagrams"

    @property
    def output_file(self):
        default = self.diagrams_root / "Makefile.mmd"
        return self["output_file"::default]

    def plan(self):
        """Runs a plan for this plugin"""
        plan = super(self.__class__, self).plan()
        input_file = self["file"]
        diagram_title = (
            abcs.Path(self["diagram_title"::input_file])
            .absolute()
            .relative_to(abcs.Path(".").absolute())
        )
        output_file = self.output_file
        if not self.diagrams_root.exists():
            plan.append(
                self.goal(
                    resource=self.diagrams_root,
                    type="mkdir",
                    command=f"mkdir {self.diagrams_root}",
                )
            )
        plan.append(
            self.goal(
                resource=output_file,
                type="render",
                command=f"pynchon makefile render mermaid --title {diagram_title} --output {output_file} {input_file} ",
            )
        )
        return plan

    @cli.click.group
    def render(self):
        """Subcommands for rendering"""

    @render.command("mermaid")
    @cli.click.option("--title", help="diagram title", default="Makefile Targets")
    @cli.click.option(
        "--template",
        help="mermaid template to use",
        default="mermaid-graph.mmd.j2",
    )
    @cli.options.output
    @cli.click.argument("makefile", default="Makefile")
    def _render_mermaid(
        self, output: str = "", makefile: str = "", title: str = "", template: str = ""
    ):
        """Renders mermaid diagram for makefile targets"""
        tmpl = self._get_template_file(template)
        LOGGER.warning("writing to file: {output}")
        if output in ["-", "/dev/stdout", ""]:
            import sys

            fhandle = sys.stdout
        else:
            fhandle = open(output, "w")
        print(
            api.render.clean_whitespace(
                tmpl.render(
                    **dict(
                        title=title,
                        parsed=self.parse(makefile=makefile),
                    )
                )
            ),
            file=fhandle,
        )

    @tagging.tags(click_aliases=["parse.makefile"])
    @cli.click.flag(
        "--graph", "-g", "only_graph", help="Returns only the prerequisites-graph"
    )
    @cli.click.flag(
        "--include-private",
        "-p",
        "include_private",
        help="Includes 'private' targets that start with '.'",
    )
    @cli.click.flag(
        "--module-docs",
        help="Module docs only",
    )
    @cli.click.flag(
        "--markdown",
        help="Enrich docs with markdown",
    )
    @cli.click.option(
        "--target",
        help="Retrieve help for named target only",
    )
    # @cli.click.option(
    #     "--lookup",
    #     help="Retrieves best-guess for the relevant help, where lookup might be a target, or a target namespace, etc",
    #     default="",
    # )
    @cli.click.argument(
        "makefile",
        default="",
        required=False,
    )
    def parse(
        self,
        makefile: str = "",
        target: str = "",
        # lookup: str = "",
        only_graph: bool = False,
        include_private: bool = False,
        module_docs: bool = False,
        markdown: bool = False,
    ):
        """Parse Makefile to JSON.  Includes DAGs for targets, target-body, and target-type details"""
        makefile = makefile or self.config["file"]
        from collections import OrderedDict

        out = makefile_parse(
            makefile=makefile,
            target=target,
            # lookup=lookup,
            module_docs=module_docs,
            markdown=markdown,
            include_private=include_private,
        )
        out = (
            OrderedDict(sorted([k, v] for k, v in out.items()))
            if isinstance(out, (dict,))
            else out
        )
        if only_graph:
            out = {t: out[t]["prereqs"] for t in out}
        return out
