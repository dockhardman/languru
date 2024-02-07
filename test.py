import json
import os
from typing import Text

import requests
from dotenv import load_dotenv
from openai import OpenAI
from rich import print

load_dotenv()


client = OpenAI(base_url="http://localhost:8680/v1")
res = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ],
)
print(res)


# api_key = os.environ["OPENAI_API_KEY"]

# headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
# data = {
#     "model": "gpt-3.5-turbo",
#     "messages": [
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "Hello!"},
#     ],
#     "stream": True,
# }


# try:
#     with requests.post(
#         "https://api.openai.com/v1/chat/completions",
#         json=data,
#         headers=headers,
#         stream=True,
#     ) as response:
#         # Check if the connection was established successfully
#         if response.status_code != 200:
#             print(f"Connection failed: {response.status_code}")
#             exit(1)
#         for line in response.iter_lines():
#             if line:
#                 decoded_line: Text = line.decode("utf-8")
#                 if decoded_line.strip().startswith("data: "):
#                     data = decoded_line.replace("data: ", "", 1)
#                     print(json.loads(data))

#                 # # SSE data lines start with "data: "
#                 # if decoded_line.startswith("data: "):
#                 #     data = decoded_line.replace("data: ", "", 1)
#                 #     print(f"Received data: {data}")
# except Exception as e:
#     print(f"An error occurred: {e}")
