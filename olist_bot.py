import requests
import json
from flask import Flask, request, Response
import re
import os

TOKEN = '1862189868:AAGHzOTx26BX3-W5U5uFqbWeFwRYTkZuVHI'
BOT_BASE_URL = 'https://api.telegram.org/bot' + TOKEN
BOT_GET_ME = BOT_BASE_URL + '/getMe'
BOT_UPDATE = BOT_BASE_URL + '/getUpdates'
BOT_SEND_MESSAGE = BOT_BASE_URL + '/sendMessage?chat_id='
print("BOT_GET_ME: ", BOT_GET_ME)
print("BOT_SEND_MESSAGE: ", BOT_SEND_MESSAGE)
print("BOT_UPDATE: ", BOT_UPDATE)
print("BOT_SEND_MESSAGE: ", BOT_SEND_MESSAGE+str(1934548946)+'&text=sadasd')


def send_message(chat_id, text):
    url = BOT_SEND_MESSAGE + str(chat_id)
    r = requests.post(url, json={'text': text})
    print("Status Code:", r.status_code)
    return None


def parse_message(message):
    chat_id = message['message']['chat']['id']
    region = message['message']['text']

    region = region.strip(' ').replace('/', '')
    return chat_id, region


def forecast(region_requested):
    url = 'https://olist-arima-forecast.herokuapp.com/olist/forecast'
    header = {'Content-type': 'application/json'}
    region = json.dumps({"region": region_requested})

    r = requests.post(url, data=region, headers=header)
    return r.text


def check_response(response):
    predictions = re.findall(r"(?:\d+(?:\.\d*)?|\.\d+)", response)
    if predictions:
        return predictions, True
    else:
        return response, False


app = Flask(__name__)


@app.route('/', methods=['GET','POST'])
def bot_answer():
    # if request.method == 'POST':
    message = request.get_json()

    chat_id, region = parse_message(message)

    response = forecast(region)
    response, is_prediction = check_response(response)

    if is_prediction:
        message = '''{} region will sell:\n  R${:,.2f} in July.\n  R${:,.2f} in August.\n  R${:,.2f} in September.'''.\
                    format(region, float(response[0]), float(response[1]), float(response[2]))
        send_message(chat_id, message)
        return Response('Ok', status=200)
    else:
        send_message(chat_id, response)
        return Response('Ok', status=200)


if __name__ == "__main__":
    port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port)

    # region = "nordeste"
    # response = forecast(region)
    # response, is_prediction = check_response(response)
    #
    # if is_prediction:
    #     message = '''{} region will sell:\n  R$ {:,.2f} in July.\n  R$ {:,.2f} in August.\n  R$ {:,.2f} in September.'''. \
    #         format(region, float(response[0]), float(response[1]), float(response[2]))
    #     print(message)
    # else:
    #     print(response)
