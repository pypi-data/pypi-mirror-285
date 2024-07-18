import logging
import warnings
from typing import Dict, Any

import requests
from requests import Response

from investfly.models.CommonModels import Session

warnings.simplefilter("ignore")


class RestApiClient:

    """
    Internal class to make REST API requests. Users of the SDK do not use this class directly.
    Please use investfly.api.InvestflyApiClient` instead
    """

    def __init__(self, baseUrl: str) -> None:
        self.headers: Dict[str, str] = {}
        self.baseUrl = baseUrl
        self.log = logging.getLogger(self.__class__.__name__)

    def login(self, username: str, password: str) -> Session:
        res = requests.post(self.baseUrl + "/user/login", auth=(username, password), verify=False)
        if res.status_code == 200:
            self.headers['investfly-client-id'] = res.headers['investfly-client-id']
            self.headers['investfly-client-token'] = res.headers['investfly-client-token']
            dict_obj = res.json()
            session = Session.fromJsonDict(dict_obj)
            return session
        else:
            raise RestApiClient.getException(res)

    def logout(self):
        requests.post(self.baseUrl + "/user/logout", verify=False)
        del self.headers['investfly-client-id']
        del self.headers['investfly-client-token']

    def doGet(self, url: str) -> Any:
        res = requests.get(self.baseUrl + url, headers=self.headers, verify=False)
        # This does not actually return JSON string, but instead returns Python Dictionary/List etc
        if res.status_code == 200:
            contentType: str = res.headers['Content-Type']
            if "json" in contentType:
                return res.json()
            else:
                return res.text
        else:
            raise RestApiClient.getException(res)

    def doPost(self, url: str, obj: Dict[str, Any]) -> Any:
        res: Response = requests.post(self.baseUrl + url, json=obj, headers=self.headers, verify=False)
        if res.status_code == 200:
            contentType: str = res.headers['Content-Type']
            if "json" in contentType:
                return res.json()
            else:
                return res.text
        else:
            raise RestApiClient.getException(res)
        
    def doPostCode(self, url: str, code: str) -> Any:
        res: Response = requests.post(self.baseUrl + url, data=code, headers=self.headers, verify=False)
        if res.status_code == 200:
            contentType: str = res.headers['Content-Type']
            if "json" in contentType:
                return res.json()
            else:
                return res.text
        else:
            raise RestApiClient.getException(res)

    @staticmethod
    def getException(res: Response):
        try:
            # Server returns valid JSON in case of any exceptions that may occor while processing request
            errorObj: Dict[str, Any] = res.json()
            if 'message' in errorObj.keys():
                return Exception(errorObj.get('message'))
            else:
                return Exception(str(errorObj))
        except requests.exceptions.JSONDecodeError:
            # Just in case, there are other errors
            return Exception(res.text)
