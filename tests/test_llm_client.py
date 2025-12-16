import unittest

from src.utils.llm_client import LLMClient


class FakeUsage:
    def __init__(self):
        self.prompt_tokens = 10
        self.completion_tokens = 5
        self.total_tokens = 15


class FakeMessage:
    def __init__(self, content):
        self.content = content


class FakeChoice:
    def __init__(self, content):
        self.message = FakeMessage(content)
        self.finish_reason = "stop"


class FakeResponse:
    def __init__(self, content):
        self.choices = [FakeChoice(content)]
        self.model = "test-model"
        self.id = "resp-123"
        self.usage = FakeUsage()


class FakeChat:
    def __init__(self, response):
        self.response = response

    def create(self, **kwargs):
        self.kwargs = kwargs
        return self.response


class FakeClient:
    def __init__(self, response):
        self.chat = type("Chat", (), {"completions": FakeChat(response), "send": FakeChat(response)})


class LLMClientTests(unittest.TestCase):
    def test_postprocess_returns_text_and_usage(self):
        response = FakeResponse("Hello!")
        client = FakeClient(response)
        llm = LLMClient(api_key="test", default_model="m", client=client)
        result = llm.postprocess("hi", "User said: ${output}", model=None, system_prompt="sys")
        self.assertEqual(result["text"], "Hello!")
        self.assertEqual(result["usage"]["total_tokens"], 15)
        # Prompt filled
        messages = client.chat.completions.kwargs["messages"]
        # First is system
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[0]["content"], "sys")
        # Second is user with filled transcript
        self.assertEqual(messages[1]["role"], "user")
        self.assertIn("hi", messages[1]["content"])

    def test_requires_model(self):
        response = FakeResponse("x")
        client = FakeClient(response)
        llm = LLMClient(api_key="test", default_model=None, client=client)
        with self.assertRaises(ValueError):
            llm.postprocess("hi", "t")


if __name__ == "__main__":
    unittest.main()
