"""Resource client for obtaining an access token.
"""
import json
import os
from collections import UserDict
from datetime import datetime as dt
from typing import Any, Dict, List

import iso8601
import requests

from ..client import Client
from .resource import ResourceClient


class TokenStorage(UserDict):
    """
    Dict based persistent storage for access tokens. Initializes the cache
    only with the valid (not expired) tokens and persists tokens on each
    call to create.
    """

    def __init__(self, tokens_file: str):
        self.tokens_file = tokens_file

        # if the tokens file is empty, it implies that the user has chosen
        # not to cache tokens, so this class just acts as an in memory dict
        if self.tokens_file == "":
            super().__init__()
            return

        try:
            with open(
                self.tokens_file, mode="r", encoding="utf-8"
            ) as tokens_fd:
                persisted_tokens = json.loads(tokens_fd.read())
                valid_tokens = {
                    token_id: persisted_tokens[token_id]
                    for token_id in persisted_tokens
                    if iso8601.parse_date(
                        persisted_tokens[token_id]["validUntil"]
                    ).timestamp()
                    > dt.now().timestamp()
                }

                super().__init__(valid_tokens)
        except FileNotFoundError:
            super().__init__()

    def __delitem__(self, key) -> None:
        super().__delitem__(key)
        self._write()

    def __setitem__(self, __key, __value) -> None:
        super().__setitem__(__key, __value)
        self._write()

    def _write(self):
        """write the tokens to persistent file"""

        if self.tokens_file == "":
            return

        tokens_path = os.path.dirname(self.tokens_file)
        # create directory if needed.
        try:
            os.mkdir(tokens_path)
        except OSError:
            pass  # ignore error creating directory.

        tokens_blob = json.dumps(self.data, sort_keys=True, indent=4)

        def opener(path, flags):
            return os.open(path, flags, 0o600)

        with open(
            self.tokens_file, mode="w", encoding="utf-8", opener=opener
        ) as tokens_file:
            print(tokens_blob, file=tokens_file)


class NoValidTokenException(Exception):
    """
    Exception for when there is no valid token in cache and you
    cannot retrieve/create more.
    """

    def __init__(self, *args: object) -> None:
        super().__init__("no valid token in cache", *args)


class AccessTokenClient(ResourceClient):
    """AccessTokenClient is used to obtain access tokens to
    authenticate to databases.
    """

    def __init__(
        self,
        cyral_client: Client,
        cache_tokens: bool = True,
        automatically_create: bool = True,
    ):
        super().__init__(cyral_client)
        tokens_file = ""
        if cache_tokens:
            tokens_file = os.path.join(
                "~", ".cyral", f".{cyral_client.cp_address}.tokens"
            )
            tokens_file = os.path.expanduser(tokens_file)
        self.token_cache = TokenStorage(tokens_file)
        self.automatically_create = automatically_create

    def _get_legacy(self) -> str:
        """
        retrieves the access token from the legacy route.
        """
        resp = self.do_get("/v1/opaqueToken/accessToken")

        # we check if the token has an ID because on the legacy route
        # there is no concept of token ID, so if the response has
        # an ID it means we are dealing with the new access token
        if "id" in resp:
            self.token_cache[resp["id"]] = resp
            return resp["accessToken"]
        return resp["accessToken"]

    def get(self, uuid: str = "") -> str:
        """
        retrieves a valid access token from the cache and prints
        its value. If no valid access token is cached, attempts
        to retrieve the token from the legacy token route. This
        will create a token automatically with the default
        parameters if there is a possibility of creating one.
        If it fails, raises NoValidTokenException.
        """
        try:
            return self.show(uuid)
        except NoValidTokenException:
            if self.automatically_create and not uuid:
                try:
                    token = self.create_token()
                    return token["accessToken"]
                except requests.exceptions.HTTPError as err:
                    if (
                        err.response is not None
                        and err.response.status_code
                        == requests.codes["not_found"]
                    ):
                        return self._get_legacy()
                    raise
        raise NoValidTokenException

    def show(self, uuid: str = "") -> str:
        """
        retrieves a valid access token from the cache.
        """

        if not uuid:
            for token in self.token_cache.data.values():
                return token["accessToken"]

        elif uuid in self.token_cache.data:
            return self.token_cache.data["accessToken"]

        raise NoValidTokenException

    def create_token(
        self,
        validity: int = 0,
        name: str = f"cyral-cli-{dt.now().strftime('%Y%m%d%H%M%S')}",
    ) -> Dict[str, Any]:
        """
        creates an access token with the given validity and name.
        The validity is in number of seconds.
        """
        data = {}
        if validity != 0:
            data["validity"] = f"{validity}s"
        if name != "":
            data["name"] = name

        token = self.do_post("/v1/accessTokens/tokens", data)
        self.token_cache[token["id"]] = token
        return token

    def list_tokens(self) -> List[Dict[str, Any]]:
        """
        lists the user's access tokens and informs whether they are
        cached or not.
        """
        tokens = self.do_get("/v1/accessTokens/tokens")["accessTokens"]
        for token in tokens:
            if token["id"] in self.token_cache.data:
                token["cached"] = True
        return tokens

    def delete_token(self, token_id: str):
        """
        deletes an access token
        """
        self.do_delete(f"/v1/accessTokens/tokens/{token_id}")
        if token_id in self.token_cache:
            del self.token_cache[token_id]
