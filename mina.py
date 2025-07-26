import streamlit as st
import openai
import psycopg2
import os

# Nastavenie OpenAI API kľúča z prostredia
openai.api_key = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Funkcia na vytvorenie tabuľky v databáze
def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            role TEXT,
            content TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

# Funkcia na uloženie správy
def save_message(role, content):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (role, content) VALUES (%s, %s)", (role, content))
    conn.commit()
    cur.close()
    conn.close()

# Funkcia na načítanie histórie
def load_messages():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT role, content FROM messages ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# Inicializácia databázy
init_db()

st.title("Chat s Mínou")

# Zobrazenie histórie
messages = load_messages()
for role, content in messages:
    if role == "user":
        st.markdown(f"🟠 **Ty:** {content}")
    else:
        st.markdown(f"🔵 **Mína:** {content}")

# Vstup používateľa
user_input = st.text_input("Napíš správu:")

if st.button("Odoslať"):
    if user_input.strip():
        save_message("user", user_input)

        # Odpoveď od OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Si Mína, priateľská AI pomocníčka."},
                *[{"role": r, "content": c} for r, c in load_messages()],
                {"role": "user", "content": user_input},
            ]
        )

        reply = response["choices"][0]["message"]["content"]
        save_message("assistant", reply)
        st.experimental_rerun()