from pathlib import Path
from markdown_it import MarkdownIt
from mdformat.renderer import MDRenderer
from bs4 import BeautifulSoup

from .hyperlink import Hyperlink


def _md_it_wikify_link(self, tokens, idx, options, env):
    if "href" in tokens[idx].attrs:
        link = Hyperlink(tokens[idx].attrs["href"])
        tokens[idx].attrSet("href", link.wikify())
    return self.renderToken(tokens, idx, options, env)


class Page:

    def __init__(self):
        pass


class MarkdownPage(Page):
    def __init__(self, doc_root: Path, file_path: Path) -> None:
        super().__init__()

        self.doc_root = doc_root
        self.file_path = file_path
        self.md_src = None
        self.md = None
        self.html = None
        self.soup = None
        self.links: list = []
        self.load()

    def get_full_path(self):
        return self.doc_root / self.file_path

    def load(self):
        with open(self.get_full_path(), "r") as f:
            self.md_src = f.read()

        self.md = MarkdownIt()
        self.render_html()

    def _wikify_link(self, token):
        if token.type != "link_open":
            return
        if "href" in token.attrs:
            link = Hyperlink(token.attrs["href"])
            token.attrSet("href", link.wikify())

    def _visit_token(self, token, func):
        if token.children is not None:
            for child in token.children:
                self._visit_token(child, func)
        else:
            func(token)

    def wikify_links(self):
        tokens = self.md.parse(self.md_src)

        # self.md.add_renderer_rule("link_open", _md_it_wikify_link)
        for token in tokens:
            self._visit_token(token, self._wikify_link)

        md_renderer = MDRenderer()
        options = {}
        env = {}
        self.md_src = md_renderer.render(tokens, options, env)

    def render_html(self):
        self.html = self.md.render(self.md_src)

        self.soup = BeautifulSoup(self.html, features="html.parser")
        self.links = self.soup.find_all("a", href=True)
