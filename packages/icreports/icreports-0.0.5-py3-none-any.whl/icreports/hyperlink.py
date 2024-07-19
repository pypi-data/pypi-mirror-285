from pathlib import Path


class Hyperlink:
    def __init__(self, link: str) -> None:
        self.link = link

    def resolve(self, root: Path):
        resolved_link = self.link
        if resolved_link.startswith("/"):
            resolved_link = resolved_link.lstrip("/")
        elif resolved_link.startswith("."):
            resolved_link = str(root) + resolved_link[1:]
        else:
            resolved_link = str(root) + "/" + resolved_link
        return resolved_link

    def is_local(self):
        if not self.link.endswith(".md"):
            return False
        return not (self.link.startswith("http") or self.link.startswith("#"))

    def wikify(self):
        if self.is_local() and not self.link.endswith("index.md"):
            return self.link.split("/")[-1]
        else:
            return self.link
