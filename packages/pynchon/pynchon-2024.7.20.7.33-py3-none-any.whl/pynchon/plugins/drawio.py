""" pynchon.plugins.drawio

    A Wrapper for docker-containers that
    provide the "drawio" diagramming utility

    Live Cloud Version:
        https://app.diagrams.net/
    Local Server:
        https://hub.docker.com/r/jgraph/drawio
        https://www.drawio.com/blog/diagrams-docker-app
    CLI Tools:
        https://github.com/rlespinasse/docker-drawio-desktop-headless
"""

import webbrowser

from fleks import tagging

from pynchon import abcs, api, cli, events, models  # noqa
from pynchon.util import files, lme, text, typing  # noqa

LOGGER = lme.get_logger(__name__)

ElementList = typing.List[typing.Dict]
DEFAULT_HTTP_PORT = 8080
DEFAULT_DOCKER_NAME = "drawio-server"


@tagging.tags(click_aliases=["draw"])
class DrawIO(models.DiagramTool, models.Planner):
    """
    Wrapper for docker-containers that
    provide the "drawio" diagramming utility
    """

    class config_class(abcs.Config):
        config_key: typing.ClassVar[str] = "drawio"
        file_glob: str = typing.Field(
            default="*.drawio", description="Where to find jinja templates"
        )

        docker_image: str = typing.Field(
            default="jgraph/drawio", help="Docker image to use"
        )
        http_port: str = typing.Field(help="Port to use", default=DEFAULT_HTTP_PORT)
        docker_args: typing.List = typing.Field(
            default=[f"--rm --name={DEFAULT_DOCKER_NAME}"],
            help="Docker args to use",
        )
        export_docker_image: str = typing.Field(
            default="rlespinasse/drawio-desktop-headless"
        )
        format: str = typing.Field(help="", default="png")
        export_width: int = typing.Field(help="", default=800)
        export_args: typing.List = typing.Field(
            help="",
            default=[
                "--export",
                "--border 10",
                "--crop",
                # "--zoom",
                "--transparent",
                # "--embed-svg-images",
                # "--embed-diagram",
                # "--svg-theme light",
            ],
        )

    name = "drawio"
    cli_name = "drawio"
    priority = 0
    contribute_plan_apply = True

    @tagging.tags(click_aliases=["ls"])
    def list(self, changes=False, **kwargs):
        """
        Lists affected resources (*.drawio files) for this project
        """
        return self._list(changes=changes, **kwargs)

    def plan(
        self,
        config=None,
    ) -> typing.List:
        """Creates a plan for this plugin"""
        plan = super(self.__class__, self).plan()
        for src in self.list():
            plan.append(
                self.goal(
                    type="render",
                    resource=src,
                    command=f"pynchon drawio render {src}",
                )
            )
        return plan.finalize()

    @cli.click.argument("output", required=False)
    @cli.click.argument("input")
    def render(
        self,
        input,
        output=None,
    ):
        """
        Exports a given .drawio file to some
        output file/format (default format is SVG)
        """
        format = self.config["format"]
        assert input.endswith(".drawio") or input.endswith(
            ".xml"
        ), "Expected an xml or drawio file as input"
        output = output or ".".join(
            list(filter(None, input.split(".")[:-1])) + [format]
        )
        export_args = " ".join(self.config.export_args)
        # export_args += f" --width {self.config.export_width} --height 600"
        export_docker_args = "-w /workspace -v `pwd`:/workspace"
        result = self._run_docker(
            (
                f"docker run {export_docker_args} {self.config.export_docker_image} "
                f"{export_args} --output {output} {input}"
            ),
            strict=True,
        )
        print(result.stdout if result.succeeded else result)
        raise SystemExit(0 if result.succeeded else 1)

    export = render

    def stop(self):
        """Stop DrawIO server"""
        return self._stop_container(name=DEFAULT_DOCKER_NAME)

    @cli.click.option(
        "--background", "-b", help="Run in background", is_flag=True, default=False
    )
    def serve(self, background: bool = False):
        """
        Runs the drawio-UI in a docker-container
        """
        port = self.config.http_port
        dargs = " ".join(self.config.docker_args)
        dimg = self.config.docker_image
        if background:
            background = "&"
            dargs = dargs  # f'-it {dargs}'
        else:
            dargs = f"-it {dargs}"
            background = ""
        cmd_t = f"docker run {dargs} -p {port}:{port} {dimg} {background}"
        return self._run_docker(cmd_t, strict=True, interactive=True)

    def open(self, *args, **kwargs):
        """
        Opens a browser for the container started by `serve`
        """
        return webbrowser.open(
            f"http://localhost:{self.config.http_port}/?offline=1&https=0"
        )
