import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class _FallbackLlm:
    def invoke(self, messages):
        raise RuntimeError("OPENAI_API_KEY is not configured")


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = _FallbackLlm()
