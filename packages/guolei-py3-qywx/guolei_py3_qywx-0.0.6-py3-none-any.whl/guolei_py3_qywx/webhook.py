#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
=================================================
qywx Webhook Class Library
-------------------------------------------------
作者：[郭磊]
手机：[15210720528]
Email：[174000902@qq.com]
Github：https://github.com/guolei19850528/guolei_py3_qywx
=================================================
"""

from typing import Iterable, Callable

from addict import Dict
from guolei_py3_requests import requests_request, RequestsResponseCallable
from requests import Response


class RequestsResponseCallable(RequestsResponseCallable):
    @staticmethod
    def status_code_200_json_addict_errcode_0_errmsg_ok(response: Response = None):
        json_addict = RequestsResponseCallable.status_code_200_json_addict(response=response)
        return json_addict.errcode == 0 and json_addict.errmsg == "ok"

    @staticmethod
    def status_code_200_json_addict_errcode_0_errmsg_ok_media_id(response: Response = None):
        if RequestsResponseCallable.status_code_200_json_addict_errcode_0_errmsg_ok(response=response):
            return RequestsResponseCallable.status_code_200_json_addict(response=response).media_id


class Api(object):
    """
    企业微信 群机器人 Webhook API Class

    @See https://developer.work.weixin.qq.com/document/path/91770
    """

    def __init__(
            self,
            base_url: str = "https://qyapi.weixin.qq.com/cgi-bin/webhook",
            key: str = "",
            mentioned_list: list = [],
            mentioned_mobile_list: list = []
    ):
        """
        @See https://developer.work.weixin.qq.com/document/path/91770
        :param base_url: base url https://qyapi.weixin.qq.com/cgi-bin/webhook
        :param key: key
        :param mentioned_list: userid的列表，提醒群中的指定成员(@某个成员)，@all表示提醒所有人
        :param mentioned_mobile_list: 手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人
        """
        self._base_url = base_url
        self._key = key
        self._mentioned_list = mentioned_list
        self._mentioned_mobile_list = mentioned_mobile_list

    @property
    def base_url(self) -> str:
        return self._base_url[:-1] if self._base_url.endswith("/") else self._base_url

    @base_url.setter
    def base_url(self, base_url: str = ""):
        self._base_url = base_url

    @property
    def key(self) -> str:
        return self._key

    @key.setter
    def key(self, key: str = ""):
        self._key = key

    @property
    def mentioned_list(self) -> list:
        return self._mentioned_list

    @mentioned_list.setter
    def mentioned_list(self, value: list = []):
        self._mentioned_list = value

    @property
    def mentioned_mobile_list(self) -> list:
        return self._mentioned_mobile_list

    @mentioned_mobile_list.setter
    def mentioned_list(self, value: list = []):
        self._mentioned_mobile_list = value

    def send(
            self,
            requests_request_kwargs_json: dict = None,
            requests_response_callable: Callable = RequestsResponseCallable.status_code_200_json_addict_errcode_0_errmsg_ok,
            requests_request_args: Iterable = (),
            requests_request_kwargs: dict = {}
    ) -> bool:
        """
        send
        :param requests_request_kwargs_json:
        :param requests_response_callable:
        :param requests_request_args:
        :param requests_request_kwargs:
        :return:
        """
        requests_request_kwargs_json = Dict(requests_request_kwargs_json)
        requests_request_kwargs = Dict(requests_request_kwargs)
        requests_request_kwargs = Dict({
            "url": f"{self.base_url}/send",
            "method": "POST",
            "params": {
                "key": self.key,
                **requests_request_kwargs.params,
            },
            "json": {
                **requests_request_kwargs_json,
                **requests_request_kwargs.json
            },
            **requests_request_kwargs,
        })
        return requests_request(
            requests_response_callable=requests_response_callable,
            requests_request_args=requests_request_args,
            requests_request_kwargs=requests_request_kwargs
        )

    def send_text(
            self,
            content: str = "",
            mentioned_list: list = [],
            mentioned_mobile_list: list = [],
            requests_response_callable: Callable = RequestsResponseCallable.status_code_200_json_addict_errcode_0_errmsg_ok,
            requests_request_args: Iterable = (),
            requests_request_kwargs: dict = {}
    ) -> bool:
        """

        :param content:
        :param mentioned_list:
        :param mentioned_mobile_list:
        :param requests_response_callable:
        :param requests_request_args:
        :param requests_request_kwargs:
        :return:
        """
        if not isinstance(content, str) or not len(content):
            raise ValueError(f"content:{content} type must be str and not empty")
        if not isinstance(mentioned_list, list):
            mentioned_list = []
        if not isinstance(mentioned_mobile_list, list):
            mentioned_mobile_list = []
        return self.send(
            requests_request_kwargs_json={
                "msgtype": "text",
                "text": {
                    "content": content,
                    "mentioned_list": self.mentioned_list + mentioned_list,
                    "mentioned_mobile_list": self.mentioned_mobile_list + mentioned_mobile_list,
                }
            },
            requests_response_callable=requests_response_callable,
            requests_request_args=requests_request_args,
            requests_request_kwargs=requests_request_kwargs,
        )

    def send_markdown(
            self,
            content: str = "",
            mentioned_list: list = [],
            mentioned_mobile_list: list = [],
            requests_response_callable: Callable = RequestsResponseCallable.status_code_200_json_addict_errcode_0_errmsg_ok,
            requests_request_args: Iterable = (),
            requests_request_kwargs: dict = {}
    ) -> bool:
        """
        send markdown
        :param content:
        :param mentioned_list:
        :param mentioned_mobile_list:
        :param requests_response_callable:
        :param requests_request_args:
        :param requests_request_kwargs:
        :return:
        """
        if not isinstance(content, str) or not len(content):
            raise ValueError(f"content:{content} type must be str and not empty")
        if not isinstance(mentioned_list, list):
            mentioned_list = []
        if not isinstance(mentioned_mobile_list, list):
            mentioned_mobile_list = []
        return self.send(
            requests_request_kwargs_json={
                "msgtype": "markdown",
                "markdown": {
                    "content": content,
                    "mentioned_list": self.mentioned_list + mentioned_list,
                    "mentioned_mobile_list": self.mentioned_mobile_list + mentioned_mobile_list,
                }
            },
            requests_response_callable=requests_response_callable,
            requests_request_args=requests_request_args,
            requests_request_kwargs=requests_request_kwargs
        )

    def send_file(
            self,
            media_id: str = "",
            mentioned_list: list = [],
            mentioned_mobile_list: list = [],
            requests_response_callable: Callable = RequestsResponseCallable.status_code_200_json_addict_errcode_0_errmsg_ok,
            requests_request_args: Iterable = (),
            requests_request_kwargs: dict = {}
    ) -> bool:
        """
        send file
        :param media_id:
        :param mentioned_list:
        :param mentioned_mobile_list:
        :param requests_response_callable:
        :param requests_request_args:
        :param requests_request_kwargs:
        :return:
        """
        if not isinstance(media_id, str) or not len(media_id):
            raise ValueError(f"media_id:{media_id} type must be str and not empty")
        if not isinstance(mentioned_list, list):
            mentioned_list = []
        if not isinstance(mentioned_mobile_list, list):
            mentioned_mobile_list = []
        return self.send(
            requests_request_kwargs_json={
                "msgtype": "file",
                "file": {
                    "media_id": media_id,
                    "mentioned_list": self.mentioned_list + mentioned_list,
                    "mentioned_mobile_list": self.mentioned_mobile_list + mentioned_mobile_list,
                }
            },
            requests_response_callable=requests_response_callable,
            requests_request_args=requests_request_args,
            requests_request_kwargs=requests_request_kwargs
        )

    def send_voice(
            self,
            media_id: str = "",
            mentioned_list: list = [],
            mentioned_mobile_list: list = [],
            requests_response_callable: Callable = RequestsResponseCallable.status_code_200_json_addict_errcode_0_errmsg_ok,
            requests_request_args: Iterable = (),
            requests_request_kwargs: dict = {}
    ) -> bool:
        """
        send voice
        :param media_id:
        :param mentioned_list:
        :param mentioned_mobile_list:
        :param requests_response_callable:
        :param requests_request_args:
        :param requests_request_kwargs:
        :return:
        """
        if not isinstance(media_id, str) or not len(media_id):
            raise ValueError(f"media_id:{media_id} type must be str and not empty")
        if not isinstance(mentioned_list, list):
            mentioned_list = []
        if not isinstance(mentioned_mobile_list, list):
            mentioned_mobile_list = []
        return self.send(
            requests_request_kwargs_json={
                "msgtype": "voice",
                "voice": {
                    "media_id": media_id,
                    "mentioned_list": self.mentioned_list + mentioned_list,
                    "mentioned_mobile_list": self.mentioned_mobile_list + mentioned_mobile_list,
                }
            },
            requests_response_callable=requests_response_callable,
            requests_request_args=requests_request_args,
            requests_request_kwargs=requests_request_kwargs
        )

    def upload(
            self,
            requests_request_kwargs_files=None,
            requests_request_kwargs_params_files_type: str = "file",
            requests_response_callable: Callable = RequestsResponseCallable.status_code_200_json_addict_errcode_0_errmsg_ok_media_id,
            requests_request_args: Iterable = (),
            requests_request_kwargs: dict = {}
    ) -> str:
        """
        upload file
        :param requests_request_kwargs_files: requests.request(files=requests_request_kwargs_files)
        :param requests_request_kwargs_params_files_type: file or voice
        :param requests_response_callable: RequestsResponseCallable.status_code_200_json_addict_errcode_0_errmsg_ok_media_id
        :param requests_request_args: requests.request(*requests_request_args,**requests_request_kwargs)
        :param requests_request_kwargs: requests.request(*requests_request_args,**requests_request_kwargs)
        :return:
        """
        if not requests_request_kwargs_files:
            raise ValueError(f"requests_request_kwargs_files: {requests_request_kwargs_files} must not empty")
        if not isinstance(requests_request_kwargs_params_files_type, str) or not len(
                requests_request_kwargs_params_files_type):
            requests_request_kwargs_params_files_type = "file"
        requests_request_kwargs = Dict(requests_request_kwargs)
        requests_request_kwargs = Dict({
            "url": f"{self.base_url}/upload_media",
            "method": "POST",
            "params": {
                "key": self.key,
                "type": requests_request_kwargs_params_files_type,
                **requests_request_kwargs.params,
            },
            "files": requests_request_kwargs_files,
            **requests_request_kwargs,
        })
        return requests_request(
            requests_response_callable=requests_response_callable,
            requests_request_args=requests_request_args,
            requests_request_kwargs=requests_request_kwargs
        )
