# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function:
import abc
import time
import uuid
from typing import (
    Any,
)
from typing_extensions import Annotated, Doc
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import iterate_in_threadpool

from zhousflib.web.fastapi.log import Logger
from zhousflib.web.fastapi.exceptions import EXCEPTION_HANDLERS

"""
from pathlib import Path

from fastapi import FastAPI
from zhousflib.web.fastapi.server import App

from my_log import Loggers


ML_MODELS = {}


class Application(App):

    def __init__(self):
        super().__init__(logger=Loggers, show_docs=False, models=ML_MODELS)

    def init_plugins(self, app: FastAPI, models: dict, exception_handler: dict):
        from fastapi.staticfiles import StaticFiles
        app.mount('/static', StaticFiles(directory=Path(__file__).parent.joinpath("app").joinpath("static")), name='static')


app_sim = Application()

if __name__ == "__main__":
    app_sim.start(app="my_app:app_sim", host="0.0.0.0", port=5006, access_log=True, workers=1)
    
"""


class App(FastAPI, metaclass=abc.ABCMeta):

    def __init__(self, logger: Logger, models: dict, show_docs=True, **extra: Annotated[
        Any,
        Doc(
            """
            Extra keyword arguments to be stored in the app, not used by FastAPI
            anywhere.
            """
        ),
    ]):
        extra["lifespan"] = self.lifespan
        extra["exception_handlers"] = EXCEPTION_HANDLERS
        if not show_docs:
            extra["docs_url"] = None
            extra["redoc_url"] = None
            extra["openapi_url"] = None
        super().__init__(**extra)
        self.logger = logger.logger
        self.models = models
        logger.init_config()

        @self.get("/")
        async def welcome():
            return JSONResponse(content={"message": "hallo!"})

        @self.get("/favicon.ico")
        async def get_favicon():
            return JSONResponse(content={"file": "static/favicon.ico"})

        @self.middleware("http")
        async def interception(request: Request, call_next):
            start_time = time.time()
            request_id = str(uuid.uuid4())
            with self.logger.contextualize(request_id=request_id):
                self.logger.info("\n")
                self.logger.info(f"【request url】: {request.url.path}")
                body = await request.body()
                if body:
                    # noinspection PyBroadException
                    try:
                        body_json = await request.json()
                        self.logger.info(f"【request body】: {body_json}")
                    except Exception as e:
                        pass
                response = await call_next(request)
                elapsed_time = f"{time.time() - start_time:.5f}"
                if len(response.headers) > 0:
                    content_type = response.headers.get("content-type", "")
                    content_disposition = response.headers.get("content-disposition", None)
                    if content_type == "application/json" and content_disposition is None:
                        response_body = [chunk async for chunk in response.body_iterator]
                        response.body_iterator = iterate_in_threadpool(iter(response_body))
                        if len(response_body) > 0:
                            self.logger.info(f"【response body】: {response_body[0].decode()}")
                response.headers["X-Process-Time"] = elapsed_time
                self.logger.info(f"【X-Process-Time】: {elapsed_time}s")
            return response

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        self.logger.info("init plugins.")
        self.init_plugins(app, self.models, EXCEPTION_HANDLERS)
        yield
        self.models.clear()

    @abc.abstractmethod
    def init_plugins(self, app: FastAPI, models: dict, exception_handler: dict):
        pass

    @staticmethod
    def start(app: str, host="0.0.0.0", port=5006, workers=1, **kw):
        import uvicorn
        kw["app"] = app
        kw["host"] = host
        kw["port"] = port
        kw["workers"] = workers
        config = uvicorn.Config(**kw)
        server = uvicorn.Server(config)
        server.run()


