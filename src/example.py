from doctree import SubjectTree, DocTree
from document import Document
from auth import Auth
import os


def dump_subject(subject: str, path: str, auth: bool = True):
    tree = SubjectTree(subject)
    tree.explore()

    for child in tree.children:
        # Create a directory for the child
        child_path = os.path.join(path, *child.path)

        # Create the directory if it doesn't exist
        if not os.path.exists(child_path):
            print(child_path)
            os.makedirs(child_path)

        for doc in child.documents:
            doc.save(child_path)


if __name__ == "__main__":
    Auth().authenticate("username", "password")
    dump_subject("maths", ".")
