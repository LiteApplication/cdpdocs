import os

from auth import Auth
from doctree import SubjectTree


def dump_subject(subject: str, path: str):
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


def dump_subjects(subjects: list[str], path: str):
    for subject in subjects:
        dump_subject(subject, path)


if __name__ == "__main__":
    Auth().authenticate("username", "password")
    dump_subjects(["maths", "info"], ".")
