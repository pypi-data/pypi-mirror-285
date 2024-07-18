#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
=================================================
qunjielong Class Library
-------------------------------------------------
作者：[郭磊]
手机：[15210720528]
Email：[174000902@qq.com]
Github：https://github.com/guolei19850528/guolei_py3_qunjielong
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
    def status_code_200_json_addict_code_200_success(response: Response = None):
        json_addict = RequestsResponseCallable.status_code_200_json_addict(response=response)
        return json_addict.code == 200 and isinstance(json_addict.success, bool) and json_addict.success

    @staticmethod
    def status_code_200_json_addict_code_200_success_data(response: Response = None):
        if RequestsResponseCallable.status_code_200_json_addict_code_200_success(response=response):
            return RequestsResponseCallable.status_code_200_json_addict(response=response).data
        return Dict({})

    @staticmethod
    def status_code_200_json_addict_code_200_success_data_str(response: Response = None):
        if RequestsResponseCallable.status_code_200_json_addict_code_200_success(response=response):
            return RequestsResponseCallable.status_code_200_json_addict(response=response).data
        return ""


class Api(object):
    """
    群接龙 第三方开放Api

    @see https://console-docs.apipost.cn/preview/b4e4577f34cac87a/1b45a97352d07e60/
    """

    def __init__(
            self,
            base_url: str = "",
            secret: str = "",
            home_id: str = "",
            diskcache: Cache = None,
            strict_redis: redis.StrictRedis = None
    ):
        """
        群接龙 第三方开放Api
        :param base_url: base url
        :param secret: secret
        :param home_id: 主页id
        :param diskcache: diskcache.core.Cache
        :param strict_redis: redis.StrictRedis
        """
        self._base_url = base_url
        self._secret = secret
        self._home_id = home_id
        self._diskcache = diskcache
        self._strict_redis = strict_redis
        self._access_token = ""

    @property
    def base_url(self):
        """
        基本url
        :return:
        """
        return self._base_url[:-1] if self._base_url.endswith("/") else self._base_url

    @base_url.setter
    def base_url(self, value: str = "") -> str:
        """
        基本url
        :param value:
        :return:
        """
        self._base_url = value

    @property
    def secret(self) -> str:
        return self._secret

    @secret.setter
    def secret(self, value: str = ""):
        self._secret = value

    @property
    def home_id(self) -> str:
        return self._home_id

    @home_id.setter
    def home_id(self, value: str = ""):
        self._home_id = value

    @property
    def access_token(self) -> str:
        return self._access_token

    @property
    def diskcache(self) -> Cache:
        """
        diskcache.core.Cache
        :return:
        """
        return self._diskcache

    @diskcache.setter
    def diskcache(self, value: Cache = None):
        """
        diskcache.core.Cache
        :param value:
        :return:
        """
        return self._diskcache

    @property
    def strict_redis(self) -> redis.StrictRedis:
        """
        redis.StrictRedis
        :return:
        """
        return self._strict_redis

    @strict_redis.setter
    def strict_redis(self, value: redis.StrictRedis = None):
        """
        redis.StrictRedis
        :param value:
        :return:
        """
        self._strict_redis = value

    def get_access_token(
            self,
            requests_request_kwargs_params: dict = {},
            requests_response_callable: Callable = RequestsResponseCallable.status_code_200_json_addict_code_200_success_data_str,
            requests_request_args: Iterable = (),
            requests_request_kwargs: dict = {}
    ) -> str:
        """
        获取访问凭证

        see https://console-docs.apipost.cn/preview/b4e4577f34cac87a/1b45a97352d07e60/?target_id=71e7934a-afce-4fd3-a897-e2248502cc94s
        :return: 访问凭证
        """
        requests_request_kwargs = Dict(requests_request_kwargs)
        requests_request_kwargs = Dict({
            "url": f"{self.base_url}/open/auth/token",
            "method": "GET",
            "params": {
                "secret": self.secret,
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
            f"jtwy_py3_library",
            f"qunjielong",
            f"Qunjielong",
            f"redis",
            f"access_token",
            f"{hashlib.md5(self.base_url.encode('utf-8')).hexdigest()}",
            f"{self.secret}",
        ])
        if strict_redis is None or not isinstance(strict_redis, redis.StrictRedis):
            strict_redis = self.strict_redis
        if isinstance(strict_redis, redis.StrictRedis):
            self._access_token = strict_redis.get(cache_key)
        if not isinstance(self._access_token, str) or not len(self._access_token):
            self._access_token = self.get_access_token()
            if isinstance(strict_redis, redis.StrictRedis):
                strict_redis.setex(name=cache_key, value=self.access_token, time=timedelta(seconds=110))
        return self

    def access_token_with_diskcache(self, cache: Cache = None):
        """
        使用diskcache,获取访问凭证
        :param cache: diskcache.core.Cache class instance if None or type not diskcache.core.Cache use self.diskcache
        :return: self
        """
        # 缓存key
        cache_key = "_".join([
            f"jtwy_py3_library",
            f"qunjielong",
            f"Qunjielong",
            f"diskcache",
            f"access_token",
            f"{hashlib.md5(self.base_url.encode('utf-8')).hexdigest()}",
            f"{self.secret}",
        ])
        if cache is None or not isinstance(cache, Cache):
            cache = self.diskcache
        if isinstance(cache, Cache):
            self._access_token = cache.get(key=cache_key, default="")
        if not isinstance(self._access_token, str) or not len(self._access_token):
            self._access_token = self.get_access_token()
            if isinstance(cache, Cache):
                cache.set(key=cache_key, value=self.access_token, expire=timedelta(seconds=110).total_seconds())
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

    def query_all_orders(
            self,
            requests_request_kwargs_json: dict = {},
            requests_response_callable: Callable = RequestsResponseCallable.status_code_200_json_addict_code_200_success_data,
            requests_request_args: Iterable = (),
            requests_request_kwargs: dict = {},
    ) :
        requests_request_kwargs_json = Dict(requests_request_kwargs_json)
        requests_request_kwargs = Dict(requests_request_kwargs)
        requests_request_kwargs = Dict({
            "url": f"{self.base_url}/open/api/order/all/query_order_list",
            "method": "POST",
            "params": {
                "accessToken": self.access_token,
                **requests_request_kwargs.params,
            },
            "json": {
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

    def query_forward_orders(
            self,
            requests_request_kwargs_json: dict = {},
            requests_response_callable: Callable = RequestsResponseCallable.status_code_200_json_addict_code_200_success_data,
            requests_request_args: Iterable = (),
            requests_request_kwargs: dict = {},
    ) :
        requests_request_kwargs_json = Dict(requests_request_kwargs_json)
        requests_request_kwargs = Dict(requests_request_kwargs)
        requests_request_kwargs = Dict({
            "url": f"{self.base_url}/open/api/order/forward/query_order_list",
            "method": "POST",
            "params": {
                "accessToken": self.access_token,
                **requests_request_kwargs.params,
            },
            "json": {
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

    def query_single_order(
            self,
            order_no: str = None,
            requests_response_callable: Callable = RequestsResponseCallable.status_code_200_json_addict_code_200_success_data,
            requests_request_args: Iterable = (),
            requests_request_kwargs: dict = {},
    ) :
        requests_request_kwargs = Dict(requests_request_kwargs)
        requests_request_kwargs = Dict({
            "url": f"{self.base_url}/open/api/order/single/query_order_info",
            "method": "POST",
            "params": {
                "accessToken": self.access_token,
                **requests_request_kwargs.params,
            },
            "json": {
                "orderNo": order_no,
                **requests_request_kwargs.json,
            },
            **requests_request_kwargs,
        })
        return requests_request(
            requests_response_callable=requests_response_callable,
            requests_request_args=requests_request_args,
            requests_request_kwargs=requests_request_kwargs
        )

    def query_multi_order(
            self,
            order_no_list: list[str] = [],
            requests_response_callable: Callable = RequestsResponseCallable.status_code_200_json_addict_code_200_success_data,
            requests_request_args: Iterable = (),
            requests_request_kwargs: dict = {},
    ) :
        requests_request_kwargs = Dict(requests_request_kwargs)
        requests_request_kwargs = Dict({
            "url": f"{self.base_url}/open/api/order/multi/query_order_info",
            "method": "POST",
            "params": {
                "accessToken": self.access_token,
                **requests_request_kwargs.params,
            },
            "json": {
                "orderNoList": order_no_list,
                **requests_request_kwargs.json,
            },
            **requests_request_kwargs,
        })
        return requests_request(
            requests_response_callable=requests_response_callable,
            requests_request_args=requests_request_args,
            requests_request_kwargs=requests_request_kwargs
        )

    def query_act_goods(
            self,
            act_no: Union[int, str] = "",
            requests_response_callable: Callable = RequestsResponseCallable.status_code_200_json_addict_code_200_success_data,
            requests_request_args: Iterable = (),
            requests_request_kwargs: dict = {},
    ) :
        requests_request_kwargs = Dict(requests_request_kwargs)
        requests_request_kwargs = Dict({
            "url": f"{self.base_url}/open/api/act_goods/query_act_goods",
            "method": "POST",
            "params": {
                "accessToken": self.access_token,
                **requests_request_kwargs.params,
            },
            "json": {
                "actNo": act_no,
                **requests_request_kwargs.json,
            },
            **requests_request_kwargs,
        })
        return requests_request(
            requests_response_callable=requests_response_callable,
            requests_request_args=requests_request_args,
            requests_request_kwargs=requests_request_kwargs
        )

    def query_goods(
            self,
            id: Union[int, str] = "",
            requests_response_callable: Callable = RequestsResponseCallable.status_code_200_json_addict_code_200_success_data,
            requests_request_args: Iterable = (),
            requests_request_kwargs: dict = {},
    ) :
        requests_request_kwargs = Dict(requests_request_kwargs)
        requests_request_kwargs = Dict({
            "url": f"{self.base_url}/open/api/goods/get_goods_detail/{id}",
            "method": "GET",
            "params": {
                "accessToken": self.access_token,
                **requests_request_kwargs.params,
            },
            **requests_request_kwargs,
        })
        return requests_request(
            requests_response_callable=requests_response_callable,
            requests_request_args=requests_request_args,
            requests_request_kwargs=requests_request_kwargs
        )

    def query_list_act_info(
            self,
            act_no_list: list = [],
            requests_response_callable: Callable = RequestsResponseCallable.status_code_200_json_addict_code_200_success_data,
            requests_request_args: Iterable = (),
            requests_request_kwargs: dict = {},
    ) :
        requests_request_kwargs = Dict(requests_request_kwargs)
        requests_request_kwargs = Dict({
            "url": f"{self.base_url}/open/api/act/list_act_info",
            "method": "POST",
            "params": {
                "accessToken": self.access_token,
                **requests_request_kwargs.params,
            },
            "json": {
                "actNoList": act_no_list,
                **requests_request_kwargs.json,
            },
            **requests_request_kwargs,
        })
        return requests_request(
            requests_response_callable=requests_response_callable,
            requests_request_args=requests_request_args,
            requests_request_kwargs=requests_request_kwargs
        )
