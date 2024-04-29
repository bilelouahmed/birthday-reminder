from controllers.whatsapp import Whatsapp
from controllers.rag import *
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, NotFound, ServiceUnavailable, Forbidden
import time
from utils import *

rag = Neo4jGPTQuery(rag=True)

session = Whatsapp()

app = Flask(__name__)
CORS(app)

NOTIFIED = read_file_list("/lists/notified.txt")

DELAY = 86400  # 1 day


@app.post("/api/add_notified_conversation")
def add_to_whitelist():
    number = request.json.get("number", "")

    if not (number):
        raise BadRequest(
            "One or several fields are missing. Please, provide with phone number in format '{indicative without +}{phone number without 0}'."
        )

    if set(request.json.keys()) - {"number"}:
        raise BadRequest(
            "An extra field has been received. Please, check you provide your request with number (str)."
        )

    formatted_number = re.findall(r"\d{11,12}(?:-\d{10})?", str(number))

    if len(formatted_number) == 0:
        raise BadRequest(
            "Please, check you provide the phone number with the good format ({indicative without +}{phone number without 0})."
        )

    with open("notified.txt", "a") as file:
        file.write(formatted_number + "\n")

    return jsonify(
        {
            "message": f"Number {formatted_number} successfully added to whitelist. It will now be notified of the birthday of family members."
        }
    )


@app.post("/")
def main():
    while True:
        birthday = []
        if len(birthday) == 1:
            message = f"C'est l'anniversaire de {birthday[0]} aujourd'hui ! Joyeux anniversaire !"
        elif len(birthday) > 1:
            message = f"C'est l'anniversaire de {birthday[0]}, "
            print("1 : ", message)
            for i in range(1, len(birthday) - 1):
                message += f"{birthday[i]}, "
                print(i, ":", message)
            message = (
                message[:-2] + f" et {birthday[-1]} aujourd'hui ! Joyeux anniversaire !"
            )

        if len(birthday) > 0:
            for number in NOTIFIED:
                session.send_message(id=number, message=message)
        time.sleep(DELAY)


@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return jsonify(error=str(e)), 400


@app.errorhandler(NotFound)
def handle_not_found_error(e):
    return jsonify(error=str(e)), 404


@app.errorhandler(ServiceUnavailable)
def handle_service_unavailable(e):
    return jsonify(error=str(e)), 503


@app.errorhandler(Forbidden)
def handle_forbidden(e):
    return jsonify(error=str(e)), 403


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)
