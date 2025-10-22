# resources/models.py
from dataclasses import dataclass, field, fields
from typing import Any, Type, TypeVar, List, Optional

T = TypeVar("T", bound="BaseModel")


@dataclass
class BaseModel:
    @classmethod
    def from_dict(cls: Type[T], data: Any) -> T:
        # If data is a list, recursively convert each element
        if isinstance(data, list):
            return [cls.from_dict(item) for item in data]  # type: ignore

        if not isinstance(data, dict):
            raise ValueError(f"Expected dict or list, got {type(data)}")

        init_kwargs = {}
        for f in fields(cls):
            key = f.name
            value = data.get(key)

            # Recursively convert dict to dataclass if type is BaseModel
            if isinstance(f.type, type) and issubclass(f.type, BaseModel) and isinstance(value, dict):
                value = f.type.from_dict(value)
            # Handle lists of BaseModel
            elif getattr(f.type, "__origin__", None) == list and isinstance(value, list):
                inner_type = f.type.__args__[0]
                if isinstance(inner_type, type) and issubclass(inner_type, BaseModel):
                    value = [inner_type.from_dict(v) for v in value]
            init_kwargs[key] = value
        return cls(**init_kwargs)


@dataclass
class Guild(BaseModel):
    id: str
    guild: str
    owner: str
    name: str
    is_active: bool

@dataclass
class User(BaseModel):
    id: str
    user: str
    is_active: bool

@dataclass
class Level(BaseModel):
    id: str
    guild: Guild
    user: User
    level: int
    experience: int