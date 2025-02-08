"""
title: Reasoning Tokens
author: yeyuan98
repo: https://github.com/yeyuan98/openwebui-reasoning-tokens
date: 2025-02-07
version: 0.1
license: MIT
description: Enables reasoning tokens and displays them visually in OWUI

Forked from @rmarfil3 (repo: https://github.com/rmarfil3/openwebui-openrouter-reasoning-tokens).

Refer to Github repo for instructions.

Current limitation: token count statistics does not display in OWUI
"""
from pydantic import BaseModel, Field
import logging
import requests
import json
import time


class Pipe:
    class Valves(BaseModel):
        API_BASE_URL: str = Field(default="https://api.siliconflow.cn/v1")
        #API_BASE_URL: str = Field(default="https://ark.cn-beijing.volces.com/api/v3")
        API_KEY: str = Field(
            default="",
            description="API key for authentication",
        )
        API_REASONING_TOKEN_REQUEST: str = Field(
            default="",
            description="Additional request field for reasoning tokens (use default if not needed)"
        )
        API_REASONING_TOKEN_FIELD: str = Field(
            default="reasoning_content",
            description="Field containing reasoning tokens in the response (vary by provider)"
        )
        API_MODELS: str = Field(
            default="deepseek-ai/DeepSeek-R1",
            description="Model names separated by comma without any space"
        )
        LOG_CONSOLE: bool = False

    def __init__(self):
        self.valves = self.Valves()
        self.logger = logging.getLogger(__name__)
    
    def log(self, log_line):
        if self.valves.LOG_CONSOLE:
            self.logger.warning(log_line) # Somehow WARN is the threshold, not INFO

    def pipes(self):
        models = self.valves.API_MODELS.split(",")
        self.log("Registered models: " + json.dumps(models))

        return [{
            "id": f"reasoning/{model}",
            "name": f"reasoning/{model}",
        } for model in models]

    def pipe(self, body: dict):
        headers = {
            "Authorization": f"Bearer {self.valves.API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://openwebui.com/",
            "X-Title": "Open WebUI",
        }

        # Modify the request to include reasoning tokens and fix model ID
        modified_body = {**body}
        if "model" in modified_body:
            # Remove "reasoning/" prefix from model ID
            modified_body["model"] = (
                modified_body["model"].split(".", 1)[-1].replace("reasoning/", "", 1)
            )

        if self.valves.API_REASONING_TOKEN_REQUEST != "":
            modified_body[self.valves.API_REASONING_TOKEN_REQUEST] = True
        
        self.log("Request POST:")
        self.log("    Header: " + json.dumps(headers))
        self.log("    Body: " + json.dumps(modified_body))

        try:
            response = requests.post(
                f"{self.valves.API_BASE_URL}/chat/completions",
                json=modified_body,
                headers=headers,
                stream=body.get("stream", False),
            )
            response.raise_for_status()

            if body.get("stream", False):
                return self._handle_streaming_response(response, modified_body)
            else:
                return self._handle_normal_response(response, modified_body)
        except Exception as e:
            return f"Error: {e}, Body: {modified_body}"

    def _handle_normal_response(self, response, body: dict):
        data = response.json()
        self.log("Response [Normal]: " + data)
        reasoning_field = self.valves.API_REASONING_TOKEN_FIELD
        if "choices" in data:
            for choice in data["choices"]:
                if "message" in choice and reasoning_field in choice["message"]:
                    reasoning = choice["message"][reasoning_field]
                    content = choice["message"]["content"]
                    choice["message"][
                        "content"
                    ] = f"<think>{reasoning}</think>\n{content}"
        return data

    def _handle_streaming_response(self, response, body: dict):
        thinking_state = -1  # -1: not started, 0: thinking, 1: answered
        reasoning_field = self.valves.API_REASONING_TOKEN_FIELD
        self.log("Response [Streaming, lines below]:")

        def construct_chunk(content, role='assistant'):
            return f"""data: {json.dumps({
                'id': data.get('id'),
                'object': 'chat.completion.chunk',
                'created': int(time.time()),
                'model': body.get("model"),
                'choices': [{
                    'index': 0,
                    'delta': {'content': content, 'role': role},
                    'finish_reason': None
                }],
                'info': data.get('usage', {})
            })}\n\n"""

        for line in response.iter_lines():
            if not line:
                continue
            decoded_line = line.decode("utf-8")
            self.log("    Line: " + decoded_line)
            try:
                if not decoded_line.startswith("data: "):
                    continue
                if "data: [DONE]" in decoded_line:
                    continue
                data = json.loads(decoded_line[6:])  # Skip "data: " prefix
                if not data.get("choices"):
                    continue
                choice = data["choices"][0]
                delta = choice.get("delta", {})

                # Handle transitioning states
                if thinking_state == -1 and delta.get(reasoning_field):
                    self.log("    Transition: -1 -> 0" + decoded_line)
                    thinking_state = 0
                    yield construct_chunk("<think>")
                elif thinking_state == 0 and not delta.get(reasoning_field):
                    self.log("    Transition: 0 -> 1" + decoded_line)
                    thinking_state = 1
                    yield construct_chunk("</think>\n\n")

                # Handle content output
                content = delta.get(reasoning_field, "") or delta.get("content", "")
                if content:
                    yield construct_chunk(content)
            except json.JSONDecodeError:
                continue
