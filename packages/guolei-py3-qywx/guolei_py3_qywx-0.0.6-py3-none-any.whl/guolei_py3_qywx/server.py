#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
=================================================
qywx Server Class Library
-------------------------------------------------
作者：[郭磊]
手机：[15210720528]
Email：[174000902@qq.com]
Github：https://github.com/guolei19850528/guolei_py3_qywx
=================================================
"""
import hashlib
from datetime import timedelta
from typing import Union, Callable, Iterable

import redis
from addict import Dict
from diskcache import Cache
from guolei_py3_requests import requests_request, RequestsResponseCallable
from requests import Response


class RequestsResponseCallable(RequestsResponseCallable):
    @staticmethod
    def status_code_200_json_addict_errcode_0_errmsg_ok(response: Response = None):
        json_addict = RequestsResponseCallable.status_code_200_json_addict(response=response)
        return json_addict.errcode == 0 and json_addict.errmsg == "ok"

    @staticmethod
    def status_code_200_json_addict_errcode_0(response: Response = None):
        json_addict = RequestsResponseCallable.status_code_200_json_addict(response=response)
        return json_addict.errcode == 0

    @staticmethod
    def status_code_200_json_addict_errcode_0_media_id(response: Response = None):
        if RequestsResponseCallable.status_code_200_json_addict_errcode_0(response=response):
            return RequestsResponseCallable.status_code_200_json_addict(response=response).media_id

    @staticmethod
    def status_code_200_json_addict_errcode_0_url(response: Response = None):
        if RequestsResponseCallable.status_code_200_json_addict_errcode_0(response=response):
            return RequestsResponseCallable.status_code_200_json_addict(response=response).url

    @staticmethod
    def status_code_200_json_addict_errcode_0_errmsg_ok_access_token(response: Response = None):
        if RequestsResponseCallable.status_code_200_json_addict_errcode_0_errmsg_ok(response=response):
            return RequestsResponseCallable.status_code_200_json_addict(response=response).access_token


class Api(object):
    def __init__(
            self,
            base_url: str = "https://qyapi.weixin.qq.com",
            corp_id: str = "",
            agent_id: str = "",
            secret: str = "",
            diskcache: Cache = None,
            strict_redis: redis.StrictRedis = None
    ):
        self._base_url = base_url
        self._corp_id = corp_id
        self._secret = secret
        self._agent_id = agent_id
        self._diskcache = diskcache
        self._strict_redis = strict_redis
        self._access_token = ""

    @property
    def base_url(self):
        return self._base_url[:-1] if self._base_url.endswith("/") else self._base_url

    @base_url.setter
    def base_url(self, value):
        self._base_url = value

    @property
    def corp_id(self):
        return self._corp_id

    @corp_id.setter
    def corp_id(self, value):
        self._corp_id = value

    @property
    def secret(self):
        return self._secret

    @secret.setter
    def secret(self, value):
        self._secret = value

    @property
    def agent_id(self):
        return self._agent_id

    @agent_id.setter
    def agent_id(self, value):
        self._agent_id = value

    @property
    def diskcache(self):
        return self._diskcache

    @diskcache.setter
    def diskcache(self, value):
        self._diskcache = value

    @property
    def strict_redis(self):
        return self._strict_redis

    @strict_redis.setter
    def strict_redis(self, value):
        self._strict_redis = value

    @property
    def access_token(self):
        return self._access_token

    def get_access_token(
            self,
            requests_request_kwargs_params: dict = {},
            requests_response_callable: Callable = RequestsResponseCallable.status_code_200_json_addict_errcode_0_errmsg_ok_access_token,
            requests_request_args: Iterable = (),
            requests_request_kwargs: dict = {}
    ):
        requests_request_kwargs = Dict(requests_request_kwargs)
        requests_request_kwargs = Dict({
            "url": f"{self.base_url}/cgi-bin/gettoken",
            "method": "GET",
            "params": {
                "corpid": self.corp_id,
                "corpsecret": self.secret,
                **requests_request_kwargs_params,
            },
            **requests_request_kwargs,
        })
        return requests_request(
            requests_response_callable=requests_response_callable,
            requests_request_args=requests_request_args,
            requests_request_kwargs=requests_request_kwargs
        )

    def access_token_with_strict_redis(self, strict_redis: redis.StrictRedis = None):
        """
        使用redis.StrictRedis,获取访问凭证
        :param strict_redis: redis.StrictRedis class instance if strict_redis is None or type not redis.StrictRedis use self.strict_redis
        :return:
        """
        # 缓存key
        cache_key = "_".join([
            f"guolei_py3_qywx_server",
            f"redis",
            f"access_token",
            f"{hashlib.md5(self.base_url.encode('utf-8')).hexdigest()}",
            f"{self.corp_id}",
            f"{self.agent_id}",
        ])
        if strict_redis is None or not isinstance(strict_redis, redis.StrictRedis):
            strict_redis = self.strict_redis
        if isinstance(strict_redis, redis.StrictRedis):
            self._access_token = strict_redis.get(cache_key)
        if not isinstance(self._access_token, str) or not len(self._access_token):
            self._access_token = self.get_access_token()
            if isinstance(strict_redis, redis.StrictRedis):
                strict_redis.setex(name=cache_key, value=self.access_token, time=timedelta(seconds=7100))
        return self

    def access_token_with_diskcache(self, cache: Cache = None):
        """
        使用diskcache,获取访问凭证
        :param cache: diskcache.core.Cache class instance if None or type not diskcache.core.Cache use self.diskcache
        :return: self
        """
        # 缓存key
        cache_key = "_".join([
            f"guolei_py3_qywx_server",
            f"diskcache",
            f"access_token",
            f"{hashlib.md5(self.base_url.encode('utf-8')).hexdigest()}",
            f"{self.corp_id}",
            f"{self.agent_id}",
        ])
        if cache is None or not isinstance(cache, Cache):
            cache = self.diskcache
        if isinstance(cache, Cache):
            self._access_token = cache.get(key=cache_key, default="")
        if not isinstance(self._access_token, str) or not len(self._access_token):
            self._access_token = self.get_access_token()
            if isinstance(cache, Cache):
                cache.set(key=cache_key, value=self.access_token, expire=timedelta(seconds=7100).total_seconds())
        return self

    def access_token_with_cache(self, cache_type: str = "diskcache", cache: Union[Cache, redis.StrictRedis] = None):
        """
        使用缓存 获取访问凭证
        :param cache_type: diskcache=login_with_diskcache(cache),strict_redis=login_with_strict_redis(cache)
        :param cache: diskcache.core.Cache or redis.StrictRedis
        :return:
        """
        if isinstance(cache_type, str) and cache_type.lower() in ["disk_cache".lower(), "diskcache".lower(),
                                                                  "disk".lower()]:
            return self.access_token_with_diskcache(cache=cache)
        if isinstance(cache_type, str) and cache_type.lower() in ["strict_redis".lower(), "strictredis".lower(),
                                                                  "redis".lower()]:
            return self.access_token_with_strict_redis(strict_redis=cache)
        self._access_token = self.get_access_token()
        return self

    def message_send(
            self,
            requests_request_kwargs_json: dict = {},
            requests_response_callable: Callable = RequestsResponseCallable.status_code_200_json_addict_errcode_0_errmsg_ok,
            requests_request_args: Iterable = (),
            requests_request_kwargs: dict = {}
    ):
        requests_request_kwargs = Dict(requests_request_kwargs)
        requests_request_kwargs = Dict({
            "url": f"{self.base_url}/cgi-bin/message/send",
            "method": "POST",
            "params": {
                "access_token": self.access_token,
                **requests_request_kwargs.params,
            },
            "json": {
                "agentid": self.agent_id,
                **requests_request_kwargs_json,
                **requests_request_kwargs.json,
            },
            **requests_request_kwargs,
        })
        return requests_request(
            requests_response_callable=requests_response_callable,
            requests_request_args=requests_request_args,
            requests_request_kwargs=requests_request_kwargs
        )

    def upload(
            self,
            requests_request_kwargs_files=None,
            requests_request_kwargs_params_files_type: str = "file",
            requests_response_callable: Callable = RequestsResponseCallable.status_code_200_json_addict_errcode_0_media_id,
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
            "url": f"{self.base_url}/cgi-bin/media/upload",
            "method": "POST",
            "params": {
                "access_token": self.access_token,
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

    def upload_img(
            self,
            requests_request_kwargs_files=None,
            requests_response_callable: Callable = RequestsResponseCallable.status_code_200_json_addict_errcode_0_url,
            requests_request_args: Iterable = (),
            requests_request_kwargs: dict = {}
    ) -> str:
        """
        upload img
        :param requests_request_kwargs_files: requests.request(files=requests_request_kwargs_files)
        :param requests_response_callable: RequestsResponseCallable.status_code_200_json_addict_errcode_0_errmsg_ok_media_id
        :param requests_request_args: requests.request(*requests_request_args,**requests_request_kwargs)
        :param requests_request_kwargs: requests.request(*requests_request_args,**requests_request_kwargs)
        :return:
        """
        if not requests_request_kwargs_files:
            raise ValueError(f"requests_request_kwargs_files: {requests_request_kwargs_files} must not empty")
        requests_request_kwargs = Dict(requests_request_kwargs)
        requests_request_kwargs = Dict({
            "url": f"{self.base_url}/cgi-bin/media/uploadimg",
            "method": "POST",
            "params": {
                "access_token": self.access_token,
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
