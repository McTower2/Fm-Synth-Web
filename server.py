from flask import Flask
from routes.audio_routes import audio_bp
from routes.api_routes import api_bp
from synth.class_Synthesiser import Synthesiser

app = Flask(__name__, static_folder="static")

try:
    app.synth = Synthesiser(numVoices=6)
    print("✅ Synthesizer initialized correctly")
except Exception as e:
    print(f"❌ ERROR WHILE INITIALIZING THE SYNTHESIZER: {e}")


app.register_blueprint(audio_bp)
app.register_blueprint(api_bp, url_prefix='/api')


@app.route("/")
def index():
    return app.send_static_file("index.html")


if __name__ == "__main__":
    app.run(debug=False)