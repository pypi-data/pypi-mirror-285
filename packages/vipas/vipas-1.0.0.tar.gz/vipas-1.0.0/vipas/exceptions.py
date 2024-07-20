# coding: utf-8

"""
  Copyright (c) 2024 Vipas.AI
 
  All rights reserved. This program and the accompanying materials
  are made available under the terms of a proprietary license which prohibits
  redistribution and use in any form, without the express prior written consent
  of Vipas.AI.
  
  This code is proprietary to Vipas.AI and is protected by copyright and
  other intellectual property laws. You may not modify, reproduce, perform,
  display, create derivative works from, repurpose, or distribute this code or any portion of it
  without the express prior written permission of Vipas.AI.
  
  For more information, contact Vipas.AI at legal@vipas.ai
  
"""  # noqa: E501

# client_exceptions.py

from typing import Any, Optional, List
from typing_extensions import Self
from vipas.error_suggestions import ERROR_SUGGESTIONS

class VipasException(Exception):
    """The base exception class for all VipasExceptions"""

class ClientException(VipasException):

    def __init__(
        self, 
        status=None, 
        http_resp=None,
        *,
        body: Optional[str] = None,
        data: Optional[Any] = None,
        suggested_actions: Optional[List[str]] = None,
    ) -> None:
        self.status = status
        self.body = body
        self.data = data
        self.suggested_actions = suggested_actions

        if http_resp:
            if self.status is None:
                self.status = http_resp.status
            if self.body is None:
                try:
                    self.body = http_resp.data.decode('utf-8')
                except Exception:
                    pass

    @classmethod
    def from_response(
        cls, 
        *, 
        http_resp, 
        body: Optional[str],
        data: Optional[Any],
    ) -> Self:
        suggested_actions = None

        # Fetch suggestions from the dictionary
        suggestions = ERROR_SUGGESTIONS.get(http_resp.status_code, {})
        suggested_actions = suggestions.get("suggested_actions")

        exception_args = {
            "status": http_resp.status_code,
            "http_resp": http_resp,
            "body": body,
            "data": data,
            "suggested_actions": suggested_actions,
        }

        if http_resp.status_code == 400:
            raise BadRequestException(**exception_args)

        if http_resp.status_code == 401:
            raise UnauthorizedException(**exception_args)

        if http_resp.status_code == 403:
            raise ForbiddenException(**exception_args)

        if http_resp.status_code == 404:
            raise NotFoundException(**exception_args)
        
        if http_resp.status_code == 429:
            raise RateLimitExceededException(**exception_args)
        
        if http_resp.status_code == 504:
            raise GatewayTimeoutException(**exception_args)

        if 500 <= http_resp.status_code <= 599:
            raise ConnectionException(**exception_args)

        raise ClientException(**exception_args)

    def __str__(self):
        """Custom error messages for exception"""
        error_message = f"({self.status})\n"

        if self.data or self.body:
            error_message += f"HTTP response body: {self.data or self.body}\n"
        
        if self.suggested_actions:
            error_message += "Suggested Actions:\n"
            for action in self.suggested_actions:
                error_message += f"- {action}\n"

        return error_message

class BadRequestException(ClientException):
    pass

class NotFoundException(ClientException):
    pass

class UnauthorizedException(ClientException):
    pass

class ForbiddenException(ClientException):
    pass

class ConnectionException(ClientException):
    pass

class RateLimitExceededException(ClientException):
    pass

class GatewayTimeoutException(ClientException):
    pass