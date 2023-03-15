# CDPDocs
Document downloader for cahier-de-prepa.fr

# Usage
```python
from cdpdocs.auth import Auth, set_class_name
from cdpdocs.doctree import SubjectTree

# Authenticate using username and password
set_class_name("myclass")
auth = Auth()
auth.authenticate("username", "password")

# Authenticate using a json file
auth = Auth(from_file="credentials.json")
# credentials.json : 
# { "username": "myusername", "password": "password1234"

# Get a subject tree
maths = SubjectTree("maths")

# Explore the tree
maths.explore()

# List all documents
def list_docs_recursive(doctree):
    for doc in doctree.documents:
        print(doc)
    for child in doctree.children:
        list_docs_recursive(child)

list_docs_recursive(maths)

# Download a document
maths.children[0].documents[0].download() # Assuming the first child of maths has at least one document 
```
    
You need to edit the `src/cdpdocs/auth.py` file to change the `CLASS_NAME` variable to match your class's name on cahier-de-prepa.fr.

