from pydantic import BaseModel, ConfigDict

class STRHeaders(BaseModel):
  Event: str | None = None
  Site: str | None = None
  Date: str | None = None
  Round: str | None = None
  White: str | None = None
  Black: str | None = None
  Result: str | None = None

class PGNHeaders(STRHeaders):
  model_config = ConfigDict(extra='allow')