from typing import TypedDict, Optional, Any

class Service(TypedDict):
    id: str
    alias: Optional[str]
    name: str
    version: str
    configuration: Any
