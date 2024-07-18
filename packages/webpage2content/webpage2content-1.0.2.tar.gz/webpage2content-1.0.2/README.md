# webpage2content

A simple Python package that takes a web page (by URL) and extracts its main human-readable content. It uses LLM technology to remove all of the boilerplate webpage cruft (headers, footers, copyright and accessibility notices, advertisements, login and search controls, etc.) that isn't part of the main content of the page.

## Installation

```bash
pip install webpage2content
```

## Usage

```python
import openai
from webpage2content import webpage2content

text = webpage2content("http://mysite.com", openai.OpenAI())
print(text)
```

## CLI

You can invoke webpage2content from the command line.

```cmd
C:> webpage2content https://slashdot.com/
```

If you don't have your OPENAI_API_KEY environment variable set, you can pass it to the CLI invocation as a second argument.

```cmd
C:> webpage2content https://slashdot.com/ sk-ABCD1234
```
