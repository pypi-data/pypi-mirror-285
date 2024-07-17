import requests
import datetime
from abc import abstractmethod
from typing import Any, Optional, List
from urllib.parse import urlencode
from .models import *

class XBRLUSClient:
  token: str = ""
  client_id = ""
  username = ""
  password = ""
  client_secret = ""
  platform = "pc"
  access_token = ""
  refresh_token = ""
  expires_in = 0
  refresh_token_expires_in = 0
  token_type = "bearer"
  grant_type: GrantType
  _last_token_fetch_time: datetime.datetime = None

  session: requests.Session = None

  request_headers = {
    "Content-Type": "application/json; charset=utf-8"
  }


  def __init__(self, client_id: str, grant_type: GrantType, client_secret: str, platform: str, username: Optional[str] = None, password: Optional[str] = None):
    self.client_id = client_id
    self.client_secret = client_secret
    self.username = username
    self.password = password
    self.platform = platform
    self.grant_type  =grant_type
    self.session = requests.Session()
    

  def __refresh_when_expired(self):
    pass
  def __login_to_api(self, client_id: str, grant_type: GrantType, client_secret: str, username: str, password: str, platform: str):
    req_data = {
      "client_id": client_id,
      "client_secret": client_secret,
      "platform": platform,
      "grant_type": grant_type
    }
    if grant_type == "password":
      req_data["username"] = username
      req_data["password"] = password
    if grant_type == "refresh_token":
      req_data["refresh_token"] = self.refresh_token
    print(req_data)
    r = self.session.post(f"{BASE_URL}/oauth2/token", headers={
      "Content-Type": "application/x-www-form-urlencoded"
    }, data=req_data)
    resp = r.json()
    self.access_token = resp["access_token"]
    self.refresh_token = resp["refresh_token"]
    self.expires_in = resp["expires_in"]
    self._last_token_fetch_time = datetime.datetime.now()
    self.token_type = resp["token_type"]
    self.refresh_token_expires_in = resp["refresh_token_expires_in"]
    self.session.headers = {
      "Authorization": f"Bearer {self.access_token}"
    }

  def login(self):
    self.__login_to_api(self.client_id, self.grant_type, self.client_secret, self.username, self.password, self.platform)

  def renew_token(self):
    self.__login_to_api(self.client_id, "refresh_token", client_secret=self.client_secret, username=self.username, password=self.password, platform=self.platform)

class BaseEndpoint:

  client: XBRLUSClient = None

  def __init__(self, client: XBRLUSClient):
    self.client = client
    self.client.session.headers = {
      "Authorization": f"Bearer {client.access_token}"
    }

  @abstractmethod
  def search(self, params: dict, fields: list[str]):
    pass

  @abstractmethod
  def query_by_id(self, id: str, fields: list[str]):
    pass

  def get_headers(self):
    return {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {self.client.access_token}"
    }
  
  def request(self, method: str, url: str, params: dict, fields: List[str], body: Optional[dict] = None) -> requests.Response:
    if (datetime.datetime.now() - self.client._last_token_fetch_time).seconds > self.client.expires_in:
      self.client.renew_token()
    core_url = f"{API_BASE_URL}/{url}?fields={','.join(fields)}&{urlencode(params) if params is not None else ''}"
    if method == "GET":
      r = self.client.session.get(core_url)
    if method == "POST":
      r = self.client.session.post(core_url, data=body)
    if method == "DELETE":
      r = self.client.session.delete(core_url)
    return r
    
class FactsEndpoint(BaseEndpoint):
  
  def search(self, params):
    pass
  
  def query_by_id(self, id: str):
    pass


class EntityEndpoint(BaseEndpoint):
  def search(self, params: dict, fields: List[str]):
    url = f"/entity/search"
    r = self.request(method="GET", url=url, fields=fields, params=params)
    return r.json()
  
  def query_by_id(self, id: str, fields: List[str]):
    r = self.request(method="GET", url=f"entity/{id}", fields=fields, params=None)
    return r.json()
  def search_reports(self, params: dict, fields: List[str]):
    url = "/entity/report/search"
    r = self.request("GET", url=url, params=params, fields=fields)
  def search_reports_from_entity(self, entity_id: str, params: dict, fields: List[str]):
    url = f"/entity/{entity_id}/report/search"
    r = self.request("GET", url=url, params=params, fields=fields)
    return r.json()

