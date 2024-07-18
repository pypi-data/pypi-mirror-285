# Deeptune Python Library

[![fern shield](https://img.shields.io/badge/%F0%9F%8C%BF-SDK%20generated%20by%20Fern-brightgreen)](https://github.com/fern-api/fern)
[![pypi](https://img.shields.io/pypi/v/deeptune)](https://pypi.python.org/pypi/deeptune)

The Deeptune Python library provides convenient access to the Deeptune API from Python.

## Installation

```sh
pip install deeptune
```

## Usage

Instantiate and use the client with the following:

```python
from deeptune.client import DeeptuneApi

client = DeeptuneApi(
    xi_api_key="YOUR_XI_API_KEY",
    token="YOUR_TOKEN",
)
client.text_to_speech.generate(
    prompt_audio_uri="prompt_audio_uri",
    target_language="target_language",
    target_text="target_text",
)
```

## Async Client

The SDK also exports an `async` client so that you can make non-blocking calls to our API.

```python
from deeptune.client import AsyncDeeptuneApi

client = AsyncDeeptuneApi(
    xi_api_key="YOUR_XI_API_KEY",
    token="YOUR_TOKEN",
)
await client.text_to_speech.generate(
    prompt_audio_uri="prompt_audio_uri",
    target_language="target_language",
    target_text="target_text",
)
```

## Contributing

While we value open-source contributions to this SDK, this library is generated programmatically.
Additions made directly to this library would have to be moved over to our generation code,
otherwise they would be overwritten upon the next generated release. Feel free to open a PR as
a proof of concept, but know that we will not be able to merge it as-is. We suggest opening
an issue first to discuss with us!

On the other hand, contributions to the README are always very welcome!
