#!/usr/bin/env python3

import os

from auth import Auth, set_class_name
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
    import sys

    if len(sys.argv) <= 4:
        print(
            f"Usage: {sys.argv[0]} username password classname subject [subjects ...]"
        )
        exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    classname = sys.argv[3]

    set_class_name(classname)
    Auth().authenticate(username, password)

    dump_subjects(sys.argv[4:], ".")