class ReportsEndpoint(BaseEndpoint):
  def search(self, params: dict, fields: list[str]):
    url = "/report/search"
    r = self.request("GET", url, params, fields=fields)
    return r.json()

  def query_by_id(self, id: str, fields: list[str]):
    url = f"/report/{id}"
    r = self.request("GET", url, None, fields)
    return r.json()

  def search_fact_in_report(self, report_id: str, params: dict, fields: List[str]):
    url = f"/report/{report_id}/fact/search"
    r = self.request("GET", url, params, fields)
    return r.json()

  def search_report_containing_facts(self, params, fields):
    url = f"/report/fact/search"
    r = self.request("GET", url, params, fields)
    return r.json()

class AssertionEndpoint(BaseEndpoint):
  def search(self, params: dict, fields: list[str]):
    url = "/assertion/search"
    r = self.request("GET", url, params, fields)
  def validate(self, file: Any):
    url = "/assertion/validate"
    r = self.request("POST", url, params={}, fields={}, body=file)
    return r.ok    

class DTSEndpoint(BaseEndpoint):
  def search(self, params: dict, fields: list[str]):
    url = "/dts/search"
    r = self.request("GET", url, params, fields)
    return r.json()

  def search_concept_in_dts(self, dts_id: str, params: dict, fields: List[str]):
    url = f"/dts/{dts_id}/concept/search"
    r = self.request("GET", url, params, fields)
    return r.json()

  def get_concept_from_dts(self, dts_id: str, concept_local_name: str, params: dict, fields: List[str]):
    url = f"/dts/{dts_id}/concept/{concept_local_name}"
    r = self.request("GET", url, params, fields)
    return r.json()

  def get_concept_label(self, dts_id: str, concept_local_name: str, params: dict, fields: List[str]):
    url = f"/dts/{dts_id}/concept/{concept_local_name}/label"
    r = self.request("GET", url, params, fields)

  def get_concept_reference(self, dts_id: str, concept_local_name: str, params: dict, fields: List[str]):
    url = f"/dts/{dts_id}/concept/{concept_local_name}/reference"
    r = self.request("GET", url, params, fields)
    return r.json()
  

  def get_network_and_relationship_info(self, dts_id: str, fields: List[str]):
    url = f"/dts/{dts_id}/network"
    r = self.request("GET", url, params={}, fields=fields)
    return r.json()

  def search_relationship_info(self, dts_id: str, fields: List[str]):
    url = f"/dts/{dts_id}/network/search"
    r = self.request("GET", url, params={}, fields=fields)
    return r.json()

class ConceptEndpoint(BaseEndpoint):
  def search(self, params: dict, fields: list[str]):
    url = f"/concept/search"
    r = self.request("GET", url, params, fields)
    return r.json()

  def search_concept_in_reports(self, concept_local_name: str, params: dict, fields: List[str]):
    url = f"/concept/{concept_local_name}/search"
    r = self.request("GET", url, params, fields)
    return r.json()


class LabelEndpoint(BaseEndpoint):
  def search(self, params: dict, fields: list[str]):
    url = "/label/search"
    r = self.request("GET", url, fields=fields, params=params)
    return r.json()

  def search_in_dts(self, dts_id: str, params: dict, fields: List[str]):
    url = f"/label/{dts_id}/search"
    r = self.request("GET", url, params, fields)
    return r.json()

class NetworkEndpoint(BaseEndpoint):
  def search(self, params: dict, fields: list[str]):
    '''
    /network/relationship/search
    '''
    url = "/network/relationship/search"
    r = self.request("GET", url, params, fields)
    return r.json()


  def search_relationship_in_network(self, network_id: str, params: dict, fields: List[str]):
    url = f"/network/{network_id}/relationship/search"
    r = self.request("GET", url, params, fields)
    return r.json()

  def query_by_id(self, id: str, fields: List[str]):
    url = f"/network/{id}"
    r = self.request("GET", url, params={}, fields=fields)
    return r.json()

class RelationshipEndpoint(BaseEndpoint):
  def search(self, params: dict, fields: list[str]):
    url = "/relationship/search"
    r = self.request("GET", url, params, fields)
    return r.json()
  
  def get_as_tree(self, params: dict, fields: List[str]):
    url = "/relationship/tree/search"
    r = self.request("GET", url, params, fields)
    return r.json()

class DocumentsEndpoint(BaseEndpoint):
  def search(self, params: dict, fields: list[str]):
    url = "/document/search"
    r = self.request("GET", url, params, fields)
    return r.json()