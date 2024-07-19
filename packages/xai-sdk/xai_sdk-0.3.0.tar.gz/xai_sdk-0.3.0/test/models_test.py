"""Tests the models SDK.

Note: These tests hit the production API. A valid API key must be available in the `XAI_API_KEY`
environment variable.
"""

import os
import unittest

from xai_sdk import v2


class ModelsTest(unittest.TestCase):
    def setUp(self):
        self.client = v2.Client()

    @unittest.skipIf("XAI_API_KEY" not in os.environ, "No API key specified")
    def test_list_language_models(self):
        response = self.client.models.list_language_models()
        self.assertGreater(len(response.models), 1)

    @unittest.skipIf("XAI_API_KEY" not in os.environ, "No API key specified")
    def test_multi_text_embedding(self):
        response = self.client.models.list_embedding_models()
        self.assertGreater(len(response.models), 1)


class AsyncModelsTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = v2.Client(asynchronous=True)

    @unittest.skipIf("XAI_API_KEY" not in os.environ, "No API key specified")
    async def test_list_language_models(self):
        response = await self.client.models.list_language_models()
        self.assertGreater(len(response.models), 1)

    @unittest.skipIf("XAI_API_KEY" not in os.environ, "No API key specified")
    async def test_multi_text_embedding(self):
        response = await self.client.models.list_embedding_models()
        self.assertGreater(len(response.models), 1)


if __name__ == "__main__":
    unittest.main()
