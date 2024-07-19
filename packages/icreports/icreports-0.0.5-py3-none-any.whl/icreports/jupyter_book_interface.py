import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class JupyterBookInterface:

    def __init__(
        self,
        source_dir: Path,
        build_dir: Path | None = None,
        document_name: str = "document",
    ):

        if build_dir:
            self.build_dir = build_dir
        else:
            self.build_dir = Path() / "_build"

        self.source_dir = source_dir
        self.document_name = document_name

    def build_html(self):

        logger.info("Building HTML output")

        cmd = f"jb build --all {self.source_dir}"
        subprocess.run(cmd, shell=True, check=True)

        source_path = self.build_dir / "html"
        named_path = self.build_dir / self.document_name

        shutil.copytree(source_path, named_path)
        shutil.make_archive(self.build_dir / f"{self.document_name}", "zip", named_path)
        shutil.rmtree(named_path)

        logger.info("Finished building HTML output")

    def build_pdf(self):

        logger.info("Building PDF output")

        cmd = f"jb build --all {self.source_dir} --builder pdflatex"
        subprocess.run(cmd, shell=True, check=True)

        source_path = self.build_dir / "latex/book.pdf"
        dst_path = self.build_dir / f"{self.document_name}.pdf"
        shutil.move(source_path, dst_path)

        logger.info("Finished building PDF output")
