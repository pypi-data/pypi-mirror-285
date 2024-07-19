"""Tests the embedding SDK.

Note: These tests hit the production API. A valid API key must be available in the `XAI_API_KEY`
environment variable.
"""

import os
import unittest

from xai_sdk import v2


class EmbeddingsTest(unittest.TestCase):
    def setUp(self):
        self.client = v2.Client()

    @unittest.skipIf("XAI_API_KEY" not in os.environ, "No API key specified")
    def test_single_text_embedding(self):
        response = self.client.embeddings.create(input="Hello World", model="v2")
        self.assertEqual(len(response.embeddings), 1)

    @unittest.skipIf("XAI_API_KEY" not in os.environ, "No API key specified")
    def test_multi_text_embedding(self):
        response = self.client.embeddings.create(input=["Hello World"] * 64, encoding_format="base64", model="v2")
        self.assertEqual(len(response.embeddings), 64)


class AsyncEmbeddingsTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = v2.Client(asynchronous=True)

    @unittest.skipIf("XAI_API_KEY" not in os.environ, "No API key specified")
    async def test_single_text_embedding(self):
        response = await self.client.embeddings.create(input="Hello World", model="v2")
        self.assertEqual(len(response.embeddings), 1)

    @unittest.skipIf("XAI_API_KEY" not in os.environ, "No API key specified")
    async def test_multi_text_embedding(self):
        response = await self.client.embeddings.create(input=["Hello World"] * 64, encoding_format="base64", model="v2")
        self.assertEqual(len(response.embeddings), 64)


if __name__ == "__main__":
    unittest.main()
