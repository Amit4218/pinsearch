from pydantic import BaseModel
from typing import Dict


class ApplicationSettings(BaseModel):
    title: str = "Pinsearch"
    summary: str = "Search and verify 6-digit Indian PIN codes instantly."
    description: str = "Get accurate address information, including State, District, Region, and geographic coordinates directly from official datasets."
    version: str = "1.0.0"
    contact: Dict[str, str] = {
        "name": "Amit Bhagat",
        "email": "amitbhagat621@gmail.com",
    }
    docs_url: str | None = None
    redoc_url: str | None = None
    openapi_url: str | None = None
    