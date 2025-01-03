from flask import Flask, jsonify, request, send_from_directory
import threading
from game_state import get_current_question_data, reset_game

app = Flask(__name__, static_folder="static", template_folder="templates")
player_buzzed = None
buzz_lock = threading.Lock()

@app.route("/")
def index():
    # Serve the buzzer interface
    return send_from_directory("static", "index.html")

@app.route("/buzz", methods=["POST"])
def buzz():
    global player_buzzed
    with buzz_lock:
        if player_buzzed is None:
            data = request.json
            player_buzzed = data.get("player")
    return jsonify({"status": "success"})

@app.route("/reveal/<int:answer_index>", methods=["POST"])
def reveal_answer(answer_index):
    data = get_current_question_data()
    if data and 0 <= answer_index < len(data["revealed"]):
        data["revealed"][answer_index] = True
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid answer index"}), 400

@app.route("/reset_game", methods=["POST"])
def reset_game_route():
    reset_game()
    return jsonify({"status": "success"})

def reset_buzzer():
    global player_buzzed
    with buzz_lock:
        player_buzzed = None

def start_flask():
    app.run(host="0.0.0.0", port=8000, debug=False)

if __name__ == "__main__":
    start_flask()
