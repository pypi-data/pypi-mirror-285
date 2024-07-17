from typing import Union, Literal

GrantType = Union[Literal["password"], Literal["client_credentials"], Literal["refresh_token"]]

API_BASE_URL = "https://api.xbrl.us/api/v1"
BASE_URL = "https://api.xbrl.us"
