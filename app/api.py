from flask import Flask, jsonify, make_response
from flask_cors import CORS
import random
import sys
import os
from selenium import webdriver
from PIL import Image
from io import BytesIO

api = Flask(__name__)
CORS(api)
options = webdriver.ChromeOptions()
options.headless = True
options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")


@api.route("/")
def index():
    return "This is the Bingo Bot, how may I help you?"


@api.route("/generate")
def generate_bingo_card():
    with webdriver.Chrome(
        executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options
    ) as driver:
        driver.get(generate_html())
        elem = driver.find_element_by_id("bingocard")
        elem.screenshot("screenshot.png")
    upload_image_to_groupme()
    return "Done!"


def upload_image_to_groupme():
    upload_url = "https://image.groupme.com"
    pass


def generate_html():
    html = start_html_doc()
    terms = get_bingo_terms()
    random.shuffle(terms)
    html.append(generate_table(terms))
    html.append("</body></html>")

    return "data:text/html;charset=utf-8," + "".join(html)


def get_bingo_terms():
    with open(os.environ.get("TERMS_FILE", "sample_terms.txt"), "r") as in_file:
        terms = [line.strip() for line in in_file.readlines()]
        terms = [term for term in terms if term]
    return terms


def start_html_doc():
    head = """
    <!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01//EN\" \"http://www.w3.org/TR/html4/strict.dtd\">
            <html lang=\"en\">\n<head>
            <meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\">
            <title>Bingo Cards</title>
            <style type=\"text/css\">
            \tbody { font-size: 14px; font-family: 'Helvetica', 'Arial', sans-serif; width: 20em; height: 20em; }
            \ttable { border-spacing: 2px; table-layout: fixed; }
            \t.newpage { page-break-after:always; }
            \ttr { }
            \ttd { text-align: center; border: thin black solid; padding: 10px; width: 20%; height: 20%; }
            </style>\n</head>\n<body>\n")"""
    return [head]


def generate_table(terms):
    "Generates an HTML table representation of the bingo card for terms"
    ts = terms[:12] + ["Logan is playing The Show (FREE SPACE)"] + terms[12:24]
    res = "<table id='bingocard'>\n"
    for i, term in enumerate(ts):
        if i % 5 == 0:
            res += "\t<tr>\n"
        res += "\t\t<td>" + term + "</td>\n"
        if i % 5 == 4:
            res += "\t</tr>\n"
    res += "</table>\n"
    return res


if __name__ == "__main__":
    api.run(host="0.0.0.0", debug=False, port=os.environ.get("PORT", 80))
