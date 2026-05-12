from pydantic import BaseModel, ConfigDict

class IgnoredItemCreate(BaseModel):
    market_hash_name: str

class IgnoredItemRead(BaseModel):
    market_hash_name: str

    model_config = ConfigDict(from_attributes=True)

