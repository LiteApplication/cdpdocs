from cdpdocs.auth import Auth, set_class_name
from cdpdocs.doctree import SubjectTree
import os

# Authenticate using username and password
set_class_name("mpi-pv")
auth = Auth(from_file="credentials.json")

SUBJECTS = ["maths", "info", "LV1", "general"]
BASE = "cdp-dump"

for subject in SUBJECTS:
    # Get a subject tree
    tree = SubjectTree(subject)
    tree.explore(query_filenames=False)

    # Download all documents and keep the same structure
    os.makedirs(os.path.join(BASE, subject), exist_ok=True)

    def download_docs_recursive(node, path):
        for doc in node.documents:
            doc.save(path)
            print(f"Downloaded {doc.filename} to {path}")
        for child in node.children:
            os.makedirs(os.path.join(path, child.path[-1]), exist_ok=True)
            download_docs_recursive(child, os.path.join(path, child.path[-1]))

    download_docs_recursive(tree, os.path.join(BASE, subject))
