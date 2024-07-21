import os
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

SERVICE_URL = os.getenv("SERVICE_URL")


class toqen:
  """
  A client class for interacting with the Toqen server.
  """
  def __init__(self, 
               toqen_ai_key, 
               org_id, 
               server_url = "https://toqen-server.onrender.com", 
               canary_prob = 0.1):
    self.server_url = server_url
    self.toqen_ai_key = toqen_ai_key
    self.org_id = org_id
    self.canary_prob = canary_prob
    print('TOQEN.AI: Client initialized')

  def chat(self, text_prompt, **kwargs):
    data = {
       "message": text_prompt, 
       'toqen_ai_key':self.toqen_ai_key,
       'org_id':self.org_id,
       'canary_prob':self.canary_prob,
       'kwargs':kwargs
       }

    # print(f"ECHO.AI: {kwargs}")

    response = requests.post(self.server_url, json=data)

    # Check response status code
    if response.status_code == 200:
    # Successful response
        response_data = response.json()
        echoed_message = response_data.get("message")
        # print(f"TOQEN.AI: {echoed_message}")
    else:
        # Error response
        response_data = response.json()
        echoed_message = f"Error: {response.status_code} - {response.text}"
        # print(echoed_message)
        

    return echoed_message


# Export the EchoClient class
__all__ = ['toqen']
