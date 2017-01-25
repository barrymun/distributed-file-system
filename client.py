import base64
import json
import time

import requests
from Crypto.Cipher import AES

PUBLIC_KEY = "0123456789abcdef0123456789abcdef"
client_id = "1"
decrypted_password = "0dP1jO2zS7111111"
r = requests.get("http://127.0.0.1:5000/client/auth")


def pad(s):
    return s + b" " * (AES.block_size - len(s) % AES.block_size)


# ESTABLISHING CONNECTION WITH AUTHENTICATION SERVER
cipher = AES.new(PUBLIC_KEY, AES.MODE_ECB)  # avoid ECB generally, but here is ok
encrypted_password = base64.b64encode(cipher.encrypt(decrypted_password))

headers = {'Content-type': 'application/json'}
payload = {'client_id': client_id, 'encrypted_password': encrypted_password}
r = requests.post("http://127.0.0.1:5000/client/auth", data=json.dumps(payload), headers=headers)
response_body = r.text
encoded_token = json.loads(response_body)["token"]

cipher = AES.new(PUBLIC_KEY, AES.MODE_ECB)  # never use ECB in strong systems obviously
decoded = cipher.decrypt(base64.b64decode(encoded_token))
decoded_data = json.loads(decoded.strip())

session_key = decoded_data["session_key"]
print("SESSION KEY DECODED")
print(session_key)
ticket = decoded_data["ticket"]
server_host = decoded_data["server_host"]
server_port = decoded_data["server_port"]

# UPLOADING FILE TO FILE SERVER, USING AUTHENTICATED DATA
cipher = AES.new(session_key, AES.MODE_ECB)  # never use ECB in strong systems obviously
encrypted_directory = base64.b64encode(cipher.encrypt(pad("/home/great")))
encrypted_filename = base64.b64encode(cipher.encrypt(pad("sample.txt")))

data = open('test.txt', 'rb').read()

headers = {'ticket': ticket, 'directory': encrypted_directory, 'filename': encrypted_filename}
r = requests.post("http://" + server_host + ":" + server_port + "/server/file/upload", data=data, headers=headers)
time.sleep(3)
print r.text

r2 = requests.post("http://" + server_host + ":" + server_port + "/server/file/delete", headers=headers)
time.sleep(3)
print r2.text

# texturl = "http://" + server_host + ":" + server_port + "/server/file/rollback"
# print url
# r3 = requests.post(url, headers=headers)
# print r3.text
