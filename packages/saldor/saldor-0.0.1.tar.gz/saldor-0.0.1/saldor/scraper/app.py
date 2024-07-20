from flask import Flask, request, jsonify, render_template, Response
from bs4 import BeautifulSoup
import requests
from typing import Dict, Callable, Union
from markdownify import markdownify
import re
import ollama
import os

app = Flask(__name__)

scrapes: Dict[str, str] = {}


def reduce_newlines(text):
    # Replace runs of 3 or more newlines with exactly 2 newlines
    reduced_text = re.sub(r"\n{3,}", "\n\n", text)
    return reduced_text


def scrape_url(url: str) -> str:
    cache_dir = "request_cache"
    os.makedirs(cache_dir, exist_ok=True)
    cache_file_path = os.path.join(cache_dir, url.replace("/", "_") + ".html")

    if os.path.exists(cache_file_path):
        with open(cache_file_path, "r", encoding="utf-8") as cache_file:
            page = cache_file.read()
    else:
        response = requests.get(url)
        response.encoding = "utf-8"
        page = response.text
        with open(cache_file_path, "w", encoding="utf-8") as cache_file:
            cache_file.write(page)

    return page


def scrape_jina(url: str) -> str:
    cache_dir = "jina_cache"
    os.makedirs(cache_dir, exist_ok=True)
    cache_file_path = os.path.join(cache_dir, url.replace("/", "_") + ".html")

    if os.path.exists(cache_file_path):
        with open(cache_file_path, "r", encoding="utf-8") as cache_file:
            page = cache_file.read()
    else:
        response = requests.get(f"https://r.jina.ai/{url}")
        response.encoding = "utf-8"
        page = response.text
        with open(cache_file_path, "w", encoding="utf-8") as cache_file:
            cache_file.write(page)
    return page


def scrape_base(page: str) -> str:
    if page != "":
        scrapes["base"] = page
    else:
        return "No page found"


def scrape_with_ollama(page: str) -> str:
    print("starting ollama")
    if page != "":
        response = ollama.chat(
            model="llama3-gradient",
            messages=[
                {
                    "role": "user",
                    "content": f"The following is text scrapped from a website. Could you format it to make it readable for an LLM?: {scrapes['bs4-text']}",
                },
            ],
        )
        scrapes["ollama"] = response["message"]["content"]
        print("finished ollama")
    else:
        return "No page found"


def scrape_with_base_bs4(page: str) -> Union[str, None]:
    if page != "":
        soup = BeautifulSoup(page, "html.parser")
        scrapes["bs4-base"] = soup.prettify()
    else:
        return "No page found"


def scrape_with_text_bs4(page: str) -> Union[str, None]:
    if page != "":
        soup = BeautifulSoup(page, "html.parser")
        res = soup.text
        res = reduce_newlines(res)
        scrapes["bs4-text"] = res
    else:
        return "No page found"


def scrape_with_markdownify(page: str) -> Union[str, None]:
    if page != "":
        res = markdownify(page)
        res = reduce_newlines(res)
        scrapes["markdownify"] = res
    else:
        return "No page found"


scrapers: list[Callable[[str], Union[str, None]]] = [
    scrape_base,
    scrape_with_base_bs4,
    scrape_with_text_bs4,
    scrape_with_markdownify,
    # scrape_with_ollama
]


@app.route("/")
def home() -> str:
    return render_template("index.html")


@app.route("/scrape", methods=["POST"])
def scrape() -> Response:
    url: str = request.form["url"]
    if not url:
        return jsonify({"error": "Invalid URL"}), 400
    page = scrape_url(url)

    scrapes["jina"] = scrape_jina(url)

    for scraper in scrapers:
        scraper(page)

    return jsonify({"result": "Done!"})


@app.route("/view", methods=["GET"])
def view() -> Response:
    method: str = request.args.get("method")
    if method not in scrapes:
        return jsonify({"error": "Invalid method"}), 400
    return jsonify({"result": scrapes[method]})


if __name__ == "__main__":
    app.run(debug=True, port=12345)
