import base64
import json
import os
from typing import Any, Dict, Union
from httpx._client import USE_CLIENT_DEFAULT, Client, UseClientDefault
from httpx._models import Request, Response
from httpx._types import AuthTypes
from httpx._urls import URL
import httpx


class BaseCustomHttpClient:
    def _change_request(self, request: Request) -> Request:
        # auth
        auth = f"{os.environ['OPENAI_USER']}:{os.environ['OPENAI_PASSWORD']}"
        auth = f"Basic {base64.b64encode(auth.encode("utf-8")).decode("utf-8")}"
        openai_host = 'gateway.mpi.test.shopee.io'
        # headers
        request.headers.update({
            'Content-Type': 'application/json',
            'Host': openai_host,
            'Authorization': auth
        })
        # content
        content: str = request._content.decode("utf-8")
        data: Dict[str, Any] = json.loads(content)
        # model
        model: str = data.get('model', 'gpt-3.5-turbo')
        model_name = 'openai_v1_gpt_35_turbo' if model == 'gpt-3.5-turbo' else 'openai_gpt_4'
        domain = f'http://gateway.mpi.test.shopee.io/ufs/v1'
        url = f'{domain}/{model_name}/chat/completions'
        request.url = URL(url)
        return request


class CustomHttpClient(Client, BaseCustomHttpClient):
    def send(
            self,
            request: Request,
            *,
            stream: bool = False,
            auth: Union[AuthTypes, UseClientDefault, None] = USE_CLIENT_DEFAULT,
            follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
    ) -> Response:
        request = self._change_request(request)
        return super().send(request, stream=stream, auth=auth, follow_redirects=follow_redirects)


class OpenAIChat:
    def __init__(self, model: str = 'gpt3', env: str = 'test'):
        self.auth = httpx.BasicAuth(os.environ['OPENAI_USER'], os.environ['OPENAI_PASSWORD'])
        model_name = 'openai_v1_gpt_35_turbo' if model == 'gpt3' else 'openai_gpt_4'
        self.domain = f'http://gateway.mpi.{env}.shopee.io/ufs/v1'
        self.url = f'{self.domain}/{model_name}/chat/completions'

    def get_model_list(self):
        url = f'{self.domain}/openai_v1_models'
        resp = httpx.get(url, auth=self.auth)
        return resp.json()

    def chat(self, message_json: dict):
        resp = httpx.post(self.url, auth=self.auth, json=message_json)
        return resp.json()

    @staticmethod
    def custom_request():
        base_url = "https://api.openai.com/v1"
        _custom_http_client = CustomHttpClient(base_url=base_url, timeout=None, proxies=None, transport=None)
        return _custom_http_client
