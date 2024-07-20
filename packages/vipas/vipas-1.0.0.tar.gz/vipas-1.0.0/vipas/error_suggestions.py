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

ERROR_SUGGESTIONS = {
    400: {
        "suggested_actions": [
            "Check the request syntax and ensure it is correct.",
            "Verify that all required parameters are included in the request.",
            "Refer to the API documentation for the correct request format.",
            "If the problem persists, please contact support for assistance."
        ]
    },
    401: {
        "suggested_actions": [
            "Verify that you are using the correct VPS authentication token.",
            "Ensure the token has not expired and is still valid.",
            "If you are unsure about your token, please contact support for assistance."
        ]
    },
    403: {
        "suggested_actions": [
            "Check your permissions to ensure you have access to the requested resource.",
            "Verify that your account has the necessary roles to perform this action.",
            "If you believe this is an error, please contact support for assistance."
        ]
    },
    404: {
        "suggested_actions": [
            "Verify that the model ID is correct and valid.",
            "Ensure the model with the provided model ID is currently deployed.",
            "If the problem persists, please contact support for assistance."
        ]
    },
    429: {
        "suggested_actions": [
            "Reduce the frequency of your requests to comply with the rate limits.",
            "Consider implementing exponential backoff for retries.",
            "If you need higher rate limits, please contact support to discuss options."
        ]
    },
    504: {
        "suggested_actions": [
            "Check the server status to ensure it is running and not experiencing high load.",
            "Implement retry logic with exponential backoff to handle temporary server issues.",
            "Ensure your request payload is optimized and not causing excessive processing time.",
            "If the problem persists, please contact support for assistance."
        ]
    }
}