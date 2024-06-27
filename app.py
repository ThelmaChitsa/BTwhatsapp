"""
Copyright (c) Meta Platforms, Inc. and affiliates.
All rights reserved.

This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""

import json
from flask import Flask, render_template, request
import flask
import requests
from message_helper import get_templated_message_input, get_text_message_input, send_message
from flights import get_flights
from flask import current_app
import datetime
# from livereload import Server, LiveReload

app = Flask(__name__)
# LiveReload(app)

with open('config.json') as f:
    config = json.load(f)

app.config.update(config)

@app.route("/")
def index():
    return render_template('index.html', name=__name__)

@app.route('/welcome', methods=['POST'])
async def welcome():
  data = get_text_message_input(app.config['RECIPIENT_WAID']
                                , 'Whatsapp POC w/ Python!)')
  await send_message(data)
  return flask.redirect(flask.url_for('catalog'))

@app.route("/catalog")
def catalog():
    return render_template('catalog.html', title='Whatsapp Proof of Concept', flights=get_flights())

@app.route("/buy-ticket", methods=['POST'])
async def buy_ticket():
    # Send template message
    url = 'https://graph.facebook.com' + f"/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"
    headers = {
        "Authorization": "Bearer " + current_app.config['ACCESS_TOKEN'],
        "Content-Type": "application/json"
    }
    payload = get_templated_message_input()

    try:
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            message = "Templated message sent successfully!"
        else:
            message = f"Failed to send templated message. Status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        message = f"An error occurred while sending the templated message: {str(e)}"

    # Redirect to the catalog page with the message
    return flask.redirect(flask.url_for('catalog', message=message))

@app.route('/send-message', methods=['POST'])
async def send_custom_message():
    custom_message = request.form['message']
    data = get_text_message_input(app.config['RECIPIENT_WAID'], custom_message)
    await send_message(data)
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return flask.redirect(flask.url_for('catalog'))





# async def send_message(data):
#     custom_message = request.form['message']
#     data = get_text_message_input(app.config['RECIPIENT_WAID'], custom_message)
#     await send_message(data)
#     return flask.redirect(flask.url_for('catalog'))

# async def buy_ticket():
#   get_templated_message_input()
#   # flight_id = int(request.form.get("id"))
#   # flights = get_flights()
#   # flight = next(filter(lambda f: f['flight_id'] == flight_id, flights), None)
#   # data = get_templated_message_input(app.config['RECIPIENT_WAID'], flight)
#   # await send_message(data)
#   return flask.redirect(flask.url_for('catalog'))

if __name__ == '__main__':
    app.run(debug=True)