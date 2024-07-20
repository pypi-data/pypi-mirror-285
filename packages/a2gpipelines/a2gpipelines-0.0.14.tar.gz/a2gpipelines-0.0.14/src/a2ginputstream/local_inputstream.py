from datetime import datetime, timedelta
from enum import Enum
import hashlib
import os
import json
import requests
from a2ginputstream.inputstream import Inputstream
from jsonschema import Draft4Validator
from dateutil import parser

A2G_DATA_URL        = os.environ.get("DATA_URL", "https://v2streams.a2g.io")
A2G_INPUTSTREAM_URL = os.environ.get("INPUTSTREAM_URL", "https://v2apigateway.a2g.io")


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
            if isinstance(v, str) and 'T' in v and '-' in v and ':' in v and len(v) < 40:
                try:
                    dv = parser.parse(v)
                    dt = dv.replace(tzinfo=None)
                    obj[k] = dt
                except:
                    pass
        return obj


class CacheManager:
    duration_inputstream:int
    duration_data:int

    def __init__(self, cache_options: dict | None = None):
        if cache_options is None:
            self.duration_data = 60 * 24
            self.duration_inputstream = 60 * 24
        else:
            self.duration_data = cache_options.get("duration_data", 60 * 24)
            self.duration_inputstream = cache_options.get("duration_inputstream", 60 * 24)

        # create cache directories
        if not os.path.exists(".a2g_cache"):
            os.mkdir(".a2g_cache")
            os.mkdir(".a2g_cache/inputstreams")
            os.mkdir(".a2g_cache/data")
        

    def get_inputstream(self, ikey:str) -> Inputstream | None:
        """
        return Inputstream if exists in cache and is not expired
        otherwise return None
        params:
            ikey: str
        """
        file_name = f".a2g_cache/inputstreams/{ikey}.json"
        if os.path.exists(file_name):
            print(f"Inputstream - Ikey: {ikey}, Checking cache expiration...")
            data = json.loads(open(file_name, "r").read(), cls=CustomJsonDecoder)
            if datetime.utcnow() < data["duration"]:
                print(f"Inputstream - Ikey: {ikey}, from cache")
                return Inputstream(**data["inputstream"])
            else:
                print(f"Inputstream - Ikey: {ikey}, Cache expired, removing file...")
                os.remove(file_name)
                return None
        return None


    def set_inputstream(self, inputstream:Inputstream):
        cache_register = {
            "inputstream": inputstream.get_dict(),
            "duration": datetime.utcnow() + timedelta(minutes=self.duration_inputstream)
        }

        file_name = inputstream.Ikey
        if not os.path.exists(f".a2g_cache/inputstreams/"): os.mkdir(f".a2g_cache/inputstreams/")
        open(f".a2g_cache/inputstreams/{file_name}.json", "w+").write(json.dumps(cache_register, cls=CustomJSONEncoder))


    def get_data(self, ikey:str, hash_query:str) -> list[dict] | None:
        """
        return data if exists in cache and is not expired
        otherwise return None
        params:
            ikey: str
            query: dict
        """
        file_name = f".a2g_cache/data/{ikey}/{hash_query}.json"
        index_ttl_file = f".a2g_cache/data/ttl_index.json"
        if os.path.exists(file_name) and os.path.exists(index_ttl_file):

            # check if cache is expired
            print(f"Data - Ikey: {ikey}, Checking cache expiration...")
            index = json.loads(open(index_ttl_file, "r").read(), cls=CustomJsonDecoder)
            ttl_key = f"{ikey}_{hash_query}"
            if ttl_key in index:
                ttl = index[ttl_key]
                if datetime.utcnow() > ttl:
                    print(f"Data - Ikey: {ikey}, Cache expired, removing file...")
                    os.remove(file_name)
                    return None

            # recover data from cache
            try:
                print(f"Data - Ikey: {ikey}, Recovering data from cache...")
                data = json.loads(open(file_name, "r").read(), cls=CustomJsonDecoder)
                print(f"Data - Ikey: {ikey}, from cache")
                return data
            except Exception as e:
                print(f"Error reading cache file: {file_name} - {e}")
                if os.path.exists(file_name): os.remove(file_name)
                return None
        else:
            if os.path.exists(file_name): os.remove(file_name)
            return None
    

    def set_data(self, ikey:str, hash_query:str, data:list[dict]):
        # update ttl index
        ttl_key = f"{ikey}_{hash_query}"
        ttl = datetime.utcnow() + timedelta(minutes=self.duration_data)
        index_file = f".a2g_cache/data/ttl_index.json"
        if os.path.exists(index_file):
            index = json.loads(open(index_file, "r").read(), cls=CustomJsonDecoder)
            index[ttl_key] = ttl
            open(index_file, "w+").write(json.dumps(index, cls=CustomJSONEncoder))
        else:
            open(index_file, "w+").write(json.dumps({ttl_key: ttl}, cls=CustomJSONEncoder))

        # save data
        file_name = f".a2g_cache/data/{ikey}/{hash_query}.json"
        if not os.path.exists(f".a2g_cache/")               : os.mkdir(f".a2g_cache/")
        if not os.path.exists(f".a2g_cache/data/")          : os.mkdir(f".a2g_cache/data/")
        if not os.path.exists(f".a2g_cache/data/{ikey}/")   : os.mkdir(f".a2g_cache/data/{ikey}/")
        open(file_name, "w+").write(json.dumps(data, cls=CustomJSONEncoder))



