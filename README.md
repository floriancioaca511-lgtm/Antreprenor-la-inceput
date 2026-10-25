Antreprenor la început — Proiect Python, Sesiunea 50

1. Descrierea proiectului

„Antreprenor la început” este o aplicație educațională realizată în Python, destinată persoanelor care doresc să înceapă o activitate independentă sau o afacere.

Aplicația permite gestionarea unor fișe informative și utilizarea unui asistent AI care răspunde la întrebări folosind informațiile disponibile în baza de cunoștințe.

2. Tehnologii utilizate

Python — limbajul de programare

MySQL — stocarea fișelor

SQLAlchemy — comunicarea cu baza de date

FastAPI — interfața API

ChromaDB — indexarea vectorială și căutarea semantică

OpenAI — embeddings și generarea răspunsurilor AI

LangChain — implementarea agentului AI

Streamlit — interfața grafică

3. Funcționalitățile aplicației

Aplicația conține patru pagini:

Fișe — afișarea și ștergerea fișelor existente.

Adaugă fișă — introducerea de fișe noi.

Căutare — identificarea fișelor relevante prin căutare semantică RAG.

Asistent AI — conversație cu un agent AI care poate consulta fișele din baza de cunoștințe.

4. Structura proiectului

Antreprenor-la-inceput/
├── fise_initiale/
│   └── 8 fisiere .txt
├── s50_pages/
│   ├── fise.py
│   ├── adauga.py
│   ├── cautare.py
│   └── asistent.py
├── comun.py
├── document.md
├── s50_model.py
├── s50_schema.py
├── s50_rag.py
├── s50_agent.py
├── s50_app.py
├── s50_ui.py
├── requirements.txt
├── .gitignore
└── README.md

5. Instalarea bibliotecilor

Este necesar Python, un server MySQL și acces la API-ul OpenAI.

Din folderul proiectului:

python -m pip install -r requirements.txt

6. Configurarea bazei de date

Se creează în MySQL baza de date:

CREATE DATABASE IF NOT EXISTS project50;

Se configurează variabilele de mediu:

MYSQL_USER
MYSQL_PASSWORD
OPENAI_API_KEY

Valorile acestor variabile nu se introduc în cod și nu se publică pe GitHub.

7. Pornirea serverului FastAPI

Din folderul proiectului se execută:

python s50_app.py

Serverul rulează la:

http://127.0.0.1:8005

Documentația interactivă API este disponibilă la:

http://127.0.0.1:8005/docs

La prima pornire, aplicația inițializează structura bazei de date și încarcă fișele inițiale dacă tabela este goală. Fișele sunt apoi indexate în ChromaDB.

8. Pornirea interfeței Streamlit

Într-un al doilea proces, cu FastAPI pornit, se execută:

python -m streamlit run s50_ui.py

Aplicația poate fi accesată la:

http://localhost:8501

9. Arhitectura aplicației

Fluxul principal:

Streamlit → FastAPI → MySQL / ChromaDB → OpenAI

MySQL păstrează datele fișelor.

ChromaDB facilitează identificarea informațiilor relevante.

Agentul AI utilizează fișele ca surse de context pentru răspunsuri.

Streamlit afișează rezultatele într-o interfață accesibilă utilizatorului.

10. Observații

Aplicația are scop educațional.

Informațiile juridice și fiscale din fișe sunt orientative și trebuie verificate în raport cu legislația actuală.

Cha OpenAI și parola MySQL sunt configurate local prin variabile de mediu și nu sunt incluse în repository.ei

