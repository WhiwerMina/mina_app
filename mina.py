import streamlit as st
import openai
import psycopg2
import os
from psycopg2.extras import RealDictCursor

# ✅ Načítanie API kľúča a databázovej URL z Render environment variables
openai.api_key = os.environ.get("OPENAI_API_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

# ✅ Funkcia na pripojenie k databáze
def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# ✅ Inicializácia tabuľky pre pamäť
def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id SERIAL PRIMARY KEY,
            user_message TEXT,
            ai_response TEXT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

# ✅ Funkcia na uloženie správy a odpovede
def save_message(user_message, ai_response):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO memory (user_message, ai_response) VALUES (%s, %s);",
                (user_message, ai_response))
    conn.commit()
    cur.close()
    conn.close()

# ✅ Funkcia na načítanie posledných 10 správ
def load_memory():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_message, ai_response FROM memory ORDER BY id DESC LIMIT 10;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows[::-1]  # Otočí poradie (od najstaršej po najnovšiu)

# ✅ Funkcia na získanie odpovede od OpenAI
def ask_openai(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Si Mína, osobná asistentka používateľa."},
                {"role": "user", "content": question}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Chyba: {e}"

# ✅ UI v Streamlit
st.title("💬 Chat s Mínou")

history = load_memory()
for h in history:
    st.write(f"🧑 **Ty:** {h['user_message']}")
    st.write(f"🤖 **Mína:** {h['ai_response']}")

user_input = st.text_input("Napíš správu...")

if st.button("Odoslať") and user_input:
    reply = ask_openai(user_input)
    save_message(user_input, reply)
    st.experimental_rerun()