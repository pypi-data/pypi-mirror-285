import argparse, json, re, os
from openai import OpenAI
import pdftotext
from .base import get_base_parser, initialize_base_opts

def make_opts():
    parser = argparse.ArgumentParser(
        description="Rename PDF documents according to their contents.",
        parents=[get_base_parser()])
    parser.add_argument("--first-page", "-f", type=int, default=1,
                        help="First page of pdf to read (default: 1)")
    parser.add_argument("--last-page", "-l", type=int, default=5,
                        help="Last page of pdf to read (default: 5)")
    parser.add_argument("fpath", type=str, nargs="+", help="PDF to rename")

    global opts
    opts = parser.parse_args()

    # Initialize common options
    initialize_base_opts(opts)

def llm_parse_metadata(pdf_name, text):
    message = ("Detect the metadata for year, author surnames, and title from"
               " the following text of the first pages of an academic paper or"
               " book. I will also provide the filename."
               " Format your response as a json object, where 'year' is an int,"
               " 'authors' is a list of surname strings, 'title' is a string,"
               " and 'error' is a boolean true if and only if you fail to"
               " complete the task."
               f" Here is the filename: '{pdf_name}'."
               f" Here is the text: {text}.")

    client = OpenAI(api_key=opts.openai_api_key)
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message},
        ]
    )

    meta = json.loads(completion.choices[0].message.content)
    return None if meta["error"] else meta

def pdf_fpath_to_text(fpath, fp, lp):
    with open(fpath, "rb") as f:
        pdf = pdftotext.PDF(f)
        return "\n\n".join([pdf[i] for i in range(fp-1, lp)])

def main():
    make_opts()

    for fpath in opts.fpath:
        # Extract metadata
        fdir = fpath[:fpath.rfind("/")+1]
        fname = fpath[fpath.rfind("/")+1:]
        text = pdf_fpath_to_text(fpath, opts.first_page, opts.last_page)
        meta = llm_parse_metadata(fname, text)
        if not meta:
            print(f"Unable to read metadata from {fpath}; skipping")
            continue

        # Create new filename
        year = meta["year"]
        author = meta["authors"][0]
        author = author[0].upper() + author[1:].lower()
        title = meta["title"].lower().replace(" ", "-")
        newfname = re.sub(r"[^a-zA-Z0-9-.]", r"", f"{year}-{author}-{title}.pdf")
        newfpath = f"{fdir}{newfname}"

        # Rename
        os.rename(fpath, newfpath)
        print(f"Renamed {fpath} to {newfpath}")
