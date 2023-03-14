import re
import time

from auth import Auth, AuthAware
from document import Document


class DocTree(AuthAware):
    _parse_line = re.compile(
        r"""<p class="(rep|doc)">.*<a href=".*(?:download\?id=|\?rep=)(\d+).*<span class="nom">(.*)<\/span><\/a><\/p>"""
    )

    def __init__(self, rep_id=-1, subject="", path=None):
        self.subject: str = subject
        self.path: list[str] = path if path is not None else []
        self.rep_id: int = rep_id
        self.children: list[DocTree] = []
        self.documents: list[Document] = []
        self._populated: bool = False

    def __str__(self) -> str:
        return f"DocTree<{self.subject}>({self.rep_id}, '{'/'.join(self.path)}')"

    def _parse_page(
        self, page: str, query_filenames=True
    ) -> tuple[list["DocTree"], list[Document]]:
        children = []
        documents = []
        for line in page.splitlines():
            line = line.strip()
            if line in (
                "<h3>Documents récents</h3>",
                '<script type="text/javascript">',
            ):
                # Stop before the recent documents or end of page
                break
            match = DocTree._parse_line.match(line)
            if match is None:
                continue

            if match.group(1) == "rep":
                children.append(
                    DocTree(
                        int(match.group(2)), self.subject, self.path + [match.group(3)]
                    )
                )
                print(f"Found child {children[-1]}")
            elif match.group(1) == "doc":
                documents.append(
                    Document(
                        int(match.group(2)),
                        match.group(3) if not query_filenames else None,
                        query_filename=query_filenames,
                    )
                )
                print(f"Found document {documents[-1]}")

        return children, documents

    def explore(self):
        connection = self.request("GET", f"/docs?rep={self.rep_id}")
        response = connection.getresponse()
        if response.status != 200:
            raise Exception("Failed to download document")

        data = response.read().decode("utf-8")
        connection.close()

        children, documents = self._parse_page(data)
        self.children = children
        self.documents = documents
        self._populated = True

        for child in children:
            child.explore()

    def by_path(self, path: list[str]) -> "DocTree":
        if not self._populated:
            raise RuntimeError("Cannot search in unpopulated tree")
        if len(path) == 0:
            return self
        for child in self.children:
            if child.path[-1] == path[0]:
                return child.by_path(path[1:])
        raise FileNotFoundError(f"Path {path} not found in {self}")


class SubjectTree(DocTree):
    def __init__(self, subject: str):
        super().__init__(subject=subject, path=[subject])

    def explore(self):
        connection = self.request("GET", f"/docs?{self.subject}")
        response = connection.getresponse()
        if response.status != 200:
            raise Exception("Failed to download document")

        data = response.read().decode("utf-8")
        connection.close()

        children, documents = self._parse_page(data)
        self.children = children
        self.documents = documents
        self._populated = True

        for child in children:
            child.explore()
