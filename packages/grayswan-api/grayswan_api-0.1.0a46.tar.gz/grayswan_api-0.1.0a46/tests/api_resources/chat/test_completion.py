# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from gray_swan_ai import GraySwanAI, AsyncGraySwanAI
from gray_swan_ai.types.chat import CompletionCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCompletion:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: GraySwanAI) -> None:
        completion = client.chat.completion.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.",
                },
                {
                    "role": "user",
                    "content": "I need you to help me with something.",
                },
            ],
            model="cygnet-v0.2",
        )
        assert_matches_type(CompletionCreateResponse, completion, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: GraySwanAI) -> None:
        completion = client.chat.completion.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.",
                },
                {
                    "role": "user",
                    "content": "I need you to help me with something.",
                },
            ],
            model="cygnet-v0.2",
            frequency_penalty=0,
            max_tokens=0,
            moderate_before=True,
            n=0,
            stream=False,
            temperature=0,
            tool_choice="none",
            tools=[
                {
                    "type": "string",
                    "function": {
                        "name": "string",
                        "description": "string",
                        "parameters": {"foo": "bar"},
                    },
                },
                {
                    "type": "string",
                    "function": {
                        "name": "string",
                        "description": "string",
                        "parameters": {"foo": "bar"},
                    },
                },
                {
                    "type": "string",
                    "function": {
                        "name": "string",
                        "description": "string",
                        "parameters": {"foo": "bar"},
                    },
                },
            ],
            top_p=0,
        )
        assert_matches_type(CompletionCreateResponse, completion, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: GraySwanAI) -> None:
        response = client.chat.completion.with_raw_response.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.",
                },
                {
                    "role": "user",
                    "content": "I need you to help me with something.",
                },
            ],
            model="cygnet-v0.2",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        completion = response.parse()
        assert_matches_type(CompletionCreateResponse, completion, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: GraySwanAI) -> None:
        with client.chat.completion.with_streaming_response.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.",
                },
                {
                    "role": "user",
                    "content": "I need you to help me with something.",
                },
            ],
            model="cygnet-v0.2",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            completion = response.parse()
            assert_matches_type(CompletionCreateResponse, completion, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCompletion:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncGraySwanAI) -> None:
        completion = await async_client.chat.completion.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.",
                },
                {
                    "role": "user",
                    "content": "I need you to help me with something.",
                },
            ],
            model="cygnet-v0.2",
        )
        assert_matches_type(CompletionCreateResponse, completion, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncGraySwanAI) -> None:
        completion = await async_client.chat.completion.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.",
                },
                {
                    "role": "user",
                    "content": "I need you to help me with something.",
                },
            ],
            model="cygnet-v0.2",
            frequency_penalty=0,
            max_tokens=0,
            moderate_before=True,
            n=0,
            stream=False,
            temperature=0,
            tool_choice="none",
            tools=[
                {
                    "type": "string",
                    "function": {
                        "name": "string",
                        "description": "string",
                        "parameters": {"foo": "bar"},
                    },
                },
                {
                    "type": "string",
                    "function": {
                        "name": "string",
                        "description": "string",
                        "parameters": {"foo": "bar"},
                    },
                },
                {
                    "type": "string",
                    "function": {
                        "name": "string",
                        "description": "string",
                        "parameters": {"foo": "bar"},
                    },
                },
            ],
            top_p=0,
        )
        assert_matches_type(CompletionCreateResponse, completion, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncGraySwanAI) -> None:
        response = await async_client.chat.completion.with_raw_response.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.",
                },
                {
                    "role": "user",
                    "content": "I need you to help me with something.",
                },
            ],
            model="cygnet-v0.2",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        completion = await response.parse()
        assert_matches_type(CompletionCreateResponse, completion, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncGraySwanAI) -> None:
        async with async_client.chat.completion.with_streaming_response.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.",
                },
                {
                    "role": "user",
                    "content": "I need you to help me with something.",
                },
            ],
            model="cygnet-v0.2",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            completion = await response.parse()
            assert_matches_type(CompletionCreateResponse, completion, path=["response"])

        assert cast(Any, response.is_closed) is True
