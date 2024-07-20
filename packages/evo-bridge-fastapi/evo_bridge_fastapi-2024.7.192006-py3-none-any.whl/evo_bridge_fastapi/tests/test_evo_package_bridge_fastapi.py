import unittest
import sys
import os
import requests
import json
import asyncio
import httpx
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_path + "/../../../../")

from evo.evo_framework import *

REMOTE_URL_CYBORGAI="https://cyborgai-api.fly.dev"

class TestAction(unittest.IsolatedAsyncioTestCase):
    
    async def asyncSetUp(self):
        
        idServer="6eab59db3e60504711845564bb31b567bbe5c0a2fa1919e6879fa7040695c194"

       # response = requests.get(f"{REMOTE_URL_CYBORGAI}/v1/get_server/{idServer}")

       # print("response.status_code:",response.status_code)
       # print("Response get_server:", response.content)

       # mapResponse=response.json()
        #print("Response get_server:", response.content)
        
        self.REMOTE_URL="http://172.20.10.10:8081"# mapResponse["remote_url"]
     
    
        
    async def test_0_do_text_openai(self):
        url = f"{self.REMOTE_URL}/do_action"  # Change the item name as needed
        print("test_DoGetTextStream",url)
        # Data to send - modify this as per your ItemData model
     
        eAction = EAction()
        eAction.doGenerateID()
        eAction.action = "do_text-openai"
        
        eActionItem = EActionItem()
        eActionItem.id = "input_text"
        eActionItem.enumApiType = EnumApiType.STRING
        eActionItem.data = b"how are you?"
        
        eAction.mapInput.doSet(eActionItem)
      
        eRequest = ERequest()
        eRequest.doGenerateID()
       
        eRequest.data = eAction.toBytes()
        
        eRequest.hash = IuCryptHash.toSha256Bytes(eRequest.data)
        eRequestBytes = IuApi.ToERequestLZ4(eRequest)
        print("len eRequestBytes:",len(eRequestBytes))
        timeout = httpx.Timeout(60.0, connect=10.0)
        async with httpx.AsyncClient() as client:
            try:
               
                response = await client.post(url, content=eRequestBytes)
                response.raise_for_status()

                async for data in response.aiter_bytes():
                   
                    if data:
                        eAction:EAction = IuApi.toEObject(EAction(), data)
                        print(eAction.mapInput.doGet("output_text"))
                        #text = await eAction.fromApiType("output_text")
                        #print(text)

            except httpx.HTTPStatusError as e:
                print(f"HTTP error: {e}")
            except httpx.RequestError as e:
                print(f"Request error: {e}")
        
    async def Atest_1_do_get_eapiconfig(self):
        url = f"{self.REMOTE_URL}/do_action"  # Change the item name as needed
        print("url",url)
        # Data to send - modify this as per your ItemData model
     
        eAction = EAction()
        eAction.doGenerateID()
        eAction.action = "do_get_eapiconfig"
        
        eActionItem = EActionItem()
        eActionItem.id = "input_text"
        eActionItem.enumApiType = EnumApiType.STRING
        eActionItem.data = b"how are you?"
        
        eAction.mapInput.doSet(eActionItem)
      
        eRequest = ERequest()
        eRequest.doGenerateID()
       
        eRequest.data = eAction.toBytes()
        
        eRequest.hash = IuCryptHash.toSha256Bytes(eRequest.data)
        eRequestBytes = IuApi.ToERequestLZ4(eRequest)
        print("len eRequestBytes:",len(eRequestBytes))
        
        response = requests.post(url, data=eRequestBytes)
        self.assertEqual(response.status_code, 200)
        #print("response.status_code:",response.status_code)
        #print("Response:", response.content)
        
        #print("eResponse.data:", eResponse.data)
        
        eResponseBytes = response.content
        print(f"eResponseBytes:{eResponseBytes}")
        
        eResponse = IuApi.FromEResponse(eResponseBytes)
       
        eApiConfig = IuApi.toEObject(EApiConfig(),eResponse.data )
        print(f"eApiConfig:{eApiConfig}")
       
  
if __name__ == '__main__':
    unittest.main()