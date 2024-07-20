""" pynchon.plugins.mermaid
    Examples:
        # render and display with imgcat
        pynchon mmd render docs/trifecta.mmd --output - | imgcat
    See also:
        * https://github.com/mermaid-js/mermaid-cli
        * https://mermaid.live/
"""

import os

from fleks import cli, tagging

from pynchon.models.planner import Planner

from pynchon import abcs, events, models  # noqa
from pynchon.util import files, lme, typing  # noqa

LOGGER = lme.get_logger(__name__)


@tagging.tags(click_aliases=["mmd"])
class Mermaid(models.DiagramTool, Planner):
    """
    Finds & renders Mermaid diagram files
    """

    class config_class(abcs.Config):
        config_key: typing.ClassVar[str] = "mermaid"
        apply_hooks: typing.List[str] = typing.Field(
            default=["open-after"], description=""
        )
        output_mode: str = typing.Field(default="png")
        docker_image: str = typing.Field(
            default="ghcr.io/mermaid-js/mermaid-cli/mermaid-cli:10.8.1-beta.15",
            description="",
        )
        docker_args: typing.List = typing.Field(
            default=[],
            description="Array of extra arguments to pass to docker command",
        )
        mermaid_args: typing.List = typing.Field(
            default=[],
            description="Array of extra arguments to pass to mermaid command",
        )

    name = "mermaid"
    cli_name = "mermaid"
    contribute_plan_apply = True

    @tagging.tags(click_aliases=["ls"])
    def list(self):
        """
        Find mermaid diagrams under `{{project_root}}/**/*.mmd`
        """
        includes = "**/*.mmd"
        search = [
            abcs.Path(self.project_root).joinpath(includes),
        ]
        self.logger.debug(f"search pattern is {search}")
        result = files.find_globs(search)
        return result

    apply = Planner.apply

    @cli.click.flag("--imgcat", help="view output with imgcat")
    @cli.click.argument("file", nargs=1)
    def render(
        self,
        img: str = "??",
        file: str = "",
        output: str = "",
        imgcat: bool = False,
    ):
        """
        Renders mermaid diagrams to images using the mermaid docker image.

        Output support includes handling any of these:
          * an explicitly provided output file
          * guess output file from output-mode/input-filename,
          * stdout, via '/dev/stdout' or '-'

        If '--imgcat' is passed, this will preview the result using imgcat.
        """
        # FIXME: move this stuff to shil lib?
        from uuid import uuid4

        import python_on_whales
        from python_on_whales import docker

        from pynchon.util.os import invoke

        special = output in ["-", "/dev/stdout"]
        post_op = ""
        if (not output) or special:
            fname, ext = os.path.splitext(str(file))
            output_mode = self["output_mode"]
            output = f"{fname}.{output_mode}"
            self.logger.warning(f"rendering in-place to {output}")
            if special:
                post_op = f"cat {output}"
        wd = self.working_dir
        file = abcs.Path(file).absolute().relative_to(wd)
        output = abcs.Path(output)
        output = output.absolute().relative_to(wd)
        uid = os.getuid()
        try:
            this_name = f"pynchon.mmd-{uuid4()}"
            self.logger.warning(f"starting mmd container {this_name}")
            mmd_args = " ".join(self["mermaid_args"::[]])
            cmd = f"-i {file} -o {output} {mmd_args}"
            cmd_array = cmd.split()
            dargs = [
                self.config.docker_image,
                cmd_array,
            ]
            dkwargs = dict(
                name=this_name,
                volumes=[(wd, "/workspace")],
                # interactive=True,
                # tty=True,
                workdir="/workspace",
                user=uid,
                detach=True,
            )
            LOGGER.warning("running docker:")
            LOGGER.warning(f"    name: '{this_name}'")
            LOGGER.warning(f"    image: '{self.config.docker_image}'")
            LOGGER.warning(f"    command: '{cmd}' ")
            cid = docker.run(*dargs, **dkwargs)
            stat = None
            import time

            while stat != "exited":
                time.sleep(0.7)
                self.logger.warning(f"polling for {this_name} @ {cid}..")
                try:
                    c = invoke(
                        f"docker ps -a --filter id={cid} --format json | tee /dev/stderr",
                        load_json=True,
                    ).data
                except (IndexError,):
                    pass
                else:
                    stat = c["State"]
                    LOGGER.debug(f"updated status: {stat}")
            # import IPython; IPython.embed()
        except (python_on_whales.exceptions.DockerException,) as exc:
            LOGGER.critical(exc)
            raise SystemExit(1)
        if post_op:
            invoke(post_op, strict=True, system=True)
            return None
        else:
            invoke(
                f"docker logs {cid} > /dev/stderr",
                command_logger=self.logger.warning,
                system=True,
            )
        if imgcat:
            invoke(f"imgcat {output}", system=True)

    @property
    def output_root(self):
        return abcs.Path(self[:"git.root":]) / "img"

    def plan(
        self,
        config=None,
    ) -> models.Plan:
        """Run planning for this plugin"""
        plan = super(self.__class__, self).plan(config=config)
        self.logger.debug("planning for rendering for .mmd mermaid files..")
        output_mode = self["output_mode"]
        for inp in self.list():
            rsrc = inp.parents[0] / inp.stem
            rsrc = f"{rsrc}.{output_mode}"
            plan.append(
                self.goal(
                    resource=rsrc,
                    command=(
                        f"pynchon {self.cli_name} " f"render {inp} --output {rsrc} "
                    ),
                    type="render",
                )
            )
        return plan
