import streamlit as st
from openai import OpenAI
import psycopg2
import os

# Inicializácia OpenAI klienta
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Funkcia na pripojenie k databáze
def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

# Načítanie histórie správ z databázy
def load_messages():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT role, content FROM messages ORDER BY id;")
    rows = cur.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in rows]

# Uloženie správy do databázy
def save_message(role, content):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (role, content) VALUES (%s, %s);", (role, content))
    conn.commit()
    conn.close()

# Nastavenie stránky
st.set_page_config(page_title="Chat s Mínou", page_icon="💬")
st.title("Chat s Mínou")

# Načítanie histórie
messages = load_messages()

# Zobrazenie histórie
for msg in messages:
    if msg["role"] == "user":
        st.write(f"Ty: {msg['content']}")
    elif msg["role"] == "assistant":
        st.write(f"Mína: {msg['content']}")

# Vstup používateľa
user_input = st.text_input("Napíš správu:")

# Odoslanie správy
if st.button("Odoslať") and user_input.strip() != "":
    save_message("user", user_input)

    # Príprava kontextu pre API
    api_messages = [{"role": "system", "content": "Si Mína, milá a priateľská AI, ktorá odpovedá úprimne a srdečne."}]
    api_messages += load_messages()

    # Volanie API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=api_messages
    )

    # Správny prístup ku content
    assistant_reply = response.choices[0].message.content

    # Uloženie odpovede a refresh stránky
    save_message("assistant", assistant_reply)
    st.rerun()