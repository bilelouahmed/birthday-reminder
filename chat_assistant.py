from controllers.whatsapp import Whatsapp
from controllers.rag import *
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, NotFound, ServiceUnavailable, Forbidden
import argparse
import re
from utils import *

parser = argparse.ArgumentParser(
    description="Answer automatically to the Whatsapp users in the whitelist starting their messages by @titeuf."
)
parser.add_argument("--rag", action="store_true", help="Context addition with RAG")
args = parser.parse_args()

rag = Neo4jGPTQuery(rag=args.rag)

session = Whatsapp()

app = Flask(__name__)
CORS(app)

WHITELIST = read_file_list("whitelist.txt")


@app.post("/api/add_whitelist")
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

    with open("whitelist.txt", "a") as file:
        file.write(formatted_number + "\n")

    return jsonify(
        {
            "message": f"Number {formatted_number} successfully added to whitelist. It's now allowed to call the chatbot."
        }
    )


@app.post("/")
def main():
    data = request.json
    sender_number, sender, received_timestamp, message_received = (
        session.get_message_properties(data)
    )
    if sender_number is not None and sender_number in WHITELIST:
        if message_received[:7] == "@titeuf":
            response = rag.answer(question=message_received)
            session.send_message(id=sender_number, message=response)

    return "OK"


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
    app.run(host="0.0.0.0", port=5080)
