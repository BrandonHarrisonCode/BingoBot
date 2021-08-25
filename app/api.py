"""A GroupMe bot to autogenerate bingo cards"""
import random
import os
from datetime import datetime
import json
from pytz import timezone
import requests

from flask import Flask, request
from flask_cors import CORS  # type: ignore
from selenium import webdriver

api = Flask(__name__)
CORS(api)

API_KEY = os.environ["API_KEY"]
BOT_ID = os.environ["BOT_ID"].strip()
CALL_PHRASE = os.environ.get("CALL_PHRASE", "Bingo me")
USER_LINK_ID = str(os.environ.get("USER_LINK_ID", "-1")).strip()
LINK_CALLWORDS = os.environ.get("LINK_CALLWORDS", "send")
LINK_RESPONSE_TEXT = os.environ.get("LINK_RESPONSE_TEXT", "").split(";")
GROUP_CALL_DAY_OF_THE_WEEK = int(os.environ.get("GROUP_CALL_DAY_OF_THE_WEEK", 2))
KEEPERS_CALL_PHRASE = os.environ.get("KEEPERS_CALL_PHRASE", "Keepers?")
KEEPERS_RESPONSE = os.environ.get("KEEPERS_RESPONSE", "Keeper rules.")

options = webdriver.ChromeOptions()
options.headless = True
options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")


@api.route("/", methods=["GET"])
def index():
    """The debug method for the root path"""
    return "This is the Bingo Bot, how may I help you?"


@api.route("/", methods=["POST"])
def groupme_callback():
    """The entry point for GroupMe callbacks"""
    data = request.get_json()
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"Recieved request ({current_time}): {data}")
    if is_bingo_request(data):
        return do_bingo_request()
    if is_link_request(data):
        return do_link_request()
    if is_keeper_request(data):
        return do_keeper_request()
    print("No call phrase recognized.")
    return "No data to process."


def is_bingo_request(data):
    """Returns a boolean describing if the message is a bingo request"""
    return data.get("text", "").lower().strip() == CALL_PHRASE.lower().strip()


def do_bingo_request():
    """Creates and submits a bingo response"""
    print("Call phrase recognized, generating bingo card.")
    return generate_bingo_card()


def is_link_request(data):
    """Returns a boolean describing if the message is a link request"""
    timestamp = data.get("created_at", "")
    local_message_time = datetime.fromtimestamp(timestamp, timezone("America/Chicago"))
    day_of_the_week = local_message_time.weekday()
    return (
        str(data.get("sender_id", "")).strip() == USER_LINK_ID
        and day_of_the_week == GROUP_CALL_DAY_OF_THE_WEEK
        and any(
            [
                callword.lower().strip() in data.get("text", "").lower().strip()
                for callword in LINK_CALLWORDS.split(",")
            ]
        )
    )


def do_link_request():
    """Creates and submits a link response"""
    print("User asking for link, sending response")
    random_response = random.choice(LINK_RESPONSE_TEXT)
    try:
        text_response(random_response)
        return "Success: link!"
    except RuntimeError as exception:
        return str(exception)


def is_keeper_request(data):
    """Returns a boolean describing if the message is a keeper request"""
    return data.get("text", "").lower().strip() == KEEPERS_CALL_PHRASE.lower().strip()


def do_keeper_request():
    """Creates and submits a keeper response"""
    print("User asking for keeper info, sending response")
    text = KEEPERS_RESPONSE
    try:
        text_response(text)
        return "Success: link!"
    except RuntimeError as exception:
        return str(exception)


@api.route("/generate")
def generate_bingo_card():
    """Generates a unique bingo card from scratch, and uploads it to GroupMe"""
    with webdriver.Chrome(
        executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options
    ) as driver:
        driver.get(generate_html())
        elem = driver.find_element_by_id("bingocard")
        screenshot_data = elem.screenshot_as_png
    try:
        image_url = upload_image_to_groupme(screenshot_data)
        post_image_to_chat(image_url)
    except RuntimeError as exception:
        return str(exception)
    return "Success: photo!"


def upload_image_to_groupme(screenshot_data):
    """Uploads the image of the bingo card (in binary data) to GroupMe's image servers"""
    upload_url = "https://image.groupme.com/pictures"
    headers = {
        "X-Access-Token": API_KEY,
        "Content-Type": "image/png",
    }
    result = requests.post(upload_url, data=screenshot_data, headers=headers)
    if not result.ok:
        print(result)
        print(result.json())
        raise RuntimeError("There was an error while uploading the image.")
    return result.json()["payload"]["picture_url"]


def text_response(text):
    """Sends a text message to the group chat"""
    chat_url = "https://api.groupme.com/v3/bots/post"
    data = json.dumps(
        {
            "bot_id": BOT_ID,
            "text": text,
        }
    )
    print(data)
    result = requests.post(chat_url, data=data)
    if not result.ok:
        print(result)
        print(result.json())
        raise RuntimeError(
            "There was an error while posting the text response to chat."
        )


def post_image_to_chat(image_url):
    """Sends a message to the group chat with the bingo card"""
    chat_url = "https://api.groupme.com/v3/bots/post"
    data = json.dumps(
        {
            "bot_id": BOT_ID,
            "picture_url": image_url,
            "text": "Here's your bingo card!",
        }
    )
    print(data)
    result = requests.post(chat_url, data=data)
    if not result.ok:
        print(result)
        print(result.json())
        raise RuntimeError("There was an error while posting the image to chat.")


def generate_html():
    """Creates the bingo card in HTML"""
    html = start_html_doc()
    terms = get_bingo_terms()
    random.shuffle(terms)
    html.append(generate_table(terms))
    html.append("</body></html>")

    return "data:text/html;charset=utf-8," + "".join(html)


def get_bingo_terms():
    """Parses the text for the bingo boxes from the environment"""
    split_string = ";;;"
    if "BINGO_TEXT" in os.environ:
        terms = os.environ["BINGO_TEXT"].split(split_string)
    else:
        with open("sample_terms.txt", "r") as in_file:
            terms = [line.strip() for line in in_file.readlines()]
            terms = [term for term in terms if term]
    return terms


def start_html_doc():
    """Sets the preamble for the HTML to define styles"""
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
    """Generates an HTML table representation of the bingo card for terms"""
    box_contents = (
        terms[:12] + ["Logan is playing The Show (FREE SPACE)"] + terms[12:24]
    )
    res = "<table id='bingocard'>\n"
    for i, term in enumerate(box_contents):
        if i % 5 == 0:
            res += "\t<tr>\n"
        res += "\t\t<td>" + term + "</td>\n"
        if i % 5 == 4:
            res += "\t</tr>\n"
    res += "</table>\n"
    return res


if __name__ == "__main__":
    api.run(host="0.0.0.0", debug=False, port=os.environ.get("PORT", 80))
