# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function:
from starlette.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


async def global_exception_handler(request, exc):
    if exc.status_code == 500:
        err_msg = 'Server Internal Error'
    else:
        err_msg = exc.detail
    return JSONResponse({
        'resultCode': exc.status_code,
        'errorString': err_msg,
        'status': 'Failed'
    })


async def validate_exception_handler(request, exc):
    return JSONResponse({
        'resultCode': 400,
        'errorString': exc.errors(),
        'status': 'Failed'
    })


EXCEPTION_HANDLERS = {
    HTTPException: global_exception_handler,
    RequestValidationError: validate_exception_handler
}
