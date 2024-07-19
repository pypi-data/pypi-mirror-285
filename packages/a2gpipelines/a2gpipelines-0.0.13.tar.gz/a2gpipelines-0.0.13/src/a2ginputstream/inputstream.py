import copy
from datetime import datetime
from enum import Enum
from uuid import UUID
from dateutil import parser


# Enums
class FileIndexFieldType(Enum):
    Datetime = 0
    String = 1
    Number = 2
    Integer = 3

class DateBucketSize(Enum):
    Minute = 0
    Hour = 1
    Day = 2
    Week = 3
    Month = 4
    Year = 5

class InputstreamStatus(Enum):
    ToDiscover = 0
    Undiscovered = 1
    Exposed = 2
    ToDiscoverAgain = 3

class InputstreamStorage(Enum):
    Collection = 0
    TimeSeriesCollection = 1
    File = 2

class InputstreamProtocol(Enum):
    MQTT = 0
    HTTP = 1
    BOTH = 2

class RealTimeMode(Enum):
    OFF = 0
    ON = 1

class IndexType(Enum):
    Unique = 0
    Search = 1

class SortType(Enum):
    Ascending = 0
    Descending = 1

# Models
class IndexField:
    Name: str
    FieldType: FileIndexFieldType
    DoubleBucketSize: float
    DateBucketSize: DateBucketSize

    def __init__(self, **kwargs) -> None:
        kwargs["FieldType"] = FileIndexFieldType(kwargs.pop('fieldType'))
        kwargs["DateBucketSize"] = DateBucketSize(kwargs.pop('dateBucketSize'))
        self.__dict__ = kwargs

    def get_dict(self):
        data = copy.deepcopy(self.__dict__)
        return data

class CollectionIndexField:
    Name: str
    SortType: SortType

    def __init__(self, **kwargs) -> None:
        kwargs["sortType"] = SortType(kwargs.pop('sortType'))
        self.__dict__ = kwargs

    def get_dict(self):
        data = copy.deepcopy(self.__dict__)
        return data

class CollectionIndex:
    Name: str
    Fields: list[CollectionIndexField]
    Size: int
    IndexUse: int
    SinceUse: datetime
    IndexType: IndexType
    DateCreated: datetime
    IsCompound: bool

    def __init__(self, **kwargs) -> None:
        kwargs["SinceUse"] = datetime.fromisoformat(kwargs.pop('sinceUse'))
        kwargs["DateCreated"] = datetime.fromisoformat(kwargs.pop('dateCreated'))
        kwargs["Fields"] = [CollectionIndexField(**x) for x in kwargs["fields"]]
        self.__dict__ = kwargs

    def get_dict(self):
        data = copy.deepcopy(self.__dict__)
        data["Fields"] = [x.get_dict() for x in data["Fields"]]
        return data

class Inputstream:
    Id: UUID
    Name: str
    InputstreamCollectionName: str
    Schema: str
    SchemaSample: str
    SampleDate: datetime
    Status: InputstreamStatus
    Tags: list[str]
    Ikey: str
    CollectionIndexes: list[CollectionIndex]
    FilesIndex: list[IndexField]
    Storage: InputstreamStorage
    Protocol: InputstreamProtocol
    RealTimeMode: RealTimeMode
    Size: int
    MaxNDocsByFile: int
    AllowAnyOrigin: bool
    FileConsolidatorCron: str
    Removed: bool
    CreatedOn: datetime
    UpdatedOn: datetime
    DeletedOn: datetime
    LastEnquiry: datetime


    def __init__(self, from_response = False, **kwargs) -> None:
        if from_response: self.from_response(**kwargs)
        else:
            kwargs["Id"] = UUID(kwargs.pop('Id'))

            kwargs["Status"]       = InputstreamStatus(kwargs.pop('Status'))
            kwargs["Storage"]      = InputstreamStorage(kwargs.pop('Storage'))
            kwargs["Protocol"]     = InputstreamProtocol(kwargs.pop('Protocol'))
            kwargs["RealTimeMode"] = RealTimeMode(kwargs.pop('RealTimeMode'))

            kwargs["FilesIndex"]        = [IndexField(**x) for x in kwargs["FilesIndex"]]
            kwargs["CollectionIndexes"] = [CollectionIndex(**x) for x in kwargs["CollectionIndexes"]]

            self.__dict__ = kwargs

    
    def from_response(self, **kwargs) -> None:
        kwargs["Id"]           = UUID(kwargs.pop('id'))

        kwargs["Name"]                      = kwargs.pop('name')
        kwargs["InputstreamCollectionName"] = kwargs.pop('inputstreamCollectionName')
        kwargs["Schema"]                    = kwargs.pop('schema')
        kwargs["SchemaSample"]              = kwargs.pop('schemaSample')
        kwargs["Tags"]                      = kwargs.pop('tags')
        kwargs["Ikey"]                      = kwargs.pop('ikey')
        kwargs["Size"]                      = kwargs.pop('size')
        kwargs["MaxNDocsByFile"]            = kwargs.pop('maxNDocsByFile')
        kwargs["AllowAnyOrigin"]            = kwargs.pop('allowAnyOrigin')
        kwargs["FileConsolidatorCron"]      = kwargs.pop('fileConsolidatorCron')
        kwargs["Removed"]                   = kwargs.pop('removed')

        kwargs["Status"]       = InputstreamStatus(kwargs.pop('status'))
        kwargs["Storage"]      = InputstreamStorage(kwargs.pop('storage'))
        kwargs["Protocol"]     = InputstreamProtocol(kwargs.pop('protocol'))
        kwargs["RealTimeMode"] = RealTimeMode(kwargs.pop('realTimeMode'))

        kwargs["FilesIndex"]        = [IndexField(**x) for x in kwargs["filesIndex"]]
        kwargs["CollectionIndexes"] = [CollectionIndex(**x) for x in kwargs["collectionIndexes"]]

        kwargs["SampleDate"]  = kwargs.pop('sampleDate')  if kwargs.get('sampleDate')  else None
        kwargs["CreatedOn"]   = kwargs.pop('createdOn')   if kwargs.get('createdOn')   else None
        kwargs["UpdatedOn"]   = kwargs.pop('updatedOn')   if kwargs.get('updatedOn')   else None
        kwargs["DeletedOn"]   = kwargs.pop('deletedOn')   if kwargs.get('deletedOn')   else None
        kwargs["LastEnquiry"] = kwargs.pop('lastEnquiry') if kwargs.get('lastEnquiry') else None

        self.__dict__ = kwargs

    def get_dict(self):
        data = copy.deepcopy(self.__dict__)
        data["Id"] = str(data["Id"])
        data["FilesIndex"] = [x.get_dict() for x in self.FilesIndex]
        data["CollectionIndexes"] = [x.get_dict() for x in self.CollectionIndexes]
        return data
