from datetime import datetime
from enum import Enum
import json
import os
from pymongo import MongoClient
from dateutil import parser
import requests
from a2ginputstream.inputstream import Inputstream


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return super().default(obj)

class CustomJsonDecoder(json.JSONDecoder):
    def __init__(self, *args ,**kargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kargs)

    def object_hook(self, obj:dict):
        for k, v in obj.items():
            if isinstance(v, str) and 'T' in v and '-' in v and ':' in v and len(v) < 30:
                try:
                    dv = parser.parse(v)
                    dt = dv.replace(tzinfo=None)
                    obj[k] = dt
                except:
                    pass
        return obj

A2G_URL = "https://v2apigateway.a2g.io"
mongo_conn  = os.environ.get("DATA_MONGO_CONN", None)
mongo_db    = os.environ.get("DATA_DB_NAME", None)

class A2GHttpClient():

    def __init__(self, token):
        self.token = token


    def get_inputstream_by_ikey(self, ikey:str) -> Inputstream:
        try:
            headers = { "Authorization": f"A2G {self.token}"}
            res = requests.get(A2G_URL + f"/Inputstream/Ikey/{ikey}", headers=headers, verify=False)
            if res.status_code != 200: raise Exception("Error al obtener el inputstream")
            content = res.json(cls=CustomJsonDecoder)
            if not content["success"]: raise Exception(content["errorMessage"])
            return Inputstream(from_response=True, **content["data"])
        except Exception as e:
            raise e
    

    def insert_data(self, ikey:str, data:list[dict]):
        try:
            headers = {
                "Authorization": f"A2G {self.token}",
                "ikey": ikey
            }
            res = requests.post(A2G_URL + "Insert", headers=headers, json=data)
            if res.status_code != 200:
                raise Exception("Error al obtener el inputstream")
        except Exception as e:
            raise e
        
        

class CloudInputstream:

    def __init__(self, token:str, **kwargs):
        self.token  = token
        if mongo_conn is None or mongo_db is None:
            raise Exception("Missing MONGO_CONN or DB_NAME environment variables")
        self.client = MongoClient(mongo_conn)
        self.db     = self.client[mongo_db]
        self.inputstreams: dict[str, Inputstream] = {}
        self.a2g_client = A2GHttpClient(token)


    def get_inputstream(self, ikey:str, **kwargs) -> Inputstream:
        """
        return Inputstream
        """
        inputstream = self.inputstreams.get(ikey, None)
        if inputstream is None:
            inputstream = self.a2g_client.get_inputstream_by_ikey(ikey)
            self.inputstreams[ikey] = inputstream
        
        return inputstream


    def get_inputstream_schema(self, ikey:str, **kwargs) -> dict:
        """
        return Inputstream schema
        params:
            ikey: str
            cache: bool = True -> if True, use cache if exists and is not expired
        """
        inputstream = self.inputstreams.get(ikey, None)
        if inputstream is None:
            inputstream = self.a2g_client.get_inputstream_by_ikey(ikey)
            self.inputstreams[ikey] = inputstream
        
        return json.loads(inputstream.Schema)


    def find(self, ikey:str, query:dict, **kwargs):
        """
        return data from inputstream
        params:
            ikey: str
            query: dict
        """
        inputstream = self.inputstreams.get(ikey, None)
        if inputstream is None:
            inputstream = self.a2g_client.get_inputstream_by_ikey(ikey)
            self.inputstreams[ikey] = inputstream
        coll_name = inputstream.InputstreamCollectionName
        return list(self.db[coll_name].find(query))


    def find_one(self, ikey, query:dict, **kwargs):
        """
        return one data from inputstream
        params:
            collection: str
            query: dict
        """
        inputstream = self.inputstreams.get(ikey, None)
        if inputstream is None:
            inputstream = self.a2g_client.get_inputstream_by_ikey(ikey)
            self.inputstreams[ikey] = inputstream
        coll_name = inputstream.InputstreamCollectionName
        return self.db[coll_name].find_one(query)   
     

    def get_data_aggregate(self, ikey:str, query: list[dict], **kwargs):
        """
        return data from inputstream
        params:
            ikey: str
            query: list[dict]
        """
        inputstream = self.inputstreams.get(ikey, None)
        if inputstream is None:
            inputstream = self.a2g_client.get_inputstream_by_ikey(ikey)
            self.inputstreams[ikey] = inputstream
        coll_name = inputstream.InputstreamCollectionName
        return list(self.db[coll_name].aggregate(query))
    

    def insert_data(self, ikey:str, data:list[dict]):
        """
        validate data against inputstream JsonSchema and insert into inputstream collection
        params:
            ikey: str
            data: list[dict]
        """
        inputstream = self.inputstreams.get(ikey, None)
        if inputstream is None:
            inputstream = self.a2g_client.get_inputstream_by_ikey(ikey)
            self.inputstreams[ikey] = inputstream
        self.a2g_client.insert_data(ikey, data)
        