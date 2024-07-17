import unittest
from xbrluspy import XBRLUSClient, EntityEndpoint


SECRET = "da1e8f3e-2b98-4de8-9132-bb551dabebc3"
CLIENT_ID = "f2864797-e196-47d2-a450-a7fa0495f905"
USERNAME = "hcyip42@gmail.com"
PASSWORD = "o2Rg8XAnNh"

class EntityTests(unittest.TestCase):
  client = XBRLUSClient(client_id=CLIENT_ID, 
                      grant_type="password", 
                      client_secret=SECRET, 
                      username=USERNAME,
                      password=PASSWORD,
                      platform="pc")
  entity = None
  def __init__(self, methodName: str = "runTest"):
    self.client.login()
    self.entity = EntityEndpoint(self.client)
    super().__init__(methodName)


  def test_search(self):
    res = self.entity.search(params={
      "entity.cik": "0000320193"
    },
    fields=[
      "entity.cik", "entity.id", "entity.name"
    ])
    print(res)
    self.assertEqual(res["data"][0]["entity.name"], "Apple Inc.")
  
  def test_query(self):
    res = self.entity.query_by_id("5927", fields=[
      "entity.cik"
    ])
    print(res)
    self.assertEqual(res["data"][0]["entity.cik"], "0000320193")
if __name__ == "__main__":
  unittest.main()