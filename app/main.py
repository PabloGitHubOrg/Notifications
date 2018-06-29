#!/usr/bin/env python3
from flask import Flask, request
from hashlib import sha1

import hmac
import os
import requests

app = Flask("webhooks-github")

SECRET_TOKEN = os.environ["SECRET_TOKEN"]
API_TOKEN = os.environ["API_TOKEN"]
NOTIFY_USER = os.environ["NOTIFY_USER"]
NOTIFY_REPO = os.environ["NOTIFY_REPO"]
ISSUES_URL = "https://api.github.com/repos/" + NOTIFY_REPO + "/issues"


def verify_signature():
    """Verifies signature sent in header 'X-Hub-Signature'

    Inspired by <https://simpleisbetterthancomplex.com/tutorial/2016/10/31/how-to-handle-github-webhooks-using-django.html>
    """
    header_signature = request.headers.get("X-Hub-Signature")
    if header_signature is None:
        return False
    sha_name, signature = header_signature.split('=')
    mac = hmac.new(bytes(SECRET_TOKEN, 'utf-8'), msg=request.data, digestmod=sha1)
    return hmac.compare_digest(mac.hexdigest(), signature)


def create_issue(repo_name):
    """Create an issue about a deleted repository

    https://developer.github.com/v3/issues/#create-an-issue
    """

    headers = {"Authorization": "token " + API_TOKEN}
    payload = {
        "title": "A repository has been deleted",
        "body": "This is an automated issue to notify that the repository " + repo_name + " has just been deleted\n\n/cc @" + NOTIFY_USER,
        "labels": ["webhook"]
    }
    app.logger.info("Creating issue")
    req = requests.post(ISSUES_URL, json=payload, headers=headers)
    if req.status_code != 201:
        app.logger.error("Error creating issue")
        return False
    return True


@app.route("/postreceive", methods=['POST'])
def postreceive():
    payload = request.get_json()
    if not verify_signature():
        app.logger.error("Signature does not match")
        return "Signature does not match", 400

    action = payload["action"]
    if action != "deleted":
        app.logger.info("Ignoring action: " + action)
        return "Success", 200

    app.logger.info("Deleted repository detected!")

    repository = payload["repository"]["full_name"]
    result = create_issue(repository)
    if result:
        return "Success", 201
    else:
        return "Error creating issue", 500


@app.route("/")
def hello_world():
    return "Hello, World! My master is " + NOTIFY_USER + " and I will notify about deleted repos at " + NOTIFY_REPO


if __name__ == "__main__":
    app.run()
