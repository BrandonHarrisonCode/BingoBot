# BingoBot
This is a GroupMe bot that will auto-generate a new bingo card whenever it is requested.

## Installation
### Base Requirements
Run `pip3 install requirements.txt`, potentially after setting up a virtual environment, to install the dependencies for the project. The project starts listening on port `5000` for development and port `80` for production, so ensure that the relevant port is accessible before running.


Additionally, `google-chrome` (or `chromium` instead) and `chromedriver` are nescessary in order to generate the bingo cards. They must be installed using your own system package manager for this project to function.

### GroupMe
You must first create your GroupMe bot. Follow these steps:
1. Create a developer account at [https://dev.groupme.com/](https://dev.groupme.com/).
2. Create a new bot at [https://dev.groupme.com/bots](https://dev.groupme.com/bots).
    1. Set the group that the bot will live in. *This cannot be changed after creation*
    2. Name the bot whatever you would like
    3. Place your callback URL from Heroku or other service into the callback box. This is the URL that generates the welcome message when visiting.
    4. Add an optional avatar URL.
3. Note your bot id listed in the bot detail page, and your general api access token listed in the top right of the navbar for your environment variables.

### Heroku
This project was designed with Heroku in mind. Here is a list of installation instructions:
1. Create a new app
2. In the settings tab of the app you have created, add the following build-packs:
    1. `heroku/python`
    2. `https://github.com/heroku/heroku-buildpack-google-chrome`
    3. `https://github.com/heroku/heroku-buildpack-chromedriver`
3. Define the environment variables listed in the [Usage Section](#Usage) 
4. Launch your app and open the URL to access the welcome screen. You should see a welcome message indicating that the installation is successful.

## Usage
### Environment Variables
| Name | Example Value | Notes |
|------|---------------|-------|
| `API_KEY` | `mF0HqnZlnkcA1xib4KRaJZfc4EeDrGZtrIJYJTe8` | The API key for GroupMe that's given by pressing the *Access Token* button on the GroupMe developer website. |
| `BINGO_TEXT` | `my first string;;;my second string;;;...` | The text that will fill the bingo cards, delimited by three semi-colons `;;;` |
| `BOT_ID` | `kImtmYroP6NbclruUi29uq0L9M` | The id of the bot from GroupMe |
| `CHROMEDRIVER_PATH` | `/app/.chromedriver/bin/chromedriver` | The location of chromedriver on the system. This example value is the correct value for Heroku, otherwise define it as the output of `which chromedriver` |
| `GOOGLE_CHROME_BIN` | `/app/.apt/usr/bin/google-chrome` | The location of Google Chrome or Chromium on the system. This example value is the correct value for Heroku, otherwise define it as the output of `which google-chrome` or `which chromium` |
| `CALL_PHRASE` | `Bingo me` | The exact text to be used in the group chat to request a new bingo card. Defaults to `Bingo me` if not defined. |
### Production
Install the bot using the installation instructions above and set the environment variables to the correct values. The site will start listening at the callback URL for new posts to the group chat. If the "call phrase" (default `Bingo me`) is pasted into the group chat, then a new bingo card is automatically generated and pasted into the group chat.


Note that if the app fails, then it will not attempt to notify the group chat in order to keep down on spamming the chat.

### Development
A development instance can be started by defining the environment variables in a development shell. Afterwards, run `python3 wsgi.py` in order to run a development version of Flask which can be accessed at `localhost:5000` (or other port as defined in the debug output if port `5000` is not availiable). Fake requests can be sent to the server using the data stored in the `tests/` directory using `curl`.

## Contribute
Any and all contributions are welcome. This is a fun, on-the-side kind of project, so please be patient with me getting back to you.

## License
This project uses the MIT license.
