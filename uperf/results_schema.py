import pydantic
import datetime

class Uperf_Results(pydantic.BaseModel):
    number_procs: int = pydantic.Field(gt=0)
    Bandwidth_Gb_sec: float = pydantic.Field(gt=0, allow_inf_nan=False)
    test: str
    packet: str
    packet_size: int = pydantic.Field(gt=0)
    Start_Date: datetime.datetime
    End_Date: datetime.datetime
