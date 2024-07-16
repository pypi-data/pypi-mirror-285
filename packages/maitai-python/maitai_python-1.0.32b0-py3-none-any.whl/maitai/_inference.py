import traceback
from typing import AsyncIterable, Iterable, Optional

import aiohttp
import requests
from betterproto import Casing

from maitai._config import config
from maitai._maitai_client import MaitaiClient
from maitai._utils import chat_completion_chunk_to_response
from maitai_common.utils.types import AsyncChunkQueue, ChunkQueue, EvaluateCallback, QueueIterable
from maitai_common.version import version
from maitai_gen.chat import ChatCompletionChunk, ChatCompletionParams, ChatCompletionRequest, ChatCompletionResponse, ChatStorageRequest
from maitai_gen.inference import InferenceStreamResponse


class InferenceException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class InferenceWarning(Warning):
    def __init__(self, *args, **kwargs):
        pass


class Inference(MaitaiClient):

    def __init__(self):
        super().__init__()

    @classmethod
    def infer(cls, session_id, reference_id, intent, application_ref_name, completion_params: ChatCompletionParams, apply_corrections: bool, evaluation_enabled: bool, evaluate_callback: EvaluateCallback = None,
              timeout=None, context_retrieval_enabled=False, context_query='', return_request=False, fallback_model=None) -> Iterable[InferenceStreamResponse]:
        chat_request: ChatCompletionRequest = cls.create_inference_request(application_ref_name, session_id, reference_id, intent, apply_corrections, evaluation_enabled, completion_params, evaluate_callback, context_retrieval_enabled, context_query, return_request, fallback_model)
        if evaluate_callback:
            q = ChunkQueue()
            cls.run_async(cls.send_inference_request_async(chat_request, chunk_queue=q, evaluation_callback=evaluate_callback))
            return QueueIterable(q, timeout=timeout)
        else:
            return cls.send_inference_request(chat_request)

    @classmethod
    async def infer_async(cls, session_id, reference_id, intent, application_ref_name, completion_params: ChatCompletionParams, apply_corrections: bool, evaluation_enabled: bool,
                          evaluate_callback: EvaluateCallback = None, timeout=None, context_retrieval_enabled=False, context_query='', fallback_model=None) -> AsyncIterable[InferenceStreamResponse]:
        chat_request: ChatCompletionRequest = cls.create_inference_request(application_ref_name, session_id, reference_id, intent, apply_corrections, evaluation_enabled, completion_params, evaluate_callback, context_retrieval_enabled, context_query, fallback_model)
        q = AsyncChunkQueue()
        cls.run_async(cls.send_inference_request_async(chat_request, async_chunk_queue=q, evaluation_callback=evaluate_callback))
        return QueueIterable(q, timeout=timeout)

    @classmethod
    def create_chat_storage_request(cls, session_id, reference_id, intent, application_ref_name, completion_params: ChatCompletionParams, chat_completion_response: Optional[ChatCompletionResponse],
                                    final_chunk: Optional[ChatCompletionChunk], content: str):
        inference_request = cls.create_inference_request(application_ref_name, session_id, reference_id, intent, False, False, completion_params, None, False, '')
        if final_chunk:
            chat_completion_response = chat_completion_chunk_to_response(final_chunk, content)

        return ChatStorageRequest(chat_completion_request=inference_request, chat_completion_response=chat_completion_response)

    @classmethod
    def store_chat_response(cls, session_id, reference_id, intent, application_ref_name, completion_params: ChatCompletionParams, chat_completion_response: Optional[ChatCompletionResponse],
                            final_chunk: Optional[ChatCompletionChunk], content: str):
        chat_storage_request = cls.create_chat_storage_request(session_id, reference_id, intent, application_ref_name, completion_params, chat_completion_response, final_chunk, content)
        cls.run_async(cls.send_storage_request_async(chat_storage_request))

    @classmethod
    def send_inference_request(cls, chat_request: ChatCompletionRequest) -> Iterable[InferenceStreamResponse]:
        def consume_stream():
            host = config.maitai_host
            url = f'{host}/chat/completions/serialized'
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': config.api_key,
                'x-client-version': version,
            }
            response = requests.post(url, headers=headers, data=chat_request.to_json(casing=Casing.SNAKE), stream=True)
            if response.status_code != 200:
                print(f"Failed to send inference request. Status code: {response.status_code}. Error: {response.text}")
                return
            try:
                for line in response.iter_lines():
                    if line:
                        yield line
            finally:
                response.close()

        for resp in consume_stream():
            inference_response: InferenceStreamResponse = InferenceStreamResponse().from_json(resp)
            yield inference_response

    @classmethod
    async def send_inference_request_async(cls, chat_request: ChatCompletionRequest, chunk_queue: ChunkQueue = None, async_chunk_queue: AsyncChunkQueue = None, evaluation_callback: EvaluateCallback = None):
        host = config.maitai_host
        url = f'{host}/chat/completions/serialized'
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': config.api_key,
            'x-client-version': version,
        }
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.post(url, headers=headers, data=chat_request.to_json(casing=Casing.SNAKE)) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"Failed to send inference request. Status code: {response.status}. Error: {error_text}")
                    if chunk_queue:
                        chunk_queue.put(StopIteration())
                    if async_chunk_queue:
                        await async_chunk_queue.put(StopIteration())
                    return
                async for line in response.content:
                    if line:
                        inference_response: InferenceStreamResponse = InferenceStreamResponse().from_json(line)
                        if chunk_queue:
                            chunk_queue.put(inference_response)
                        if async_chunk_queue:
                            await async_chunk_queue.put(inference_response)
                        if inference_response.evaluate_response and evaluation_callback:
                            try:
                                evaluation_callback(inference_response.evaluate_response)
                            except:
                                traceback.print_exc()
                if chunk_queue:
                    chunk_queue.put(StopIteration())
                if async_chunk_queue:
                    await async_chunk_queue.put(StopIteration())

    @classmethod
    async def send_storage_request_async(cls, chat_storage_request: ChatStorageRequest):
        host = config.maitai_host
        url = f'{host}/chat/completions/response'
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': config.api_key,
            'x-client-version': version,
        }
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                return await session.put(url, headers=headers, data=chat_storage_request.to_json(casing=Casing.SNAKE))
        except:
            traceback.print_exc()