class A2GHttpClient():

    def __init__(self, token:str):
        self.token = token


    def get_inputstream_by_ikey(self, ikey:str) -> Inputstream:
        try:
            headers = { "Authorization": f"A2G {self.token}"}
            res = requests.get(A2G_INPUTSTREAM_URL + f"/Inputstream/Ikey/{ikey}", headers=headers, verify=False)
            print(f"Getting inputstream {ikey} from A2G...")
            if res.status_code != 200:
                print(res.status_code, res.text) 
                raise Exception("Error al obtener el inputstream")
            content = res.json(cls=CustomJsonDecoder)
            if not content["success"]: raise Exception(content["errorMessage"])
            return Inputstream(from_response=True, **content["data"])
        except Exception as e:
            raise e
        

    def find(self, ikey:str, query:dict) -> dict:
        try:
            print("Downloading data from A2G...")
            hearders = {
                "Authorization": f"A2G {self.token}",
                "ikey": ikey
            }
            res = requests.post(A2G_DATA_URL + "/QueryData/FindAll", json=query, headers=hearders, verify=False)
            if res.status_code != 200: 
                raise Exception(f"Error al obtener el inputstream {res.status_code} {res.content}")
            content = res.json(cls=CustomJsonDecoder)
            if not content["success"]: raise Exception(content["errorMessage"])

            docs:list[dict] = content["data"]["data"]
            total_query     = content["data"]["total"]
            page_size       = content["data"]["size"]
            page            = 2
            downloaded_docs = content["data"]["size"]
            total_batchs    = (total_query // page_size) + 1
            print(f"Total documents to download {total_query}.")
            print(f"Batch 1/{total_batchs}")
            while downloaded_docs < total_query:
                res = requests.post(A2G_DATA_URL + "/QueryData/FindAll", json=query, headers=hearders, verify=False, params={"page": page, "pageSize": page_size})
                if res.status_code != 200: raise Exception(f"Error al descargar datos de inputstream {res.status_code}")
                content = res.json(cls=CustomJsonDecoder)
                if not content["success"]: raise Exception(content["errorMessage"])
                print(f"Batch {page}/{total_batchs}")
                downloaded_docs += content["data"]["size"]
                docs += content["data"]["data"]
                page += 1

            print(f"Data downloaded, total docs: {total_query}")
            return docs
        except Exception as e:
            raise e


    def find_one(self, ikey:str, query:dict) -> list[dict]:
        try:
            hearders = {
                "Authorization": f"A2G {self.token}",
                "ikey": ikey
            }
            res = requests.post(A2G_DATA_URL + "/QueryData/FindOne", headers=hearders, json=query, verify=False)
            if res.status_code != 200: raise Exception("Error al obtener el inputstream")
            content = res.json(cls=CustomJsonDecoder)
            if not content["success"]: raise Exception(content["errorMessage"])
            return content["data"]
        except Exception as e:
            raise e
        

    def aggregate(self, ikey:str, query: list[dict]) -> list[dict]:
        try:
            hearders = {
                "Authorization": f"A2G {self.token}",
                "ikey": ikey
            }
            res = requests.post(A2G_DATA_URL + "/QueryData/Aggregate", headers=hearders, json=query, verify=False)
            if res.status_code != 200: raise Exception("Error al obtener el inputstream")
            content = res.json(cls=CustomJsonDecoder)
            if not content["success"]: raise Exception(content["errorMessage"])
            return content["data"]
        except Exception as e:
            raise e


    def insert(self, ikey:str, data:list[dict]):
        try:
            headers = {
                "Authorization": f"A2G {self.token}",
                "ikey": ikey
            }
            res = requests.post(A2G_DATA_URL + "/Data/Insert", headers=headers, json=data, verify=False)
            if res.status_code != 200: raise Exception("Error al obtener el inputstream")
            return res.status_code, res.text
        except Exception as e:
            raise e


class LocalInputstream:

    def __init__(self, token:str, cache_options:dict = None):
        """
        Constructor for LocalInputstream
        :param token: Token to authenticate with A2G
        :param cache_options: { duration_data: int, duration_inputstream: int } | None
        """        
        self.a2g_client = A2GHttpClient(token) 
        self.cache_manager = CacheManager(cache_options)


    def __get_inputstream(self, ikey:str, cache:bool) -> Inputstream:
        inputstream = self.cache_manager.get_inputstream(ikey) if cache else None 
        if inputstream is None:
            inputstream = self.a2g_client.get_inputstream_by_ikey(ikey)
            self.cache_manager.set_inputstream(inputstream)
        return inputstream
    

    def __get_data(self, ikey:str, query, mode:str, cache:bool) -> list[dict]:
        inputstream = self.__get_inputstream(ikey, cache)
        query_str = json.dumps(query, cls=CustomJSONEncoder)
        query_hash = hashlib.sha256(query_str.encode()).hexdigest()
        data = self.cache_manager.get_data(ikey, query_hash) if cache else None
        if data is None:
            if   mode == "find"     :   data = self.a2g_client.find(ikey, query)
            elif mode == "find_one" :   data = self.a2g_client.find_one(ikey, query)
            elif mode == "aggregate":   data = self.a2g_client.aggregate(ikey, query)
            print(f"Caching data ... ikey: {ikey}, query: {query_str}")
            self.cache_manager.set_data(ikey, query_hash, data)
            print(f"Data - Ikey: {ikey}, Data cached")
        return data


    def get_inputstream_schema(self, ikey:str, cache = True) -> dict:
        """
        return Inputstream schema
        params:
            ikey: str
            cache: bool = True -> if True, use cache if exists and is not expired
        """
        inputstream = self.__get_inputstream(ikey, cache)
        return json.loads(inputstream.Schema)


    def find(self, ikey, query, cache = True):
        """
        return data from inputstream
        params:
            ikey: str
            query: dict
            cache: bool = True -> if True, use cache if exists and is not expired
        """
        mode = "find"
        return self.__get_data(ikey, query, mode, cache)


    def find_one(self, ikey, query:dict, cache = True):
        """
        return one data from inputstream
        params:
            collection: str
            query: dict
        """
        mode = "find_one"
        return self.__get_data(ikey, query, mode, cache)   
     

    def get_data_aggregate(self, ikey:str, query: list[dict], cache = True):
        """
        return data from inputstream
        params:
            ikey: str
            query: list[dict]
        """
        mode = "aggregate"
        return self.__get_data(ikey, query, mode, cache)  
    

    def insert_data(self, ikey:str, data:list[dict], batch_size = 1000, cache = True):
        """
        validate data against inputstream JsonSchema and insert into inputstream collection
        params:
            ikey: str
            data: list[dict]
            cache: bool = True -> if True, use cache if exists and is not expired
        """
        inputstream = self.__get_inputstream(ikey, cache)
        schema = json.loads(inputstream.Schema)
        schema_validator = Draft4Validator(schema=schema)

        data_parsed = json.loads(json.dumps(data, cls=CustomJSONEncoder)) 

        # validate data against schema
        i = 0
        for d in data_parsed: 
            try:
                schema_validator.validate(d)
                i += 1
            except Exception as e:
                print(f"Error validating data: {e}")
                raise e

        # insert data into inputstream collection in batch size of 1000
        # TODO: Optimizar para asyncio
        for i in range(0, len(data_parsed), batch_size):
            code, message = self.a2g_client.insert(ikey, data_parsed[i:i+batch_size])
            print(f"batch {i//batch_size}, docs: [{i} - {i+batch_size}] - {code} - {message}")