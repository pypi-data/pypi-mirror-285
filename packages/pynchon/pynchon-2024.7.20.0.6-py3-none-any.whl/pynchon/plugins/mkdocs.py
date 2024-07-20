""" pynchon.plugins.mkdocs
"""

import os
import urllib
import webbrowser
import urllib.parse
from pathlib import Path

import yaml
import fleks
from fleks import tagging

from pynchon.plugins import util as plugin_util
from pynchon.util.text import loadf

from pynchon import abcs, api, events, models  # noqa
from pynchon.util import lme, typing  # noqa

LOGGER = lme.get_logger(__name__)
DEFAULT_LOG_FILE = ".tmp.mkdocs.log"


class MkdocsPage(fleks.config.Config):
    config_key: typing.ClassVar[str] = "mkdocs.pages"
    title: str = typing.Field()
    path: typing.Union[abcs.Path, str] = typing.Field()
    relative_url: str = typing.Field()
    rel_path: str = typing.Field()
    tags: typing.List[str] = typing.Field(
        default=[], help="only used by mkdocs_blogging plugin"
    )
    draft: bool = typing.Field(default=False)
    exclude_from_blog: bool = typing.Field(
        default=False, help="only used by mkdocs_blogging plugin"
    )
    description: str = typing.Field(default="")


class MkdocsPluginConfig(abcs.Config):
    config_key: typing.ClassVar[str] = "mkdocs"
    config_file: str = typing.Field(default=None)

    @property
    def tags(self) -> typing.List:
        """ """
        tags = set()
        for p in self.pages:
            tags = tags.union(set(p.tags))
        # NB: removes empty-string
        return sorted(list(filter(None, tags)))

    @property
    def drafts(self) -> typing.List:
        ignore_list = ["index.md", "tags.md", "nav.md"]
        return [
            p
            for p in self.pages
            if all([p["draft"], p["path"].name not in ignore_list])
        ]

    @property
    def pages(self) -> typing.List:
        """ """
        from mkdocs.config.defaults import MkDocsConfig
        from mkdocs.structure.files import File
        from mkdocs.structure.pages import Page

        pages = []
        mconf = self.config
        if mconf:
            ddir = abcs.Path(mconf.get("docs_dir", "docs"))

            cfg = MkDocsConfig()
            data = yaml.load(open(self.config_file).read(), yaml.FullLoader)
            cfg.load_dict(data)
            cfg.validate()  # fl = File(
            pfiles = ddir.glob("**/*.md")
            for pfile in pfiles:
                rel_pfile = pfile.relative_to(ddir)
                mfile = File(
                    str(rel_pfile), cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls
                )
                pg = Page(
                    file=mfile,
                    config=cfg,
                    title=None,
                )
                pg.read_source(cfg)
                pmeta_d = dict(
                    title=pg.meta.pop("title", pg.title),
                    # relative_url=pg.url,
                    relative_url=f"{self.site_relative_url}/{pg.url}",
                    path=pfile.absolute(),
                    rel_path=str(rel_pfile),
                    tags=pg.meta.pop("tags", []),
                    draft=any([pg.meta.pop("draft", False), "draft" in str(rel_pfile)]),
                    **pg.meta,  # **dict(pg.title)},
                )
                pmeta = MkdocsPage(**pmeta_d)
                pages.append(pmeta)
        return pages

    @property
    def blog_posts(self) -> typing.List:
        """
        returns blog posts, iff blogging plugin is installed.
        resulting files, if any, will not include index and
        will be sorted by modification time
        """
        ignore_list = ["index.md", "tags.md", "nav.md"]
        return [
            p
            for p in self.pages
            if all([not p["draft"], p["path"].name not in ignore_list])
        ]

    @property
    def site_relative_url(self) -> str:
        """ """
        site_url = self.config["site_url"] if "site_url" in self.config else None
        if site_url:
            return urllib.parse.urlparse(site_url).path

    @property
    def config(self) -> typing.Dict:
        """
        returns a dictionary with the current mkdocs configuration
        """
        fname = self.config_file
        if fname is None:
            return {}

        return loadf.yaml(fname)

    @property
    def config_file(self) -> typing.StringMaybe:
        """returns the path to the mkdocs config-file, if applicable"""
        docs = plugin_util.get_plugin("docs", strict=False)
        docs = docs and docs.get_current_config()
        subproject = plugin_util.get_plugin("subproject", strict=False)
        subproject = subproject and subproject.get_current_config()
        project = plugin_util.get_plugin("project", strict=False)
        project = project and project.get_current_config()
        candidates = filter(
            None,
            [
                abcs.Path(".").absolute(),
                docs and docs.root,
                subproject and subproject.root,
                project and project.root,
            ],
        )
        for folder in [Path(c) for c in candidates]:
            cand = folder / "mkdocs.yml"
            if cand.exists():
                return str(cand.absolute())


