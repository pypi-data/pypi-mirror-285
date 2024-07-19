# pdf-llm-tools

`pdf-llm-tools` is a family of AI pdf utilities:

- `pdfllm-titler` renames a pdf with metadata parsed from the filename and
  contents. In particular it renames it as `YEAR-AUTHOR-TITLE.pdf`.
- (todo) `pdfllm-toccer` adds a bookmark structure parsed from the detected
  contents table of the pdf.

Currently OpenAI's `gpt-3.5-turbo-1106` is hardcoded as the LLM backend. The
program requires an API key via option, envvar, or manual input.

## Installation

```
pip install pdf-llm-tools
```

## Usage

These utilities require all PDFs to have a correct OCR layer. Run something like
[OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF) if needed.

### pdfllm-titler

```
usage: pdfllm-titler [-h] [--openai-api-key OPENAI_API_KEY] [--first-page FIRST_PAGE] [--last-page LAST_PAGE] fpath [fpath ...]

Rename PDF documents according to their contents.

positional arguments:
  fpath                 PDF to rename

options:
  -h, --help            show this help message and exit
  --openai-api-key OPENAI_API_KEY
                        OpenAI API key
  --first-page FIRST_PAGE, -f FIRST_PAGE
                        First page of pdf to read (default: 1)
  --last-page LAST_PAGE, -l LAST_PAGE
                        Last page of pdf to read (default: 5)
```




