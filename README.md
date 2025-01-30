# About
OpenWebUI has recently added support for [thinking tags](https://github.com/open-webui/open-webui/blob/b72150c881955721a63ae7f4ea1b9ea293816fc1/CHANGELOG.md?plain=1#L39). However, reasoning tokens from reasoning models in OpenRouter, such as DeepSeek R1 and its distilled variants, are still not visible in OpenWebUI. This is because the OpenRouter API places them in a [separate "reasoning" field](https://openrouter.ai/announcements/reasoning-tokens-for-thinking-models) instead of including them in the actual response message.

This pipe enables the reasoning tokens of specified models and moves those tokens into the response message, allowing OpenWebUI to detect and display them visually.

# Demo
![Demo](https://github.com/rmarfil3/openwebui-openrouter-reasoning-tokens/blob/main/DEMO.gif)

# Additional Notes
After installing and enabling this pipe, new models will be added with the *Thinking...* feature. These models are prefixed with `reasoning/`:
- reasoning/deepseek/deepseek-r1:free
- reasoning/deepseek/deepseek-r1-distill-llama-70b
- reasoning/deepseek/deepseek-r1

You can modify this list in the code under the `pipes()` function.

You may encounter an issue with generated titles. To resolve this:
1. Navigate to the Admin Panel → Settings → Interface.
2. Change the **Task Model** option to something other than "Current Model".
