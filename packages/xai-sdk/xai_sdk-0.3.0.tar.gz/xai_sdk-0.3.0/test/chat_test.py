"""Tests the chat SDK.

Note: These tests hit the production API. A valid API key must be available in the `XAI_API_KEY`
environment variable.
"""

import os
import unittest

import parameterized

from xai_sdk import v2


class ChatTest(unittest.TestCase):
    def setUp(self):
        self.client = v2.Client()

    @parameterized.parameterized.expand(
        [
            (None,),
            (1,),
            (2,),
            (4,),
            (8,),
            (16,),
            (32,),
            (64,),
        ]
    )
    @unittest.skipIf("XAI_API_KEY" not in os.environ, "No API key specified")
    def test_create_completion(self, n):
        response = self.client.chat.completions.create(
            messages=[
                {"role": "user", "content": "Hey, how are you?"},
                {"role": "assistant", "content": "good, u?"},
                {"role": "user", "content": "same"},
            ],
            model="grok-1.5",
            n=n,
        )

        self.assertEqual(n or 1, len(response.choices))

    @parameterized.parameterized.expand(
        [
            (None,),
            (1,),
            (2,),
            (4,),
        ]
    )
    @unittest.skipIf("XAI_API_KEY" not in os.environ, "No API key specified")
    def test_create_completion_multi_content(self, n):
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Hey, how are you?"},
                        {"type": "text", "text": " Hm?"},
                    ],
                },
                {"role": "assistant", "content": "good, u?"},
                {"role": "user", "content": "same"},
            ],
            model="grok-1.5",
            n=n,
        )

        self.assertEqual(n or 1, len(response.choices))

    @parameterized.parameterized.expand(
        [
            (None,),
            (1,),
            (2,),
            (4,),
            (8,),
            (16,),
            (32,),
            (64,),
        ]
    )
    @unittest.skipIf("XAI_API_KEY" not in os.environ, "No API key specified")
    def test_create_completion_stream(self, n):
        stream = self.client.chat.completions.create(
            messages=[
                {"role": "user", "content": "Hey, how are you?"},
            ],
            model="grok-1.5",
            n=n,
            stream=True,
        )

        for response in stream:
            self.assertLessEqual(len(response.choices), n or 1)


class AsyncChatTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = v2.Client(asynchronous=True)

    @parameterized.parameterized.expand(
        [
            (None,),
            (1,),
            (2,),
            (4,),
            (8,),
            (16,),
            (32,),
            (64,),
        ]
    )
    @unittest.skipIf("XAI_API_KEY" not in os.environ, "No API key specified")
    async def test_create_completion(self, n):
        response = await self.client.chat.completions.create(
            messages=[
                {"role": "user", "content": "Hey, how are you?"},
                {"role": "assistant", "content": "good, u?"},
                {"role": "user", "content": "same"},
            ],
            model="grok-1.5",
            n=n,
        )

        self.assertEqual(n or 1, len(response.choices))

    @parameterized.parameterized.expand(
        [
            (None,),
            (1,),
            (2,),
            (4,),
        ]
    )
    @unittest.skipIf("XAI_API_KEY" not in os.environ, "No API key specified")
    async def test_create_completion_multi_content(self, n):
        response = await self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Hey, how are you?"},
                        {"type": "text", "text": " Hm?"},
                    ],
                },
                {"role": "assistant", "content": "good, u?"},
                {"role": "user", "content": "same"},
            ],
            model="grok-1.5",
            n=n,
        )

        self.assertEqual(n or 1, len(response.choices))

    @parameterized.parameterized.expand(
        [
            (None,),
            (1,),
            (2,),
            (4,),
            (8,),
            (16,),
            (32,),
            (64,),
        ]
    )
    @unittest.skipIf("XAI_API_KEY" not in os.environ, "No API key specified")
    async def test_create_completion_stream(self, n):
        stream = self.client.chat.completions.create(
            messages=[
                {"role": "user", "content": "Hey, how are you?"},
            ],
            model="grok-1.5",
            n=n,
            stream=True,
        )

        async for response in stream:
            self.assertLessEqual(len(response.choices), n or 1)


if __name__ == "__main__":
    unittest.main()
