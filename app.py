from flask import Flask

app = Flask(__name__)
app.config.update(DEBUG=True)

if __name__ == "__main__":
    app.run(port=5123, debug=True)