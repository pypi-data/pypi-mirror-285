import json

from typing import Type, Dict
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseEventRecord:
    id = Column(Integer, primary_key=True, autoincrement=True)

    @classmethod
    def from_dict(cls: Type[Base], data: Dict):
        data = cls._parse_dict(data)

        if "id" not in data:
            data["id"] = None

        return cls(**data)

    @classmethod
    def _parse_dict(cls, data: Dict) -> Dict:
        raise NotImplementedError("Abstract method not overriden")

    @classmethod
    def from_json(cls, json_data: str):
        return cls.from_dict(json.loads(json_data))

    def _to_dict(self, *args, **kwargs):
        raise NotImplementedError("Abstract base implementation")

    def to_dict(self, *args, **kwargs):
        data = {
            "id": self.id,
        }

        data.update(self._to_dict(*args, **kwargs))

        return data

    def to_json(self):
        return json.dumps(self.to_dict())

    def __repr__(self):
        return self.to_json()

    def __str__(self):
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)
