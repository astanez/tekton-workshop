from flask import Flask
import os

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello from Python on OpenShift!\n"


@app.route("/health")
def health():
    return "ok\n", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
