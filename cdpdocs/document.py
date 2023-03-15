import os

from .auth import AuthAware

BUFFER_SIZE = 1024 * 1024


class Document(AuthAware):
    def __init__(self, document_id, filename=None, query_filename=True):
        self.document_id = document_id

        self._queried_filename = None
        if filename is None and query_filename:
            self.filename = self.query_filename()
        if filename is None and self.filename is None:
            # Failed to query filename or not asked to
            self.filename = f"document_{document_id}.pdf"
        elif filename is not None:
            self.filename = filename

    def query_filename(self, response=None) -> str:
        if self._queried_filename is not None:
            return self._queried_filename

        should_close = response is None
        if response is None:
            connection = self.request("GET", f"/download?id={self.document_id}")
            response = connection.getresponse()
            if response.status != 200:
                print("Failed to query filename")
                return None

        filename = response.getheader("Content-Disposition")
        if filename is not None:
            # Convert to utf-8
            filename = filename.encode("latin-1").decode("utf-8")
            filename = filename.split("=")[1].strip('"')
            self._queried_filename = filename

        if should_close:
            connection.close()
        return filename

    def save(self, path, save_as=None):
        connection = self.request("GET", f"/download?id={self.document_id}")
        response = connection.getresponse()
        if response.status != 200:
            raise Exception("Failed to download document")

        if save_as is None:
            # Get the filename from the response headers
            filename = self.query_filename(response)
            if filename is None:
                filename = f"document_{self.document_id}.pdf"
        else:
            filename = save_as

        with open(os.path.join(path, filename), "wb") as f:
            # Read the response in chunks
            while True:
                data = response.read(amt=BUFFER_SIZE)
                if not data:
                    break
                f.write(data)
        connection.close()

    def __str__(self) -> str:
        if self.filename is not None:
            return f"Document({self.document_id}, '{self.filename}')"
        return f"Document({self.document_id})"
