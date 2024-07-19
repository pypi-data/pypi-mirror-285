import os

from maitai._azure import MaitaiAsyncAzureOpenAIClient as AsyncAzureOpenAI, MaitaiAzureOpenAIClient as AzureOpenAI
from maitai._context import ContextManager
from maitai._evaluator import Evaluator as Evaluator
from maitai._inference import Inference as Inference
from maitai._maitai import Chat, Maitai
from maitai._maitai_async import MaitaiAsync

chat = Chat()
context = ContextManager()
AsyncOpenAI = MaitaiAsync
OpenAI = Maitai


def initialize(api_key):
    from maitai._config import config
    config.initialize(api_key)


if os.environ.get("MAITAI_API_KEY") and os.environ.get("MAITAI_ENV") != "development":
    initialize(os.environ.get("MAITAI_API_KEY"))
