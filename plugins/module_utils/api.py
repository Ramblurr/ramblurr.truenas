import requests

API_ENDPOINT = "%(hostname)s/api/v2.0"


class TruenasApi:
    def __init__(self, hostname, username, password):
        self.auth_tuple = (username, password)
        self.api_endpoint = API_ENDPOINT % {"hostname": hostname}
        self.headers = {"Content-Type": "application/json"}

    def _result(self, r):
        if r.ok:
            try:
                return r.json()
            except:
                return r.text
        raise ValueError(r)

    def _strip(self, resource):
        if resource[0] == "/":
            return resource[1:]

    def _uri(self, resource):
        return "%s/%s/" % (self.api_endpoint, self._strip(resource))

    def post(self, resource, data=None):
        uri = self._uri(resource)
        r = requests.post(uri, json=data, headers=self.headers, auth=self.auth_tuple)
        return self._result(r)

    def put(self, resource, data=None):
        uri = self._uri(resource)
        r = requests.put(uri, json=data, headers=self.headers, auth=self.auth_tuple)
        return self._result(r)

    def delete(self, resource):
        uri = self._uri(resource)
        r = requests.delete(uri, headers=self.headers, auth=self.auth_tuple)
        return self._result(r)

    def get(self, resource, data=None):
        uri = self._uri(resource)
        r = requests.get(uri, headers=self.headers, auth=self.auth_tuple)
        return self._result(r)
