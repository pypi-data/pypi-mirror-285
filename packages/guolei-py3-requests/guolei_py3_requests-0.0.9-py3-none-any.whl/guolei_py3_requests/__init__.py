#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
=================================================
requests Class Library
-------------------------------------------------
作者：[郭磊]
手机：[15210720528]
Email：[174000902@qq.com]
Github：https://github.com/guolei19850528/guolei_py3_requests
=================================================
"""
from inspect import isfunction
from typing import Union, Iterable, Callable

import requests
from addict import Dict
from requests import Response, Session


class RequestsResponseCallable(object):
    def __init__(self):
        pass

    @staticmethod
    def response(response: Response = None):
        if isinstance(response, Response):
            return response
        return None

    @staticmethod
    def status_code(response: Response = None):
        if RequestsResponseCallable.response(response=response):
            return response.status_code
        return -1

    @staticmethod
    def status_code_compare(response: Response = None, status_code: int = 0):
        if RequestsResponseCallable.response(response=response):
            return response.status_code == status_code
        return False

    @staticmethod
    def status_code_200(response: Response = None):
        return RequestsResponseCallable.status_code_compare(response=response, status_code=200)

    @staticmethod
    def status_code_200_text(response: Response = None):
        if RequestsResponseCallable.status_code_200(response=response):
            return response.text
        return ""

    @staticmethod
    def status_code_200_content(response: Response = None):
        if RequestsResponseCallable.status_code_200(response=response):
            return response.content
        return b""

    @staticmethod
    def status_code_200_raw(response: Response = None):
        if RequestsResponseCallable.status_code_200(response=response):
            return response.raw
        return None

    @staticmethod
    def status_code_200_json(
            response: Response = None,
            response_json_args: Iterable = (),
            response_json_kwargs: dict = {}
    ):
        response_json_kwargs = Dict(response_json_kwargs)
        if RequestsResponseCallable.status_code_200(response=response):
            return response.json(*response_json_args, **response_json_kwargs)
        return {}

    @staticmethod
    def status_code_200_json_addict(
            response: Response = None,
            response_json_args: Iterable = (),
            response_json_kwargs: dict = {}
    ):
        if RequestsResponseCallable.status_code_200(response=response):
            return Dict(
                RequestsResponseCallable.status_code_200_json(
                    response=response,
                    response_json_args=response_json_args,
                    response_json_kwargs=response_json_kwargs
                )
            )
        return Dict({})


def requests_request(
        requests_response_callable: Callable = None,
        requests_request_args: Iterable = (),
        requests_request_kwargs: dict = {}
):
    """
    call requests.request
    :param requests_response_callable: if isfunction(requests_response_callable) return requests_response_callable(session,response) else return response
    :param requests_request_args: requests.request(*requests_request_args,**requests_request_kwargs)
    :param requests_request_kwargs: requests.request(*requests_request_args,**requests_request_kwargs)
    :return: if isfunction(requests_response_callable) return requests_response_callable(session,response) else return response
    """
    requests_request_kwargs = Dict(requests_request_kwargs)
    response = requests.request(*requests_request_args, **requests_request_kwargs.to_dict())
    if not isinstance(requests_response_callable, Callable):
        return response
    else:
        return requests_response_callable(response=response)


def request_session_request(
        session: Session = None,
        requests_response_callable: Callable = None,
        requests_request_args: Iterable = (),
        requests_request_kwargs: dict = {}
):
    """
    call requests.Session.request
    :param session: requests.Session
    :param requests_response_callable: if isfunction(requests_response_callable) return requests_response_callable(session,response) else return response
    :param requests_request_args: requests.request(*requests_request_args,**requests_request_kwargs)
    :param requests_request_kwargs: requests.request(*requests_request_args,**requests_request_kwargs)
    :return: if isfunction(requests_response_callable) return requests_response_callable(session,response) else return response
    """
    requests_request_kwargs = Dict(requests_request_kwargs)
    response = session.request(*requests_request_args, **requests_request_kwargs.to_dict())
    if not isfunction(requests_response_callable):
        return session, response
    else:
        return requests_response_callable(session, response)
