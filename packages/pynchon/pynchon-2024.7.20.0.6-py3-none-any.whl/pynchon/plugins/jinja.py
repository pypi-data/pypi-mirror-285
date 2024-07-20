""" pynchon.plugins.jinja
"""

from fleks import tagging

from pynchon import abcs, api, cli

from pynchon.util import files, lme, text, typing  # noqa

LOGGER = lme.get_logger(__name__)

from pynchon.models.planner import RenderingPlugin  # noqa


@tagging.tags(click_aliases=["j"])
class Jinja(RenderingPlugin):
    """Renders files with {jinja.template_includes}"""

    # FIXME: diff-rendering with something like this:
    #   diff --color --minimal -w --side-by-side fname <(bash --pretty-print fname )

    class config_class(abcs.Config):
        config_key: typing.ClassVar[str] = "jinja"
        file_glob: str = typing.Field(
            default="*.j2", description="Where to find jinja templates"
        )
        template_includes: typing.List[str] = typing.Field(
            default=[],
            description="Where to find files for use with Jinja's `include` blocks",
        )
        exclude_patterns: typing.List[str] = typing.Field(
            description="File patterns to exclude from resource-listing"
        )
        vars: typing.Dict[str, str] = typing.Field(
            default={}, description="Extra variables for template rendering"
        )

        @property
        def exclude_patterns(self):
            "File patterns to exclude from resource-listing"
            from pynchon.config import globals

            global_ex = globals.exclude_patterns
            my_ex = self.__dict__.get("exclude_patterns", [])
            return list(set(global_ex + my_ex + ["**/pynchon/templates/includes/**"]))

    name = "jinja"
    priority = 7
    COMMAND_TEMPLATE = (
        "python -mpynchon.util.text render jinja "
        "{src} --context-file {context_file} "
        # "{print} "
        "--output {output} {template_args}"
    )

    def _get_jinja_context(self, extra_jinja_vars: dict = {}):
        """
        creates the jinja context file which will be used with rendering.

        context is derived from the entire current pynchon config,
        see `pynchon cfg`, which is the static contents of `.pynchon.json5`
        plus whatever dynamic data is provided by other plugins.  the
        contents of `extra_jinja_vars` is merged-with-overrides into
        `{{jinja.vars}}`.

        FIXME: this is cached, but beware, that basically happens per-process.
        """
        if getattr(self, "_jinja_ctx_file", None):
            return self._jinja_ctx_file
        else:
            if isinstance(extra_jinja_vars, (list, tuple)):
                tmp = []
                for ejv in extra_jinja_vars:
                    ejv = ejv.split("=")
                    k = ejv.pop(0)
                    v = "=".join(ejv)
                    tmp.append([k, v])
                extra_jinja_vars = dict(tmp)
            data = self.project_config.dict()
            data["jinja"]["vars"].update(extra_jinja_vars)
            fname = ".tmp.jinja.ctx.json"
            with open(fname, "w") as fhandle:
                fhandle.write(text.to_json(data))
            self._jinja_ctx_file = fname
            return fname

    @property
    def _include_folders(self):
        includes = self.project_config.jinja["template_includes"]
        from pynchon import api

        includes = api.render.get_jinja_includes(*includes)
        return includes

    @cli.click.flag("--local")
    def list_includes(
        self,
        local: bool = False,
    ):
        """Lists full path of each include-file"""
        includes = self._include_folders
        if local:
            includes.remove(api.render.PYNCHON_CORE_INCLUDES)
        includes = [abcs.Path(t) / "**" / self.config.file_glob for t in includes]
        LOGGER.warning(includes)
        matches = files.find_globs(includes)
        return matches

    @cli.click.flag("--local")
    def list_include_args(
        self,
        local: bool = False,
    ):
        """
        Lists all usable {% include ... %} values
        """
        includes = self.list_includes(local=local)
        out = []
        for fname in includes:
            fname = abcs.Path(fname)
            for inc in self._include_folders:
                try:
                    fname = fname.relative_to(inc)
                except ValueError:
                    continue
                else:
                    out.append(fname)
                break
            else:
                pass
        return out

    @tagging.tags(click_aliases=["ls"])
    def list(self, changes=False, **kwargs):
        """
        Lists affected resources for this project
        """
        return self._list(changes=changes, **kwargs)

    def list_filters(self, **kwargs) -> typing.Dict[str, str]:
        """
        Lists filters available for the jinja environments
        """
        self.logger.critical("not implemented yet")
        return dict()

    # FIXME: only supports in-place rendering
    @cli.click.option("-o", "--output", default="")
    @cli.click.flag(
        "-p",
        "--print",
        "should_print",
        default=False,
    )
    @cli.options.extra_jinja_vars
    @cli.click.argument("files", nargs=-1)
    def render(
        self,
        files,
        output: str = "",
        should_print: bool = False,
        plan_only: bool = False,
        extra_jinja_vars: list = [],
    ):
        """
        Renders 1 or more jinja templates
        """
        files = [abcs.Path(file) for file in files]
        jctx = self._get_jinja_context(extra_jinja_vars=extra_jinja_vars)
        templates = self._get_template_args()
        plan = super(self.__class__, self).plan()
        if output:
            assert len(files) == 1
        for src in files:
            assert src.exists()
            output = output or str(src).replace(".j2", "")
            if output == str(src):
                if not should_print:
                    raise RuntimeError("filename did not change!")
                    # raise SystemExit(1)
                else:
                    output = "/dev/stdout"
            plan.append(
                self.goal(
                    type="render",
                    resource=output,
                    command=self.COMMAND_TEMPLATE.format(
                        src=src,
                        # print='' if not should_print else '--print',
                        context_file=jctx,
                        template_args=templates,
                        output=output,
                    ),
                )
            )
        if plan_only:
            return plan
        else:
            result = plan.apply(strict=True, fail_fast=True)
            if should_print:
                for action in result:
                    if action.ok:
                        with open(action.resource) as fhandle:
                            if action.resource.endswith(".md"):
                                try:
                                    printer = self.siblings["markdown"]
                                except (KeyError,):
                                    self.logger.critical(
                                        f"the `markdown` plugin is required for previewing {action.resource}"
                                    )
                                else:
                                    printer = printer.preview
                                data = [action.resource]
                                # from pynchon.util import lme
                                # from rich.markdown import Markdown
                                # printer = lme.print
                                # data = Markdown(fhandle.read())
                            else:
                                printer = print
                                data = fhandle.read()
                            printer(data)
                return None
                # import IPython; IPython.embed()
            return result

    def _get_template_args(self):
        """ """
        templates = self["template_includes"]
        templates = [t for t in templates]
        templates = [f"--include {t}" for t in templates]
        templates = " ".join(templates)
        return templates

    @cli.options.extra_jinja_vars
    def plan(
        self,
        config=None,
        extra_jinja_vars: list = [],
    ) -> typing.List:
        """Creates a plan for this plugin"""
        plan = super(self.__class__, self).plan()
        jctx = self._get_jinja_context(extra_jinja_vars=extra_jinja_vars)
        templates = self._get_template_args()
        for src in self.list():
            output = str(src).replace(".j2", "")
            plan.append(
                self.goal(
                    type="render",
                    resource=output,
                    command=self.COMMAND_TEMPLATE.format(
                        # print='',
                        src=src,
                        context_file=jctx,
                        template_args=templates,
                        output=output,
                    ),
                )
            )
        return plan.finalize()

    # allows `pynchon jinja apply --var ...`,
    # which can then be passed-through to `pynchon jinja plan`
    apply = cli.extends_super(
        RenderingPlugin, "apply", extra_options=[cli.options.extra_jinja_vars]
    )
