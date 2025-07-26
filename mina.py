import streamlit as st
import psycopg2
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DB_URL = os.getenv("DATABASE_URL")

def init_db():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS memory (
        id SERIAL PRIMARY KEY,
        role TEXT,
        content TEXT
    )""")
    conn.commit()
    cur.close()
    conn.close()

def load_memory():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT role, content FROM memory ORDER BY id ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"role": r, "content": c} for r, c in rows]

def save_message(role, content):
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("INSERT INTO memory (role, content) VALUES (%s, %s)", (role, content))
    conn.commit()
    cur.close()
    conn.close()

st.title("Chat s Mínou")

init_db()
messages = load_memory()

for m in messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Napíš správu..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    save_message("user", prompt)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages + [{"role": "user", "content": prompt}]
    )

    reply = response.choices[0].message.content
    with st.chat_message("assistant"):
        st.markdown(reply)
    save_message("assistant", reply)
