"""
title: OpenRouter Reasoning Tokens
author: rmarfil3
repo: https://github.com/rmarfil3/openwebui-openrouter-reasoning-tokens
date: 2025-01-30
version: 0.1
license: MIT
description: Enables reasoning tokens and displays them visually in OWUI


After installing and enabling, 3 models will be added which will have the "Thinking..." feature.
These models will be prefixed with "reasoning/".

You will probably have an issue with the generated titles.
You can go to Admin Panel -> Settings -> Interface, then change the Task Model to something else instead of "Current Model".
"""

from pydantic import BaseModel, Field
import requests
import json
import time


class Pipe:
    class Valves(BaseModel):
        OPENROUTER_API_BASE_URL: str = Field(default="https://openrouter.ai/api/v1")
        OPENROUTER_API_KEY: str = Field(
            default="",
            description="Your OpenRouter API key for authentication",
        )

    def __init__(self):
        self.valves = self.Valves()

    def pipes(self):
        models = [
            'deepseek/deepseek-r1:free',
            'deepseek/deepseek-r1-distill-llama-70b',
            'deepseek/deepseek-r1',
        ]

        return [{
            "id": f"reasoning/{model}",
            "name": f"reasoning/{model}",
        } for model in models]

    def pipe(self, body: dict):
        headers = {
            "Authorization": f"Bearer {self.valves.OPENROUTER_API_KEY}",
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

        modified_body["include_reasoning"] = True

        try:
            response = requests.post(
                f"{self.valves.OPENROUTER_API_BASE_URL}/chat/completions",
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
            return f"Error: {e}, {modified_body}"

    def _handle_normal_response(self, response, body: dict):
        data = response.json()
        if "choices" in data:
            for choice in data["choices"]:
                if "message" in choice and "reasoning" in choice["message"]:
                    reasoning = choice["message"]["reasoning"]
                    choice["message"][
                        "content"
                    ] = f"<think>{reasoning}</think>\n{choice['message']['content']}"
        return data

    def _handle_streaming_response(self, response, body: dict):
        thinking_state = -1  # -1: not started, 0: thinking, 1: answered

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
                }]
            })}\n\n"""

        for line in response.iter_lines():
            if not line:
                continue
            decoded_line = line.decode("utf-8")
            try:
                if not decoded_line.startswith("data: "):
                    continue
                data = json.loads(decoded_line[6:])  # Skip "data: " prefix
                if not data.get("choices"):
                    continue
                choice = data["choices"][0]
                delta = choice.get("delta", {})

                # Handle transitioning states
                if thinking_state == -1 and delta.get("reasoning"):
                    thinking_state = 0
                    yield construct_chunk("<think>")
                elif thinking_state == 0 and not delta.get("reasoning"):
                    thinking_state = 1
                    yield construct_chunk("</think>\n\n")

                # Handle content output
                content = delta.get("reasoning", "") or delta.get("content", "")
                if content:
                    yield construct_chunk(content)
            except json.JSONDecodeError:
                continue
