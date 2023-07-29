#!/usr/bin/env python3

import os
import sys


del sys.path[0]  # Remove the current directory from the path

from cdpdocs.auth import Auth, set_class_name
from cdpdocs.doctree import SubjectTree


def dump_subject(subject: str, path: str):
    tree = SubjectTree(subject)
    tree.explore(query_filenames=False)

    os.makedirs(os.path.join(path, subject), exist_ok=True)

    for doc in tree.iter_documents():
        child_path = os.path.join(path, *doc.parent.path)
        if not os.path.exists(child_path):
            os.makedirs(child_path)
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
