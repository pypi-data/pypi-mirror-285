import json

import requests
from betterproto import Casing

from maitai._config import config
from maitai._utils import __version__ as version, required_args
from maitai_gen.application import ApplicationContext


class ContextManager:
    @required_args(["application_ref_name", "reference", "context_body"],
                   ["application_ref_name", "reference", "file_path"])
    def update(self, *, application_ref_name: str, reference: str, context_body: str = '', file_path: str = ''):
        if not reference:
            raise ValueError("Reference is required")
        if context_body and file_path:
            raise ValueError("Only one of context_body and file can be specified")

        context = ApplicationContext()
        context.reference = reference
        if file_path:
            s3_path = self.upload_context_file(file_path).get('s3_path')
            if not s3_path:
                raise Exception('Failed to upload context')
            context.context_type = 'FILE'
            context.context_path = s3_path
        else:
            context.context_body = context_body
            context.context_type = 'TEXT'

        host = config.maitai_host
        url = f'{host}/context/application'
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': config.api_key,
            'x-client-version': version,
        }
        response = requests.put(url, headers=headers, data=json.dumps({
            'application_ref_name': application_ref_name,
            'context': context.to_pydict(casing=Casing.SNAKE),
        }))

        if response.status_code != 200:
            raise RuntimeError(f"Error updating context: {response.text}")

    def upload_context_file(self, file_path: str):
        host = config.maitai_host
        url = f'{host}/context/application/file'
        headers = {
            'x-api-key': config.api_key,
            'x-client-version': version,
        }
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(url, headers=headers, files=files)
        if response.status_code != 200:
            raise RuntimeError(f"Error uploading context: {response.text}")
        return response.json()
