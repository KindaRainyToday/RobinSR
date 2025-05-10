from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from common.sr_tools import FreesrData, FREESR_FILE
from common.util import AsyncFs
from typing import Optional


class SrToolDataReq(BaseModel):
    data: Optional[FreesrData] = None


class SrToolDataRsp(BaseModel):
    message: str = "OK"
    status: int = 200


sr_tools_router = APIRouter()


## handled by cors middleware :D
# @sr_tools_router.options("/srtools")
# async def srtools_options() -> JSONResponse:
#     return JSONResponse(content=SrToolDataRsp().model_dump_json())


@sr_tools_router.post("/srtools")
async def srtools_save(req: SrToolDataReq) -> JSONResponse:
    if data := req.data:
        data_to_save = data.model_dump_json()
        await AsyncFs.write_to_file(FREESR_FILE, data_to_save)
    return JSONResponse(content=SrToolDataRsp().model_dump_json())
