#!/usr/bin/python3
# Originally from GitHub user "hrs"

import random
import sys
from selenium import webdriver

# check for the right # of args
if len(sys.argv) != 4:
    print("USAGE: " + sys.argv[0], " [file of terms] [output file] [# of cards]")
    print("Example: " + sys.argv[0] + " bingo_terms.txt bingo.html 20")
    sys.exit(1)

# read in the bingo terms
with open(sys.argv[1], 'r') as in_file:
    terms = [line.strip() for line in in_file.readlines()]
    terms = [term for term in terms if term]

# XHTML4 Strict, y'all!
head = ("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01//EN\" \"http://www.w3.org/TR/html4/strict.dtd\">\n"
        "<html lang=\"en\">\n<head>\n"
        "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\">\n"
        "<title>Bingo Cards</title>\n"
        "<style type=\"text/css\">\n"
        "\tbody { font-size: 14px; font-family: 'Helvetica', 'Arial', sans-serif; width: 20em; height: 20em; }\n"
        "\ttable { border-spacing: 2px; table-layout: fixed; }\n"
        "\t.newpage { page-break-after:always; }\n"
        "\ttr { }\n"
        "\ttd { text-align: center; border: thin black solid; padding: 10px; width: 20%; height: 20%; }\n"
        "</style>\n</head>\n<body>\n")

# Generates an HTML table representation of the bingo card for terms
def generateTable(terms, pagebreak = True):
    ts = terms[:12] + ["FREE SPACE"] + terms[12:24]
    if pagebreak:
        res = "<table class=\"newpage\">\n"
    else:
        res = "<table id='bingocard'>\n"
    for i, term in enumerate(ts):
        if i % 5 == 0:
            res += "\t<tr>\n"
        res += "\t\t<td>" + term + "</td>\n"
        if i % 5 == 4:
            res += "\t</tr>\n"
    res += "</table>\n"
    return res

html = []
html.append(head)
cards = int(sys.argv[3])
for i in range(cards):
    random.shuffle(terms)
    if i != cards - 1:
        html.append(generateTable(terms))
    else:
        html.append(generateTable(terms, False))
html.append("</body></html>")
html = "".join(html)

options = webdriver.ChromeOptions()
options.headless = True
with webdriver.Chrome(options=options) as driver:
    driver.get('data:text/html;charset=utf-8,' + html)
    elem = driver.find_element_by_id('bingocard')
    elem.screenshot(sys.argv[2])
