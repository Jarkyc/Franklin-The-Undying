from flask import Flask
from threading import Thread
app = Flask('')
@app.route('/')
def main():
    return "Online"
def run():
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
def keep_alive():
    server = Thread(target=run)
    server.start()