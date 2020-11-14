import requests
from datetime import datetime
from datetime import timezone
import secrets
import hashlib
import base64

class EmarsysApi:
    def __init__(self, username, secret, url = 'https://api.emarsys.net/api/v2/'):
        self.username = username
        self.secret = secret
        self.url = url
    def generateNonce(self):
        return secrets.token_hex(16)

    def getUTCTimestamp(self):
        dateTimeObj = datetime.utcnow()
        timestampStr = dateTimeObj.strftime("%Y-%m-%dT%H:%M:%SZ")
        return timestampStr

    def getPasswordDigest(self, nonce, timestamp, secret):
        text = nonce + timestamp + secret
        
        #SHA1 hash value of the concatenated string in hexadecimal format
        h = hashlib.sha1()
        h.update(text.encode('utf-8'))
        x = h.hexdigest()

        #Return base64encode of the hexdigest
        return base64.b64encode(x.encode('utf-8')).decode('utf-8')

    def send(self, requestType, endPoint, requestBody = ''):
        if requestType not in ['POST','GET','PUT','DELETE']:
            raise Exception('Send first parameter must be "GET", "POST", "PUT" or "DELETE"')

        requestURI = self.url + endPoint
        timestamp = self.getUTCTimestamp()
        nonce = self.generateNonce()
        passwordDigest = self.getPasswordDigest(nonce, timestamp, self.secret)

        header = f"UsernameToken Username=\"{self.username}\", PasswordDigest=\"{passwordDigest}\", Nonce=\"{nonce}\", Created=\"{timestamp}\""
        print(header)
        headers = {'X-WSSE' : header}
        if requestType == 'POST':
            r = requests.post(requestURI,headers=headers, data = requestBody)
        elif requestType == 'PUT':
            r = requests.put(requestURI,headers=headers, data = requestBody)
        elif requestType == 'GET':
            r = requests.get(requestURI,headers=headers)
        elif requestType == 'DELETE':
            r = requests.delete(requestURI,headers=headers, data = requestBody)

        return r.json()

api = EmarsysApi('customer001','customersecret')
print(api.send('GET','settings'))
print(api.send('PUT', 'contact', '{"key_id": "3","contacts":[{"3": "erik.selvig@example.com","2": "Selvig"},{"3": "ian.boothby@example.com","2": "Boothby"}]}'))

