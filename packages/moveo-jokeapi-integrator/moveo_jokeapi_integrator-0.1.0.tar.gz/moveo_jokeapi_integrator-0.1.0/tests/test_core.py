import hmac
import hashlib
import json
from moveo_webhook import MoveoWebhookHandler
from typing import Any


def _generate_signature(secret: str, payload: Any) -> str:
    bytes_payload = json.dumps(payload).encode("utf-8")
    token_bytes = secret.encode("utf-8")
    return hmac.new(
        key=token_bytes, msg=bytes_payload, digestmod=hashlib.sha256
    ).hexdigest()


def test_process_request():
    secret = "test_secret"
    handler = MoveoWebhookHandler(secret=secret)
    request_body = {
        "channel": "test",
        "session_id": "b7c13f73-801b-4f5e-acd6-966e1b86396e",
        "brain_id": "ade02da7-256e-4765-b740-d31a2b934873",
        "lang": "en",
        "context": {"joke_language_value": "en"},
        "input": {
            "text": "Awesome! Get ready to laugh soon! 😂 Here's a joke in English for you!"
        },
        "intents": [{"intent": "amusement_request", "confidence": 0.807722270488739}],
        "entities": [
            {
                "entity": "jokeLanguage",
                "value": "en",
                "start": 53,
                "end": 60,
                "confidence": 1.0,
                "type": "string",
            }
        ],
        "debug": {
            "dialog_stack": [
                {
                    "node_id": "0d59b082-7ec3-4660-afdd-59f949ec9180",
                    "name": "Joke request",
                }
            ]
        },
        "user_message_counter": 2,
    }
    signature = _generate_signature(secret, request_body)
    response = handler.process_request(request_body, signature)
    assert response.get("Response") != []
