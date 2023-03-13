import http.client as httplib
import json
from urllib.request import getproxies

CDP_SERVER = "cahier-de-prepa.fr"
CLASS_NAME = "mp2i-pv"
SKIP_PROXY = False


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Auth(metaclass=Singleton):
    def __init__(self, from_file=None):
        self.cookie = None

        if from_file is not None:
            with open(from_file, "r") as f:
                json_data = json.load(f)
                username = json_data["username"]
                password = json_data["password"]
                try:
                    self.authenticate(username, password)
                except Exception as e:
                    print("Error while authenticating from file: \n\t", e)
                    raise e
        AuthAware.request = self.request
        AuthAware._has_auth = True

    def authenticate(self, username, password):
        request_body = f"login={username}&motdepasse={password}&permconn=0&connexion=1"
        try:
            connection = self.request(
                "POST",
                f"/ajax.php",
                body=request_body,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Referer": f"https://{CDP_SERVER}/{CLASS_NAME}/docs",
                },
            )
        except Exception as e:
            print("Error while authenticating:", e)
            raise e

        response = connection.getresponse()
        if response.status != 200:
            raise Exception(
                "Authentication failed : status code " + str(response.status)
            )

        # Check that the authentication was successful
        data = response.read().decode("utf-8")
        result = json.loads(data)
        connection.close()
        if result.get("etat", "nok") != "ok":
            raise Exception("Authentication failed : '" + result["message"] + "'")

        # Extract the cookies from the response
        cookies = response.getheader("Set-Cookie")
        if cookies is None:
            raise Exception("Authentication failed : No cookies header")

        cookies = cookies.split(",")
        cdp_session = ""
        cdp_session_perm = ""
        for cookie in cookies:
            for parts in cookie.split(";"):
                parts = parts.strip()
                if parts.startswith("CDP_SESSION="):
                    cdp_session = parts
                if parts.startswith("CDP_SESSION_PERM="):
                    cdp_session_perm = parts
        if cdp_session == "" or cdp_session_perm == "":
            raise Exception("Authentication failed : missing cookies")

        # Craft the cookie header
        self.cookie = cdp_session + "; " + cdp_session_perm

        return data

    def request(self, method, path, body=None, headers=None) -> httplib.HTTPSConnection:
        if headers is None:
            headers = {}
        if self.cookie is not None:
            headers["Cookie"] = self.cookie
        connection = self._get_proxy_connection()
        if path.startswith("/"):
            path = path[1:]
        path = f"/{CLASS_NAME}/{path}"
        print(f"Requesting {method} {path} ... ")
        connection.request(method, path, body=body, headers=headers)
        return connection

    def _get_proxy_connection(self) -> httplib.HTTPSConnection:
        proxies = getproxies()
        proxy = None
        if "https" in proxies:
            proxy = proxies["https"]
        if "http" in proxies:
            proxy = proxies["http"]

        if proxy is None or SKIP_PROXY:
            conn = httplib.HTTPSConnection(CDP_SERVER)
        else:
            print("Using proxy", proxy)
            conn = httplib.HTTPSConnection(proxy)
            conn.set_tunnel(CDP_SERVER)
        return conn


class AuthAware:
    """A dummy class to be used as a base class for classes that need to use the Auth class."""

    _has_auth = False

    def request(self, method, path, body=None, headers=None) -> httplib.HTTPSConnection:
        if not self._has_auth:
            raise RuntimeError("AuthAware class has not been initialized")
        return Auth().request(method, path, body=body, headers=headers)

    def __init__(self) -> None:
        raise RuntimeError("AuthAware is not meant to be instantiated")
