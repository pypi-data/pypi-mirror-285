from humps import camelize
from pydantic import BaseModel


def to_camel(string: str) -> str:
    return camelize(string)


class CamelModel(BaseModel):
    class Config:
        alias_generator = to_camel
        populate_by_name = True