class Mkdocs(models.Planner):
    """Mkdocs helper"""

    priority = 8  # before mermaid
    name = "mkdocs"
    cli_name = "mkdocs"
    cli_label = "Docs Tools"
    config_class = MkdocsPluginConfig

    @property
    def config_file(self) -> str:
        return self["config_file"]

    def serve(self, background: bool = True):
        """
        Wrapper for `mkdocs serve`
        """
        from pynchon.util.os import invoke

        bg = "&" if background else ""
        cmd = f"mkdocs serve --config-file {self.config_file} >> {DEFAULT_LOG_FILE} 2>&1 {bg}"
        result = invoke(cmd)
        return result

    @tagging.tags(click_aliases=["ls"])
    def list(self) -> typing.List:
        """Lists site-pages based on mkdocs.yml"""
        return self.config.pages

    @fleks.cli.click.argument("files", nargs=-1)
    def open(
        self,
        files: tuple = tuple(),
    ) -> bool:
        """
        Opens `dev_addr` in a webbrowser
        """
        if not files:
            file = "."
        else:
            file = files[0] if files else "."
        mconfig = self.config.config
        default_path = urllib.parse.urlparse(mconfig["site_url"]).path
        default_path = (
            default_path[1:] if default_path.startswith("/") else default_path
        )
        default_path = default_path[:-1] if default_path.endswith("/") else default_path
        docs_dir = Path(mconfig["docs_dir"]).absolute()
        LOGGER.warning(f"opening {file}")
        if file.startswith("/"):
            LOGGER.warning("file is absolute..")
            relf = Path(file[1:])
            relf_on_docs = Path(mconfig["docs_dir"]) / relf
            file = relf_on_docs / relf
            file = file.absolute().relative_to(docs_dir)
        else:
            LOGGER.warning("file is relative..")
            file = Path(file).absolute().relative_to(docs_dir)
        file, ext = os.path.splitext(str(file))
        file = file if ext == ".md" else "".join([file, ext])
        url = mconfig["dev_addr"]
        url = f"{url}/{default_path}" if default_path else url
        url = f"{url}/{file}" if file else url
        url = f"http://{url}" if not url.startswith("http") else url
        url = url.replace("/blog/", "/#blog/")
        self.logger.warning(f"opening {url}")
        return webbrowser.open(url)

    @property
    def site_dir(self) -> str:
        """
        Returns mkdocs `site_dir` if present in config, or guesses what it should be
        """
        plugin_cfg = self.config
        mkdocs_config = plugin_cfg.config
        result = str(mkdocs_config.get("site_dir", self.working_dir / "site"))
        self.logger.warning(f"returning {result}")
        return result

    def plan(self):
        """
        Runs a plan for this plugin
        """
        plan = super(self.__class__, self).plan()
        command = f"mkdocs build --config-file {self.config_file}"
        plan.append(
            self.goal(
                type="render",
                resource=self.site_dir,
                command=command,
            )
        )
        return plan
