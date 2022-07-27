from abc import ABC, abstractmethod

import attr


@attr.s(auto_attribs=True)
class INoSqlDatabase(ABC):

    @abstractmethod
    def add_data_from_json(
            self,
            json,
            json_schema
    ):
        ...


@attr.s(auto_attribs=True)
class IMongodb(INoSqlDatabase):

    def add_data_from_json(
            self,
            json,
            json_schema
    ):
        pass


