from pydantic import BaseModel
from pinsearch_sdk import PincodeData
from typing import List, Optional

class PincodeNotFound(BaseModel):
    message: str


class PublicApiResponse(BaseModel):
    pincode_data:  Optional[PincodeData] = None
    state_data:    Optional[List[PincodeData]] = None
    district_data: Optional[List[PincodeData]] = None