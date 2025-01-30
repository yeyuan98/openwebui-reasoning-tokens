# About

OpenWebUI has recently added support for [thinking tags](https://github.com/open-webui/open-webui/blob/b72150c881955721a63ae7f4ea1b9ea293816fc1/CHANGELOG.md?plain=1#L39). However, reasoning tokens from reasoning models in OpenRouter, such as DeepSeek R1 and its distilled variants, are still not visible in OpenWebUI. This is because OpenRouter API puts them in a [separate "reasoning" field](https://openrouter.ai/announcements/reasoning-tokens-for-thinking-models) rather than including them in the actual response message.

This pipe enables the reasoning tokens of specified models and integrates them into the response message, allowing OpenWebUI to display them visually.


# Demo

![Demo](https://github.com/rmarfil3/openwebui-openrouter-reasoning-tokens/blob/main/DEMO.gif)


# Additional Notes

After installing and enabling, new models will be added which will have the _Thinking..._ feature.
These models will be prefixed with `reasoning/`.

- reasoning/deepseek/deepseek-r1:free
- reasoning/deepseek/deepseek-r1-distill-llama-70b
- reasoning/deepseek/deepseek-r1

Feel free to modify this list in the code, under `pipes()` function.

You will probably have an issue with the generated titles.
You can go to Admin Panel -> Settings -> Interface, then change the **Task Model** to something else instead of "Current Model".
