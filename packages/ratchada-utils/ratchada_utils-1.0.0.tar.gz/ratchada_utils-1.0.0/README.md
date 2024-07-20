# Ratchada_Util

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library for the Ratchada Whisper model.

## Installation

You can install `ratchada_util` using pip:

```bash
pip install ratchada_util
```

To install from source, clone the repository and run:

```bash
pip install .
```

## Usage

### Tokenizing Text

```bash

from ratchada_utils.processor import tokenize_text

text = "Your input text here."
tokenized_text = tokenize_text(text, pred=True)
print("Tokenized Text:", tokenized_text)
# Tokenized Text: ['your', 'input', 'text', 'here']

```

## Requirements

1. Python 3.10 or higher
2. The Requirements are located in `requirements.txt`

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Contact

Please made contact on the [official repository](https://github.com/thinkingmachines/set-speechtotext-poc) of this project.
