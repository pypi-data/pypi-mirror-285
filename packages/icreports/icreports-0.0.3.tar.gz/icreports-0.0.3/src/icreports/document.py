import logging
from pathlib import Path

from iccore.yaml_utils import read_yaml
from icplot.tex_interface import TexInterface

from .page import MarkdownPage
from .link_validator import LinkValidator
from .jupyter_book_interface import JupyterBookInterface

logger = logging.getLogger(__name__)


class Document:

    def __init__(self):
        pass


class Book(Document):
    def __init__(
        self,
        root: Path,
        config_path: Path | None = None,
        config: dict = {},
        version: str = "",
    ) -> None:
        super().__init__()

        self.root = root
        self.content_dir = self.root / "src"
        self.media_dir = self.content_dir / "media"
        self.link_validator = LinkValidator()
        self.config = config
        self.pages: list = []

        if config_path:
            self.config = read_yaml(config_path)
        elif not config:
            self.config = read_yaml(root / "_config.yml")

        if "project_name" in self.config:
            self.name = self.config["project_name"]
        else:
            self.name = "book"

        if version:
            self.version = version
        elif "version" in self.config:
            self.version = self.config["version"]
        else:
            self.version = "0.0.0"

        self.tex_interface = TexInterface(None, None)
        self.build_interface = JupyterBookInterface(self.root, document_name=self.name)

    def validate(self):
        logger.info(f"Looking for pages in {self.content_dir}")
        self._load_pages(self.content_dir)
        logger.info(f"Found {len(self.pages)} pages")

        self.link_validator.validate_links(self.pages)

    def _load_pages(self, path: Path):
        for direntry in path.iterdir():
            if direntry.is_file() and direntry.suffix == ".md":
                relative_path = direntry.relative_to(self.root)
                self.pages.append(MarkdownPage(self.root, relative_path))
            elif direntry.is_dir():
                self._load_pages(direntry)

    def wikify_links(self):
        for page in self.pages:
            page.wikify_links()

    def set_version(self):
        logging.info("Version is: %s", self.version)

    def publish(self, build_dir: Path):

        build_dir = build_dir.resolve()

        logger.info("Starting document checks")
        self.validate()
        logger.info("Finished document checks")

        # Generate any dynamic content, e.g. tex files
        if self.media_dir.exists():
            logger.info("Start generating dynamic content")
            self.tex_interface.build_dir = build_dir
            self.tex_interface.output_dir = build_dir / "media"
            self.tex_interface.build(self.media_dir)
            logger.info("Finish generating dynamic content")

        logger.info("Start generating published output")
        self.build_interface.build_dir = build_dir
        self.build_interface.build_html()
        self.build_interface.build_pdf()
        logger.info("Finished generating published output")
