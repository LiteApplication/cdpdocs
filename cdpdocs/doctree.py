import re
import time

from .auth import Auth, AuthAware
from .document import Document


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
        self._folders_recursive = True

    def __str__(self) -> str:
        return f"DocTree<{self.subject}>({self.rep_id}, '{'/'.join(self.path)}')"

    def _parse_page(
        self, page: str, query_filenames=True, skip_folders=False, skip_files=None
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
                if skip_folders:
                    continue
                children.append(
                    DocTree(
                        int(match.group(2)), self.subject, self.path + [match.group(3)]
                    )
                )
                print(f"Found child {children[-1]}")
            elif match.group(1) == "doc":
                if skip_files is not None and int(match.group(2)) in skip_files:
                    print("Skipped file", match.group(3))
                    continue
                documents.append(
                    Document(
                        int(match.group(2)),
                        match.group(3) if not query_filenames else None,
                        query_filename=query_filenames,
                    )
                )
                print(f"Found document {documents[-1]}")

        return children, documents

    def explore(self, query_filenames=True, skip_files=None):
        connection = self.request("GET", f"/docs?rep={self.rep_id}")
        response = connection.getresponse()
        if response.status != 200:
            raise Exception("Failed to download document")

        data = response.read().decode("utf-8")
        connection.close()

        children, documents = self._parse_page(
            data, query_filenames, skip_files=skip_files
        )
        self.children = children
        self.documents = documents
        self._populated = True

        if not self._folders_recursive:
            return  # Do not explore children if we are not in recursive mode

        for child in children:
            child.explore(query_filenames=query_filenames, skip_files=skip_files)

    def by_path(self, path: list[str]) -> "DocTree":
        if not self._populated:
            raise RuntimeError("Cannot search in unpopulated tree")
        if len(path) == 0:
            return self
        for child in self.children:
            if child.path[-1] == path[0]:
                return child.by_path(path[1:])
        raise FileNotFoundError(f"Path {path} not found in {self}")

    def iter_documents(self):
        if not self._populated and not self._folders_recursive:
            raise RuntimeError("Cannot iterate in unpopulated tree")
        for document in self.documents:
            yield document
        if not self._folders_recursive:
            return
        for child in self.children:
            yield from child.iter_documents()

    def iter_children(self):
        if not self._populated:
            raise RuntimeError("Cannot iterate in unpopulated tree")
        for child in self.children:
            yield child
            if not self._folders_recursive:
                continue
            yield from child.iter_children()

    def doc_matches(self, path: list[str]) -> bool:
        if not self._populated:
            raise RuntimeError("Cannot search in unpopulated tree")
        if len(path) == 0:  # Empty path matches nothing
            return False
        if (
            len(path) == 1
        ):  # If we are in the right folder, check if the document is here
            for document in self.documents:
                if document.match(path[0]):
                    return True
            return False
        try:
            by_path = self.by_path(path[:-1])  # Go to the right folder
        except FileNotFoundError:
            return False
        return by_path.doc_matches([path[-1]])  # Check if the document is here


class SubjectTree(DocTree):
    def __init__(self, subject: str):
        super().__init__(subject=subject, path=[subject])

    def explore(self, query_filenames=True, use_folders=None, skip_files=None):
        if use_folders is None:
            print("Exploring", self.subject, "...")

            connection = self.request("GET", f"/docs?{self.subject}")
            response = connection.getresponse()
            if response.status != 200:
                raise Exception("Failed to download document")

            data = response.read().decode("utf-8")
            connection.close()

            children, documents = self._parse_page(
                data, query_filenames, skip_folders=False, skip_files=skip_files
            )
            self.children = children
            self.documents = documents
            self._populated = True

            for child in children:
                child.explore(query_filenames=query_filenames, skip_files=skip_files)
        else:
            print("Exploring", self.subject, "with", len(use_folders), "folders ...")
            self._folders_recursive = False
            for folder, path in use_folders.items():
                self.children.append(
                    DocTree(rep_id=folder, subject=self.subject, path=path)
                )
            for child in self.children:
                connection = self.request("GET", f"/docs?rep={child.rep_id}")
                response = connection.getresponse()
                if response.status != 200:
                    raise Exception("Failed to download document")

                data = response.read().decode("utf-8")
                connection.close()

                _, documents = self._parse_page(
                    data, query_filenames, skip_folders=True, skip_files=skip_files
                )
                self.documents = documents
                self._populated = True
