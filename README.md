# About

OpenWebUI has recently added support for [thinking tags](https://github.com/open-webui/open-webui/blob/b72150c881955721a63ae7f4ea1b9ea293816fc1/CHANGELOG.md?plain=1#L39). While the original DeepSeek API places reasoning tokens in the response message, third-party providers tend to place reasoning content in distinct fields that are not well-defined.

This pipe enables the reasoning tokens of specified models and moves those tokens into the response message, allowing OpenWebUI to detect and display them visually.

Forked from [repository](https://github.com/rmarfil3/openwebui-openrouter-reasoning-tokens) with modifications to support Siliconflow/Volcengine/etc.

此pipeline支持第三方API推理过程输出。

# Demo

![Demo](https://github.com/yeyuan98/openwebui-reasoning-tokens/blob/main/DEMO.gif)

# Supported providers

OpenRouter
: The OpenRouter API places reasoning in a ["reasoning" field](https://openrouter.ai/announcements/reasoning-tokens-for-thinking-models). You need to set `include_reasoning` for the `Api Reasoning Token Request` field in the pipeline configuration (see instruction below).

Siliconflow/硅基流动
: The Siliconflow API places reasoning in a ["reasoning_content" field](https://docs.siliconflow.cn/api-reference/chat-completions/chat-completions).

Volcengine/火山引擎
: The Volcengine API places reasoning in a ["reasoning_content" field](https://www.volcengine.com/docs/82379/1399009).Refer to this [guide](https://juejin.cn/post/7468328650338779176) to setup API endpoint.

# Instruction

After installing this pipe, configure it to provide API address, key, and model names. After enabling this pipe, new models will be added with the *Thinking...* feature. These models are prefixed with `reasoning/`.

Open WebUI uses LLM for chatting as well as other tasks including title generation. Models added by this pipeline are not compatible with title generation. To resolve this issue:

1. Navigate to the Admin Panel → Settings → Interface.
2. Change the **Task Model** option to something other than "Current Model".

# Limitations

Usage statistics could not be displayed in OWUI even if the API returns usage information. This might get fixed as time permits.