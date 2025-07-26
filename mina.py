import streamlit as st
from openai import OpenAI
import psycopg2
import os

# Inicializácia OpenAI klienta
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Funkcia na pripojenie k databáze
def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")

# Funkcia na vytvorenie tabuľky, ak ešte neexistuje
def init_db():
    conn = get_connection()
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
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (role, content) VALUES (%s, %s)", (role, content))
    conn.commit()
    cur.close()
    conn.close()

# Funkcia na načítanie histórie
def load_messages():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT role, content FROM messages ORDER BY id ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in rows]

# Inicializácia databázy
init_db()

# UI
st.title("Chat s Mínou")

# Načítanie histórie
history = load_messages()
for msg in history:
    if msg["role"] == "user":
        st.markdown(f"**Ty:** {msg['content']}")
    else:
        st.markdown(f"**Mína:** {msg['content']}")

# Vstup od používateľa
user_input = st.text_input("Napíš správu:")

if st.button("Odoslať") and user_input:
    save_message("user", user_input)

    # Volanie OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Si milá a priateľská asistentka menom Mína."},
            *load_messages()  # celá história
        ]
    )

    assistant_reply = response.choices[0].message["content"]
    save_message("assistant", assistant_reply)

    st.experimental_rerun()