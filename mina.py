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
import streamlit as st
from openai import OpenAI

client = OpenAI()

st.set_page_config(page_title="Chat s Mínou", page_icon="💬")
st.title("Chat s Mínou")

# Inicializácia histórie
if "messages" not in st.session_state:
    st.session_state.messages = []

# Zobrazenie histórie
for msg in st.session_state.messages:
    st.write(f"Ty: {msg['user']}")
    st.write(f"Mína: {msg['mina']}")

# Vstup používateľa
user_input = st.text_input("Napíš správu:")

if st.button("Odoslať") and user_input.strip() != "":
    # Uloženie správy používateľa
    st.session_state.messages.append({"user": user_input, "mina": ""})

    # Vytvorenie zoznamu správ pre API
    chat_history = [{"role": "system", "content": "Si Mína, milá a priateľská AI, ktorá odpovedá úprimne a srdečne."}]
    for msg in st.session_state.messages:
        chat_history.append({"role": "user", "content": msg["user"]})
        if msg["mina"]:
            chat_history.append({"role": "assistant", "content": msg["mina"]})

    # Zavolanie API
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # môžeš použiť aj "gpt-4o"
        messages=chat_history,
    )

    # Opravený prístup ku content
    assistant_reply = response.choices[0].message.content

    # Uloženie odpovede
    st.session_state.messages[-1]["mina"] = assistant_reply

    # Zobrazenie odpovede
    st.write(f"Mína: {assistant_reply}")
📌 Čo s tým spraviť
Nahraj tento kód do svojho repozitára namiesto starého mina.py.

Commitni zmeny → Render automaticky redeployne appku.

Skús aplikáciu otvoriť znova – chyba už nebude.

🔹 Ak chceš, môžem k tomu pridať podporu hlasu (TTS), aby Mína aj hovorila.
Chceš rovno verziu s hlasovým výstupom?






Tvoje slová:
Takže keď tam zadam toto ,bude mať trvalú pamet?


ChatGPT povedal:
Nie, tento kód nebude mať trvalú pamäť – používa len st.session_state, čo funguje iba počas otvorenej relácie.
Keď zatvoríš stránku alebo reštartuješ aplikáciu, pamäť sa vymaže.

🔹 Ako spraviť, aby mala Mína trvalú pamäť
Potrebuješ niekde uložiť históriu konverzácií – napríklad:

do súboru (JSON, TXT)

alebo do databázy (napr. SQLite, PostgreSQL)

Pri každom spustení appky sa históriu načíta a pridá do messages.

Chceš, aby som ti napísala verziu kódu, kde má Mína pamäť uloženú v súbore (napr. memory.json), takže si bude pamätať aj po reštarte?






Tvoje slová:


ChatGPT povedal:
Vidím, že máš nastavené Environment Variables na Renderi (DATABASE_URL, OPENAI_API_KEY).

To znamená, že môžeš pridať trvalú pamäť cez databázu, napríklad PostgreSQL, ktorú Render poskytuje zadarmo v základnom pláne.

🔹 Ako spraviť, aby mala Mína trvalú pamäť
Použiješ DATABASE_URL na pripojenie k databáze (PostgreSQL).

Vytvoríš tabuľku napríklad takto:

sql
Kopírovať
Upraviť
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    role TEXT,
    content TEXT
);
V kóde namiesto st.session_state uložíš správy do databázy a pri spustení ich načítaš.

Chceš, aby som ti pripravila verziu mina.py, ktorá používa databázu Renderu na trvalú pamäť?
➡️ Takto by si mal históriu uloženú navždy, aj po reštarte aplikácie.






Tvoje slová:
Priprav mi to cele


ChatGPT povedal:
Dobre, pripravím ti celý nový kód mina.py, ktorý:
✅ používa PostgreSQL databázu Renderu na trvalú pamäť
✅ funguje s najnovším OpenAI API
✅ zobrazí históriu chatu vždy po načítaní stránky

📌 Postup pred použitím kódu
Uisti sa, že máš v Render Environment Variables:

OPENAI_API_KEY → tvoj API kľúč

DATABASE_URL → URL tvojej PostgreSQL databázy

V databáze spusti tento SQL príkaz (cez Render databázový panel → psql shell):

sql
Kopírovať
Upraviť
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    role TEXT,
    content TEXT
);
📌 Nový mina.py s trvalou pamäťou
python
Kopírovať
Upraviť
import streamlit as st
from openai import OpenAI
import psycopg2
import os

client = OpenAI()

# Pripojenie k databáze
def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

# Načítanie histórie z databázy
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

if st.button("Odoslať") and user_input.strip() != "":
    save_message("user", user_input)

    # Zavolanie OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "Si Mína, milá a priateľská AI, ktorá odpovedá úprimne a srdečne."}] +
                 load_messages()
    )

    assistant_reply = response.choices[0].message.content
    save_message("assistant", assistant_reply)

    st.rerun()