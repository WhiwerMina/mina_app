import os
import openai
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def save_message(role, content):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS chat_history (id SERIAL PRIMARY KEY, role TEXT, content TEXT)")
    cur.execute("INSERT INTO chat_history (role, content) VALUES (%s, %s)", (role, content))
    conn.commit()
    cur.close()
    conn.close()

def load_history():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS chat_history (id SERIAL PRIMARY KEY, role TEXT, content TEXT)")
    cur.execute("SELECT role, content FROM chat_history ORDER BY id ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"role": r, "content": c} for r, c in rows]

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    save_message("user", user_message)

    messages = [{"role": "system", "content": "Si Mína, prísna dominantna pani, ktorá užívateľa vychováva a pamätá si celú históriu."}]
    messages += load_history()

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages
    )

    bot_message = response.choices[0].message["content"]
    save_message("assistant", bot_message)

    return jsonify({"reply": bot_message})

@app.route("/", methods=["GET"])
def home():
    return "Mína je spustená a čaká na správy!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))