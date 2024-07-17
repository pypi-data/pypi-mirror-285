import hmac
import hashlib
import json
import requests
from loguru import logger
from typing import Any, Dict
from models import request as req, response as res
import traceback
from . import utils


class MoveoWebhookHandler:
    def __init__(self, secret: str, debug: bool = False):
        self.secret = secret
        utils.configure_logger(debug)

    def process_request(self, request_body: Any, signature: str):
        try:
            if self.__verify_signature(signature, request_body):
                joke_language = req.get_joke_language(request_body)
                logger.info(f"Detected joke language: {joke_language}")
                response = self.__build_moveo_response(joke_language)
                return response.model_dump(exclude_none=True)
            logger.warning(f"Signature verification failed: {signature}")
            return res.err_response("Signature verification failed").model_dump(
                exclude_none=True
            ), 403

        except Exception as e:
            logger.error(f"Exception occurred: {traceback.format_exc()}")
            return res.err_response(f"Exception occurred: {str(e)}").model_dump(
                exclude_none=True
            ), 500

    def __verify_signature(self, signature: str, payload: Any) -> bool:
        if not signature:
            return False

        bytes_payload = json.dumps(payload).encode("utf-8")
        token_bytes = self.secret.encode("utf-8")
        computed_hmac = hmac.new(
            key=token_bytes, msg=bytes_payload, digestmod=hashlib.sha256
        ).hexdigest()

        logger.debug(f"Payload: {bytes_payload}")
        logger.debug(f"Token Bytes: {token_bytes}")
        logger.debug(f"Computed HMAC: {computed_hmac}")
        logger.debug(f"Received Signature: {signature}")

        return hmac.compare_digest(computed_hmac, signature)

    def __build_moveo_response(self, joke_language: str):
        joke = self.__get_joke(joke_language)
        response = res.create_response(joke)
        logger.debug(f"Response to be sent: {response.model_dump_json()}")
        return response

    def __get_joke(self, language: str):
        url = f"https://v2.jokeapi.dev/joke/Any?type=single&safe-mode&lang={language}"
        response = requests.get(url)
        if response.status_code != 200:
            logger.error(f"Error fetching joke, status code: {response.status_code}")
            return "Error fetching joke. Seems like the joke database is on vacation! \
                    In the meantime, why do programmers hate nature? It has too many bugs!"

        joke_data = response.json()

        if joke_data.get("code") == 106:
            return self.__fallback_message(joke_data)
        logger.debug(f"Fetched joke: {joke_data['joke']}")
        return joke_data["joke"]

    def __fallback_message(self, joke_data:Dict[str, Any]) -> str:
        logger.error(f"Error fetching joke: {joke_data['message']}")
        message = "Well, looks like the joke database just hit the snooze button! \
                Maybe it's on a coffee break or caught up in a riveting conversation about the \
                philosophical implications of dad jokes."
        joke1 = "Why don't programmers tell jokes while programming?"
        punchline = "Because they might commit a syntax error!"
        joke2 = "If at first you don't succeed, call it version 1.0!"

        return f"{message}\n\nIn the meantime, why don't we create our own joke? Here goes:\n\n{joke1}\n{punchline}\n\n{joke2}"
