import json

from httpx import AsyncClient, Timeout, Response
from datetime import datetime, timedelta

from wellog import loggen
from envOS import server_env

from .Error import Error_Auth

wdai = {
  "authorization": None,
  "expiration": None,
}

class Request:
  def __init__(self, verify=False):    
    self._SERVER=[
      'WELLDOCS_INTER',
      'WELLDOCS_PUBLIC',
      'PYVERT_INTER',
      'PYVERT_PUBLIC',
      'WDAI_PUBLIC'
    ]
    params = { "verify":verify}
    self.client = AsyncClient(**params)
    self._WDAI_KEY:dict={'username':'', 'password':''}

  async def get(self, server:str, url:str='', timeout:int=60, need_token=False, type_response='JSON')->Response:
    '''
    If you need to authenticate with jtw, go through the option of the server to authenticate
    `type_response` refers to how the server will respond, can be `STRING` or `JSON`
    '''
    start = datetime.now()
    data = {
      "url": server + url,
      "timeout":Timeout(timeout)
    }
    if need_token:
      if need_token == 'WDAI':
        auth = await self.prepare_wdai(server)
        data.update(auth)

    response = await self.client.get(**data)
    loggen.info(f"{data['url']} - {response.status_code} - {(datetime.now() - start).total_seconds():.2f}s")
    
    return response
  
  async def post(self, server:str, url:str, appJson:dict=None, FormData:dict=None, Files=None, timeout:int=60, need_token=False, type_response='JSON')->Response:
    '''
    If you need to authenticate with jtw, go through the option of the server to authenticate
    `type_response` refers to how the server will respond, can be `STRING` or `JSON`
    '''
    start = datetime.now()
    data = {
      "url": server + url,
      "timeout":Timeout(timeout)
    }

    if need_token:
      if need_token == 'WDAI':
        auth = await self.prepare_wdai(server)
        data.update(auth)

    if appJson: data['json']=appJson
    else:
      data['data']=FormData
      if Files: data['files']=Files
    
    response = await self.client.post(**data)
    loggen.info(f"{data['url']} - {response.status_code} - {(datetime.now() - start).total_seconds():.2f}s")
    return response

  def prepare_response(self, type_response:str, data):
    '''Deprecated'''
    try:
      if type_response == 'STRING':
        response = json.loads(data.text)
      else:
        response = data.json()
      return response
    except Exception as e:
        response = {}
        loggen.error(str(e))

  async def prepare_wdai(self, BASE_URL):
    data = {}    
    if not wdai['expiration'] or datetime.now() > wdai['expiration']:
      wdai['expiration'] = None
      data = {
        "url": f"{BASE_URL}auth",
        "json":self._WDAI_KEY
      }
      response = await self.client.post(**data)
      loggen.info(f"{data['url']} - {response.status_code}")
      auth = response.json()
      
      if 'access_token' not in auth or 'token_type' not in auth: raise Error_Auth("Could not validate credentials")
      data = {}
      wdai['expiration'] = datetime.now() + timedelta(hours=11, minutes=59, seconds=30)
      wdai['authorization'] = auth['token_type'] + " " + auth['access_token']
    data['headers']={
        "Authorization": wdai['authorization']
      }
    return data
  
  def setKeyWDAI(self, key:dict):
    self._WDAI_KEY.update(key)