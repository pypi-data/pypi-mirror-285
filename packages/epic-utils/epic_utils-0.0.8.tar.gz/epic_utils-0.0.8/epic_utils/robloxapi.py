import requests
import json
from epic_utils.config import RobloxAPIConfig as config
from datetime import datetime

class RequestNotAuthorized(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class DataStoreEntry:
    def __init__(self, key : str, value : object, createTime : datetime, revisionCreateTime : datetime):
        self.key : str = key
        self.value : object = value
        self.createTime : datetime = createTime
        self.revisionCreateTime : datetime = revisionCreateTime
    def __str__(self):
        return f"Entry(key={self.key}, value={self.value})"

class DataStore:
    def __init__(self, api, name):
        self.api = api
        self.name = name
    def GetEntry(self, key):
        if not self.api.check_auth():
            return 
        result = self.api.request(config.ENTRYURL.format(universeid=self.api.universeId, datastore=self.name, entry=key),
                                  {"x-api-key" : self.api.api_key}, {})
        status_code = result.status_code
        if status_code != 200:
            return 
        result_data = json.loads(result.content)
        
        return DataStoreEntry(result_data["id"], result_data["value"], DataStore.loadTime(result_data["createTime"]), DataStore.loadTime(result_data["revisionCreateTime"]))
    
    def SetEntry(self, key : str, value : object):
        if not self.api.check_auth():
            return 
        data = {
            "value": value,
        }
        data = json.dumps(data)
        result = self.api.post(config.ENTRIESURL.format(universeid=self.api.universeId, datastore=self.name),
                                  {"x-api-key" : self.api.api_key, "content-type" : "application/json"}, {"id" : key}, data=data)
        status_code = result.status_code
        if status_code == 400:
            result = self.api.patch(config.ENTRYURL.format(universeid=self.api.universeId, datastore=self.name, entry=key),
                                    {"x-api-key" : self.api.api_key, "content-type" : "application/json"}, {"id" : key}, data=data)
        result_data = json.loads(result.content)

    def IncrementEntry(self, key : str, amount : int):
        if not self.api.check_auth():
            return 
        data = {
            "amount": amount,
        }
        data = json.dumps(data)
        result = self.api.post(config.ENTRYINCREMENTURL.format(universeid=self.api.universeId, datastore=self.name, entry=key),
                            {"x-api-key" : self.api.api_key, "content-type" : "application/json"}, {}, data=data)
        status_code = result.status_code
        result_data = json.loads(result.content)
        print(result_data)
    def DeleteEntry(self, key : str):
        if not self.api.check_auth():
            return 
        result = self.api.delete(config.ENTRYURL.format(universeid=self.api.universeId, datastore=self.name, entry=key),
                                 {"x-api-key" : self.api.api_key}, {})
        status_code = result.status_code
        result_data = result.content
        print(result_data)
    
    
    def ListEntries(self, temp_result = [], nextPageToken = ""):
        if not self.api.check_auth():
            return
        result = self.api.request(config.ENTRIESURL.format(universeid=self.api.universeId, datastore=self.name),
                                  {"x-api-key" : self.api.api_key}, {"pageToken" : nextPageToken, "maxPageSize" : config.PAGESIZE})
        status_code = result.status_code
        if status_code != 200:
            return temp_result
        result_data = json.loads(result.content)
        data = result_data["dataStoreEntries"]
        for entry in data:
            _data = self.GetEntry(entry["id"])
            temp_result.append(_data)
        if "nextPageToken" in list(result_data.keys()):
            nextPageToken = result_data["nextPageToken"]
        else:
            nextPageToken = ""
        
        if nextPageToken == "" or nextPageToken == None:
            return temp_result
        else:
            return self.ListEntries(temp_result=temp_result, nextPageToken=nextPageToken)
        
    @classmethod
    def loadTime(cls, string : str):
        if(string.count("0") > 0):
            for i in range(0, string.count("0")):
                string.replace("0", "0o")
        index = string.find(".")
        if index > -1:
            string = string[:index]
        time = datetime.strptime(string, "%Y-%m-%dT%H:%M:%S")
        return time        
    
    def __str__(self):
        return f"DataStore({self.api.universeId}, {self.name})"



class APIConnection:
    def __init__(self, universeId):
        self.universeId = universeId        
    
    def check_auth(self):
        keys = list(self.__dict__.keys())
        
        if "api_key" not in keys:
            raise RequestNotAuthorized("API Connection wasnt authorized")
        return True
        
    def auth(self, api_key):
        self.api_key = api_key
    
    
    
    def ListDataStores(self, temp_result=[], nextPageToken=""):
        if not self.check_auth():
            return
        result = self.request(config.DATASTOREURL.format(universeid=self.universeId),
                              {"x-api-key" : self.api_key}, {"pageToken" : nextPageToken, "maxPageSize" : config.PAGESIZE})
        status_code = result.status_code
        if status_code != 200:
            return temp_result
        result_data = json.loads(result.content)
        data = result_data["dataStores"]
        for ds in data:
            ds = DataStore(self, ds["id"])
            temp_result.append(ds)
        if "nextPageToken" in list(result_data.keys()):
            nextPageToken = result_data["nextPageToken"]
        else:
            nextPageToken = ""
        
        if nextPageToken == "" or nextPageToken == None:
            return temp_result
        else:
            return self.ListDataStore(temp_result=temp_result, nextPageToken=nextPageToken)
            
    def GetDataStore(self, datastore_name):
        return DataStore(self, datastore_name)
            
    def request(self, url, headers, params, data={}):
        result = requests.get(url, params=params, headers=headers, data=data)
        return result
    def post(self, url, headers, params, data={}):
        result = requests.post(url, params=params, headers=headers, data=data)
        return result
    def delete(self, url, headers, params, data={}):
        result = requests.delete(url, params=params, headers=headers, data=data)
        return result
    def patch(self, url, headers, params, data={}):
        result = requests.patch(url, params=params, headers=headers, data=data)
        return result
        