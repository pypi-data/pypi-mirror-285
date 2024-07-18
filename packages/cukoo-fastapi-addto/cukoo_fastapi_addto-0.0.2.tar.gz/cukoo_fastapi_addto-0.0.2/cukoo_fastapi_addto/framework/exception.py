# -*- encoding: utf-8 -*-
'''
@File    :   _exception.py
@Time    :   2023-08-01 09:00:00
@Author  :   phailin791 
@Version :   1.0
@Contact :   phailin791@hotmail.com
'''

import traceback
from loguru import logger
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from cukoo_fastapi_addto.framework import custom_exception

def init_exception(app: FastAPI):
    # catch custom Exception
    @app.exception_handler(custom_exception.ParamError)
    async def request_param_exception_handler(request: Request, exc: custom_exception.ParamError):
        """
            custom exception of param exception
        """
        logger.error(f"400_param_exception\n - URL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"code": 10400, "data": "", "message": exc.message},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
            custom exception of validator exception 
        """
        logger.error(f"400_validator_exception\n - URL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder({"code": 10400, "data": "", "body": exc.body, "message": exc.errors()}),
        )

    @app.exception_handler(custom_exception.TokenError)
    async def token_exception_handler(request: Request, exc: custom_exception.TokenError):
        """
            custom exception of token exception
        """
        logger.error(f"401_token_exception\n - URL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"code": 10401, "data": None, "message": exc.message},
        )

    @app.exception_handler(custom_exception.NotFound)
    async def not_found_exception_handler(request: Request, exc: custom_exception.NotFound):
        """
            custom exception of 404
        """
        logger.error(f"404_not_found_exception\n - URL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
        return JSONResponse(
             status_code=status.HTTP_404_NOT_FOUND,
             content={"code": 10404, "data": "", "message": exc.message}
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """
            global exception
        """
        logger.error(f"500_global_exception\n - URL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 10500, "data": "", "message": "Internal Server Error"},
        )