import typing as _typing
from typing import Optional as _Optional, List as _List
import urllib.parse as _parse

import requests as _requests

from .. import schemas as _schemas
from ..config import Config as _Config
from ..connection.fetch import FetchModule as _FetchModule
import datetime


class SnapshotModule:
    def __init__(
        self, config: _Config, fetcher: _FetchModule, api_key: str = None
    ) -> None:
        """
        :param config: from here config values will be read: `config.DP_URL`
        :param fetcher: will use this object for fetching: `fetcher._request_or_repeat(...)`
        """
        self.config = config
        self.fetcher = fetcher
        self.API_KEY = api_key

    def __get_snapshot_url(self, path: str):
        """path will be joined with dp url"""
        # appending "/" to root so path gets joined, not overwriten
        # >>> "http://q.w/r" == _parse.urljoin("http://q.w/e", "r")
        # >>> "http://q.w/e/r" == _parse.urljoin("http://q.w/e" + "///////", "r")
        url = _parse.urljoin(
            self.config.DP_URL + "/", self.config.BACKEND_SNAPSHOT_PATH
        )
        api_url = _parse.urljoin(url + "/", path)

        if self.API_KEY is not None:
            params = {"api_key": self.API_KEY}
            api_url = api_url + "?" + _parse.urlencode(params)

        return api_url

    def get_meta_by_id(self, snapshot_id: int) -> _schemas.SnapshotMeta:
        "gets meta info about snapshot (by snapshot id)"

        response = self.fetcher._request_or_repeat(
            _requests.get, url=self.__get_snapshot_url(f"{snapshot_id}/head")
        )
        self.fetcher._response_ok_or_raise(response)
        return _schemas.SnapshotMeta(**response.json())

    def __get_result_by_url_or_id(
        self,
        *,
        is_loadable: _Optional[bool] = None,
        result_file_url: _Optional[str] = None,
        snapshot_id: _Optional[int] = None,
    ) -> _typing.Any:
        "gets snapshot result by file url or id. if result is not loadable, {} will be returned"
        if result_file_url is None and snapshot_id is None:
            raise ValueError(
                "Cant get snapshot result without args. Please give file url of snapshot data or snapshot_id"
            )
        if is_loadable == False:
            # why bother downloading if it will be blank / corrupted / etc. ?
            # or should exception be raised?
            return {}
        is_preview = False
        if result_file_url is None:
            is_preview = True  # response will have to be unwrapped
            # maybe old snapshot, so ask for preview, expecting to get full snapshot result
            result_file_url = self.__get_snapshot_url(f"{snapshot_id}/preview")
        response = self.fetcher._request_or_repeat(_requests.get, url=result_file_url)
        self.fetcher._response_ok_or_raise(response)
        return (
            response.json() if not is_preview else response.json()["json_data_preview"]
        )

    def get_result_by_id(self, snapshot_id: int) -> _typing.Any:
        "gets snapshot result by snapshot id. result might be any type but usually it is a list of objects"
        # get meta
        meta = self.get_meta_by_id(snapshot_id)
        # now result
        return self.__get_result_by_url_or_id(
            is_loadable=meta.is_result_json_loadable,
            result_file_url=meta.result_file_url,
            snapshot_id=snapshot_id,
        )

    def get_by_id(self, snapshot_id: int) -> _schemas.Snapshot:
        "gets snapshot meta + snapshot result as a whole object. snapshot result is placed inside `result` attribute"
        meta = self.get_meta_by_id(snapshot_id)
        return _schemas.Snapshot(
            **meta.dict(),
            result=self.__get_result_by_url_or_id(
                is_loadable=meta.is_result_json_loadable,
                result_file_url=meta.result_file_url,
                snapshot_id=snapshot_id,
            ),
        )

    def __raise_if_not_implemented_filter(
        self,
        *,
        by_is_verified: _Optional[bool] = None,
        by_validation_statuses: _Optional[_List[str]] = None,
        **_,
    ) -> None:
        "raises NotImplemented if one of the filters is not implemented"
        if by_is_verified is not None:
            raise NotImplementedError("Sorry, filter is_verified not implemented")
        elif by_validation_statuses is not None:
            raise NotImplementedError(
                "Sorry, filter validation_statuses not implemented"
            )

    def __args_to_filter_params(
        self,
        *,
        by_challenge_id: _Optional[int] = None,
        by_user_id: _Optional[int] = None,
        by_is_verified: _Optional[bool] = None,
        by_validation_statuses: _Optional[_List[str]] = None,
        by_is_from_robot: _Optional[bool] = None,
        **_,
    ) -> dict:
        "remaps kwargs so key names match backend names"
        return {
            "challenge_id": by_challenge_id,
            "user_id": by_user_id,
            "is_verified": by_is_verified,
            "validation_statuses": by_validation_statuses,
            "is_from_code_run": by_is_from_robot,
        }

    def get_latest_meta(
        self,
        by_challenge_id: _Optional[int] = None,
        *,
        by_user_id: _Optional[int] = None,
        by_is_verified: _Optional[bool] = None,
        by_validation_statuses: _Optional[_List[str]] = None,
        by_is_from_robot: _Optional[bool] = None,
        max_stale_days: _Optional[int] = None,
    ) -> _schemas.SnapshotMeta:
        """gets latest snapshot meta by specified filters.

        :param by_challenge_id: to what challenge shall snapshot belong? If None, any will match.
        :param by_user_id: to what user shall snapshot belong? If None, any will match.
        :param by_is_verified: shall the snapshot be moderator-approved? If None, any will match.
        :param by_validation_statuses: searched statuses of snapshot validation. If None, any will match.
        :param by_is_from_robot: shall the snapshot be generated from robot code run (True) or uploaded by human (False)? If None, any will match.
        """
        # check, is each filter supported / implemented.
        # at this point locals() will have dict of supplied args and their values
        # using __class__ so we can reuse self=smth from **locals()
        self.__class__.__raise_if_not_implemented_filter(**locals())
        response = self.fetcher._request_or_repeat(
            _requests.get,
            url=self.__get_snapshot_url("latest/head/"),
            params=self.__class__.__args_to_filter_params(**locals()),
        )
        self.fetcher._response_ok_or_raise(response)
        meta = _schemas.SnapshotMeta(**response.json())

        if max_stale_days is not None and meta.date_created is not None:
            if (datetime.datetime.now() - meta.date_created).days > max_stale_days:
                raise ValueError(
                    f"Snapshot is too old. It was created {meta.date_created}."
                )
        return meta

    def get_latest_result(
        self,
        by_challenge_id: _Optional[int] = None,
        *,
        by_user_id: _Optional[int] = None,
        by_is_verified: _Optional[bool] = None,
        by_validation_statuses: _Optional[_List[str]] = None,
        by_is_from_robot: _Optional[bool] = None,
        max_stale_days: _Optional[int] = None,
    ) -> _typing.Any:
        """gets latest snapshot result by specified filters

        :param by_challenge_id: to what challenge shall snapshot belong? If None, any will match.
        :param by_user_id: to what user shall snapshot belong? If None, any will match.
        :param by_is_verified: shall the snapshot be moderator-approved? If None, any will match.
        :param by_validation_statuses: searched statuses of snapshot validation. If None, any will match.
        :param by_is_from_robot: shall the snapshot be generated from robot code run (True) or uploaded by human (False)? If None, any will match.
        """
        # at this point locals() will have dict of supplied args and their values
        # using __class__ so we can reuse self=smth from **locals()
        meta = self.__class__.get_latest_meta(**locals())
        return self.__get_result_by_url_or_id(
            is_loadable=meta.is_result_json_loadable,
            result_file_url=meta.result_file_url,
            snapshot_id=meta.id,
        )

    def get_latest(
        self,
        by_challenge_id: _Optional[int] = None,
        *,
        by_user_id: _Optional[int] = None,
        by_is_verified: _Optional[bool] = None,
        by_validation_statuses: _Optional[_List[str]] = None,
        by_is_from_robot: _Optional[bool] = None,
        max_stale_days: _Optional[int] = None,
    ) -> _schemas.Snapshot:
        """gets latest snapshot meta+result by specified filters. result is stored inside `result` attribute

        :param by_challenge_id: to what challenge shall snapshot belong? If None, any will match.
        :param by_user_id: to what user shall snapshot belong? If None, any will match.
        :param by_is_verified: shall the snapshot be moderator-approved? If None, any will match.
        :param by_validation_statuses: searched statuses of snapshot validation. If None, any will match.
        :param by_is_from_robot: shall the snapshot be generated from robot code run (True) or uploaded by human (False)? If None, any will match.
        """
        # at this point locals() will have dict of supplied args and their values
        # using __class__ so we can reuse self=smth from **locals()
        meta = self.__class__.get_latest_meta(**locals())
        return _schemas.Snapshot(
            **meta.dict(),
            result=self.__get_result_by_url_or_id(
                is_loadable=meta.is_result_json_loadable,
                result_file_url=meta.result_file_url,
                snapshot_id=meta.id,
            ),
        )
