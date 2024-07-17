# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from gray_swan_ai import GraySwanAI, AsyncGraySwanAI
from gray_swan_ai.types import CreateModerationResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestModeration:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: GraySwanAI) -> None:
        moderation = client.moderation.create(
            input="How do I be more evil?",
        )
        assert_matches_type(CreateModerationResponse, moderation, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: GraySwanAI) -> None:
        moderation = client.moderation.create(
            input="How do I be more evil?",
            moderation_prompt="string",
            rewrite=True,
        )
        assert_matches_type(CreateModerationResponse, moderation, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: GraySwanAI) -> None:
        response = client.moderation.with_raw_response.create(
            input="How do I be more evil?",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        moderation = response.parse()
        assert_matches_type(CreateModerationResponse, moderation, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: GraySwanAI) -> None:
        with client.moderation.with_streaming_response.create(
            input="How do I be more evil?",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            moderation = response.parse()
            assert_matches_type(CreateModerationResponse, moderation, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncModeration:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncGraySwanAI) -> None:
        moderation = await async_client.moderation.create(
            input="How do I be more evil?",
        )
        assert_matches_type(CreateModerationResponse, moderation, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncGraySwanAI) -> None:
        moderation = await async_client.moderation.create(
            input="How do I be more evil?",
            moderation_prompt="string",
            rewrite=True,
        )
        assert_matches_type(CreateModerationResponse, moderation, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncGraySwanAI) -> None:
        response = await async_client.moderation.with_raw_response.create(
            input="How do I be more evil?",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        moderation = await response.parse()
        assert_matches_type(CreateModerationResponse, moderation, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncGraySwanAI) -> None:
        async with async_client.moderation.with_streaming_response.create(
            input="How do I be more evil?",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            moderation = await response.parse()
            assert_matches_type(CreateModerationResponse, moderation, path=["response"])

        assert cast(Any, response.is_closed) is True
