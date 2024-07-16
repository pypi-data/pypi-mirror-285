"""Tesseract Module for LogicLayer

This module contains an implementation of the :class:`LogicLayerModule` class,
for use with a :class:`LogicLayer` instance.
"""

import dataclasses
import os
from pathlib import Path
from typing import Optional, Union

import logiclayer as ll
from fastapi import Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse

import tesseract_olap as olap
from tesseract_olap.exceptions import QueryError, TesseractError
from tesseract_olap.exceptions.query import NotAuthorized
from tesseract_olap.query import DataQuery, DataRequest, MembersQuery, MembersRequest
from tesseract_olap.schema import TesseractCube, TesseractSchema
from tesseract_olap.server import OlapServer

from .dependencies import auth_token, dataquery_params, membersquery_params
from .response import (
    MembersResModel,
    ResponseFormat,
    data_response,
    members_response,
)

DEBUG_INFO = {
    "git_branch": os.getenv("GIT_BRANCH", ""),
    "git_hash": os.getenv("GIT_HASH", ""),
}


class TesseractModule(ll.LogicLayerModule):
    """Tesseract OLAP server module for LogicLayer.

    It must be initialized with a :class:`logiclayer.OlapServer` instance, but
    can also be created directly with the schema path and the connection string
    using the helper method `TesseractModule.new(connection, schema)`.
    """

    server: OlapServer

    def __init__(self, server: OlapServer, **kwargs):
        super().__init__(**kwargs)
        self.server = server
        self.debug = kwargs.get("debug", False)

    @classmethod
    def new(cls, connection: str, schema: Union[str, Path], cache: str = ""):
        """Creates a new :class:`TesseractModule` instance from the strings with
        the path to the schema file (or the schema content itself), and with the
        connection string to the backend.
        """
        server = OlapServer(backend=connection, schema=schema, cache=cache)
        return cls(server)

    @ll.healthcheck
    def healthcheck(self):
        return self.server.ping()

    @ll.route("GET", "/")
    def module_status(self) -> ll.ModuleStatus:
        """Retrieves operational information about this instance of TesseractModule."""
        return ll.ModuleStatus(
            module=olap.__title__,
            version=olap.__version__,
            debug=DEBUG_INFO if self.debug else False,
            status="ok" if self.server.ping() else "error",
        )

    @ll.route("GET", "/cubes")
    def get_schema(
        self,
        locale: Optional[str] = None,
        token: Optional[ll.AuthToken] = Depends(auth_token),
    ) -> TesseractSchema:
        """Returns the public schema with all the available cubes."""
        roles = self.auth.get_roles(token)
        return TesseractSchema.from_entity(
            self.server.schema, roles=roles, locale=locale
        )

    @ll.route("GET", "/cubes/{cube_name}")
    def get_cube(
        self,
        cube_name: str,
        locale: Optional[str] = None,
        token: Optional[ll.AuthToken] = Depends(auth_token),
    ) -> TesseractCube:
        """Returns the public schema for the single specified cube."""
        roles = self.auth.get_roles(token)
        cube = self.server.schema.get_cube(cube_name)
        if not cube.is_authorized(roles):
            raise NotAuthorized(f"Cube({cube})", roles)
        locale = self.server.schema.default_locale if locale is None else locale
        return TesseractCube.from_entity(cube, locale=locale)

    @ll.route("GET", "/data", deprecated=True, response_class=RedirectResponse)
    def query_data_redirect(self, request: Request):
        """Redirects the request to the canonical endpoint in jsonrecords format."""
        return f"{request.url.path}.jsonrecords?{request.url.query}"

    @ll.route("GET", "/data.{extension}")
    def query_data(
        self,
        extension: ResponseFormat,
        params: DataRequest = Depends(dataquery_params),
        token: Optional[ll.AuthToken] = Depends(auth_token),
    ):
        """Executes a request for data from the server."""
        params.roles = self.auth.get_roles(token)
        query = DataQuery.from_request(self.server.schema, params)
        with self.server.session() as session:
            result = session.fetch_dataframe(query)
        return data_response(params, query, result, extension)

    @ll.route(
        "GET", "/members.{extension}", deprecated=True, response_class=RedirectResponse
    )
    def get_members_redirect(self, request: Request, extension: str):
        """Redirects the request to the canonical endpoint without extension."""
        path = request.url.path.replace(f"members.{extension}", "members")
        return f"{path}?{request.url.query}"

    @ll.route("GET", "/members")
    def get_members(
        self,
        params: MembersRequest = Depends(membersquery_params),
        token: Optional[ll.AuthToken] = Depends(auth_token),
    ) -> MembersResModel:
        """Retrieves detailed information about a level and its members."""
        params.roles = self.auth.get_roles(token)
        query = MembersQuery.from_request(self.server.schema, params)
        with self.server.session() as session:
            result = session.fetch_records(query)
        return members_response(params, query, result)

    @ll.route("GET", "/debug/schema", debug=True)
    def debug_schema(self):
        """Returns the true internal schema, used to validate the requests."""
        return dataclasses.asdict(self.server.raw_schema)

    @ll.exception_handler(TesseractError)
    def exc_tesseracterror(self, request: Request, exc: TesseractError):
        content = {"error": True, "detail": "Backend error"}

        if self.debug:
            content["type"] = type(exc).__name__

        if isinstance(exc, NotAuthorized):
            roles = tuple(exc.roles)
            if len(roles) == 0 or "visitor" in roles:
                exc.code = 401
                wall = "The requested resource needs authorization."
            else:
                exc.code = 403
                wall = "You don't have authorization to access this resource."
            content["detail"] = exc.message if self.debug else wall

        elif isinstance(exc, QueryError):
            content["detail"] = exc.message

        return JSONResponse(content, status_code=exc.code)
