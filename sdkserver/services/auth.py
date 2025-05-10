from fastapi import APIRouter
from fastapi.responses import JSONResponse

auth_router = APIRouter()


@auth_router.post("/{product_name}/mdk/shield/api/login")
async def login_with_password() -> JSONResponse:
    response_data = {
        "data": {
            "account": {
                "area_code": "**",
                "email": "ReversedRooms",
                "country": "RU",
                "is_email_verify": "1",
                "token": "mostsecuretokenever",
                "uid": "1337",
            },
            "device_grant_required": False,
            "reactivate_required": False,
            "realperson_required": False,
            "safe_mobile_required": False,
        },
        "message": "OK",
        "retcode": 0,
    }
    return JSONResponse(content=response_data)


@auth_router.post("/{product_name}/mdk/shield/api/verify")
async def login_with_session_token() -> JSONResponse:
    response_data = {
        "data": {
            "account": {
                "area_code": "**",
                "email": "ReversedRooms",
                "country": "RU",
                "is_email_verify": "1",
                "token": "mostsecuretokenever",
                "uid": "1337",
            },
            "device_grant_required": False,
            "reactivate_required": False,
            "realperson_required": False,
            "safe_mobile_required": False,
        },
        "message": "OK",
        "retcode": 0,
    }
    return JSONResponse(content=response_data)


@auth_router.post("/{product_name}/combo/granter/login/v2/login")
async def granter_login_verification() -> JSONResponse:
    response_data = {
        "data": {
            "account_type": 1,
            "combo_id": "1337",
            "combo_token": "9065ad8507d5a1991cb6fddacac5999b780bbd92",
            "data": '{"guest":false}',
            "heartbeat": False,
            "open_id": "1337",
        },
        "message": "OK",
        "retcode": 0,
    }
    return JSONResponse(content=response_data)


@auth_router.post("/account/risky/api/check")
async def risky_api_check() -> JSONResponse:
    response_data = {
        "data": {
            "id": "06611ed14c3131a676b19c0d34c0644b",
            "action": "ACTION_NONE",
            "geetest": None,
        },
        "message": "OK",
        "retcode": 0,
    }
    return JSONResponse(content=response_data)
