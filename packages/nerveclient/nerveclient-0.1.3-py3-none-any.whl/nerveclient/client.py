import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import pdb

class NerveEngineClient:
    connectionString = None
    apiKey = None
    jwt = None

    s = requests.Session()
    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[429, 500, 502, 503, 504])
    s.mount('http://', HTTPAdapter(max_retries=retries))

    def __refreshJwt(self):
        r = self.s.post(self.connectionString + "/auth", json={
            "data": {
                "apiKey": self.apiKey
            }
        })

        if r.status_code != 200:
          print("There was a problem authenticating to the Nerve Engine: " + str(r.content))
        r.raise_for_status()
        json = r.json()
        self.jwt = json["jwt"]

    def __init__(self, connectionString, apiKey):
        self.connectionString = connectionString
        self.apiKey = apiKey
        self.__refreshJwt()

    def health(self):
        r = self.s.get(self.connectionString + "/health")
        return r.status_code == 200

    def authed(self):
        r = self.s.post(self.connectionString + "/auth/ping", json={
            "jwt": self.jwt
        })

        return r.status_code == 200

    def query(self, **kwargs):
        retry = False 
        while True:
            args = {"jwt": self.jwt};
            args.update(kwargs);

            r = self.s.post(self.connectionString + "/query", json={"data": args});

            if not retry and r.status_code == 401:
                self.__refreshJwt()
                retry = True
                continue

            if r.status_code != 200:
                print("There was a problem executing the query: " + str(r.content))
            r.raise_for_status()

            return r.json()
