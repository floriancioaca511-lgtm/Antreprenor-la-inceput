# Proiectul 3 — Antreprenor la început (plan de lucru)

Ce face aplicația și de ce: vezi **`document.md`**. Aici sunt pașii de implementare.

Structura este **identică cu proiectul de la sesiunea 49** (Asistentul cursului):
se schimbă doar tema — *notițe* devin *fișe*, *capitol* devine *categorie*.
Dacă vă blocați, comparați cu fișierul corespunzător din `session49/proiect/`.

| s49 — Asistentul cursului | s50 — Antreprenor la început |
|---|---|
| tabela `s49_notita` | tabela `s50_fisa` |
| `capitol` | `categorie` |
| tool-ul `cauta_in_notite` | tool-ul `cauta_in_fise` |
| pagina Asistent AI | pagina Asistent AI |

## Cum lucrați

- În fiecare fișier găsiți comentarii `# TODO`. Numărul lor (ex: `TODO 3.1a`)
  este același cu cel din acest plan — citiți TODO-ul din cod, apoi scrieți
  funcția sub el.
- Ce **nu** are TODO este deja scris: citiți-l, îl folosiți mai departe.
- În paginile Streamlit, sub TODO-uri există linii marcate `# TEMPORAR`, ca
  pagina să pornească și înainte să scrieți soluția.

## Ordinea de lucru

```
s50_model.py   ← baza de date (tabela Fisa + funcțiile CRUD)
     ↓
s50_schema.py  ← validarea datelor
     ↓
s50_rag.py     ← Chroma: add + query + delete
     ↓
s50_agent.py   ← asistentul AI
     ↓
s50_app.py     ← rutele HTTP
     ↓
s50_ui.py + comun.py   ← scheletul interfeței (gata scrise)
     ↓
s50_pages/*.py ← paginile
```

## Setup (o singură dată)

```
pip install sqlalchemy pymysql fastapi uvicorn streamlit requests chromadb langchain langchain-openai
export OPENAI_API_KEY="sk-..."        # Windows: setx OPENAI_API_KEY "sk-..."
```

Cheia **nu** se scrie în cod. Toate comenzile se rulează din folderul proiectului.

---

## Pasul 1 — `s50_model.py` (baza de date)

**Gata scris:** conexiunea (schimbați userul și parola MySQL), `reset_db`,
`adauga_date_initiale` (citește cele 8 fișiere din `fise_initiale/` — prima
linie e titlul), `init_db`, `get_db`.

- [ ] **TODO 1.2** `Fisa` → tabela `s50_fisa`: `id`, `titlu` (**unique**),
  `categorie`, `continut` (**`Text`**), `data`; plus `__str__`
- [ ] **TODO 1.4a** `adauga_fisa(s, titlu, categorie, continut)`
- [ ] **TODO 1.4b** `toate_fisele(s, categorie=None)` → ordonate după titlu
- [ ] **TODO 1.4c** `gaseste_fisa_dupa_titlu(s, titlu)` → fișa sau `None`
- [ ] **TODO 1.4d** `sterge_fisa(s, id)` → `True` / `False`

**Test:**
```python
import s50_model
s50_model.init_db()
with s50_model.SessionLocal() as s:
    for l in s50_model.toate_fisele(s):
        print(l)
```
Apar cele 8 fișe inițiale.

---

## Pasul 2 — `s50_schema.py` (validarea datelor)

- [ ] **TODO 2.1a** `Categorie(str, Enum)`: `Forme juridice`, `Taxe`, `Facturare`,
  `Clienti si contracte`, `Freelancing`, `Altele`
- [ ] **TODO 2.1b** `FisaIn`: `titlu` 3–200 caractere, `categorie`, `continut` minim 50 caractere
- [ ] **TODO 2.2a–d** `MesajChat`, `ChatIn`, `ApelTool` (`tool` + `rezultat`), `ChatOut`

**Test:**
```python
from s50_schema import FisaIn
FisaIn(titlu="Test", categorie="Taxe", continut="prea scurt")   # ValidationError
```

---

## Pasul 3 — `s50_rag.py` (Chroma)

**Gata scris:** colecția Chroma.

- [ ] **TODO 3.1a** `indexeaza_fisa(fisa)` →
  `colectie.add(ids=[str(fisa.id)], documents=[fisa.continut], metadatas=[{"titlu": fisa.titlu}])`
- [ ] **TODO 3.1b** `indexeaza_toate(fise)` → un `for` cu `indexeaza_fisa`
- [ ] **TODO 3.1c** `sterge_din_index(fisa_id)` → `colectie.delete(ids=[str(fisa_id)])`
- [ ] **TODO 3.2** `cauta(intrebare, n_rezultate=2)` → listă `{"titlu", "text", "distanta"}`

**Test:**
```python
import s50_model, s50_rag
with s50_model.SessionLocal() as s:
    s50_rag.indexeaza_toate(s50_model.toate_fisele(s))
for r in s50_rag.cauta("ce trebuie sa scrie pe documentul prin care cer plata?"):
    print(r["distanta"], r["titlu"])
```
Primul rezultat: **Facturarea și sistemul e-Factura**.

---

## Pasul 4 — `s50_agent.py` (asistentul AI)

**Gata scris:** `SYSTEM_PROMPT` (rolul asistentului și **limitele** lui — nu inventează
cote, plafoane sau termene și nu înlocuiește un contabil), `llm`, `agent`, testul.

- [ ] **TODO 4.1** tool-ul `cauta_in_fise(intrebare)` → fișele găsite, fiecare cu
  titlul în față: `[PFA sau SRL: ce forma juridica alegi]` + textul
- [ ] **TODO 4.2** `ruleaza_agent(mesaj, istoric)` → `(raspuns, apeluri)`

**Test:** `python3 s50_agent.py` — două întrebări din fișe și una la care
asistentul nu trebuie să inventeze o cifră („cât e exact cota de impozit pentru
microîntreprinderi anul ăsta?”).

---

## Pasul 5 — `s50_app.py` (API-ul FastAPI)

**Gata scris:** importurile, pornirea (`init_db` + `indexeaza_toate`), `fisa_dict`,
`uvicorn.run(...)` pe portul **8005**.

- [ ] **TODO 5.1a** `GET /fise?categorie=`
- [ ] **TODO 5.1b** `POST /fise` (201) — titlu duplicat → `400`; apoi **`indexeaza_fisa`**
- [ ] **TODO 5.1c** `DELETE /fise/{id}` — `404`; apoi **`sterge_din_index`**
- [ ] **TODO 5.2** `GET /cauta?intrebare=&n=2` — `n` în afara 1–5 → `400`
- [ ] **TODO 5.3** `POST /chat` — eroare de la OpenAI → `502`

**Test:** `python3 s50_app.py` → http://127.0.0.1:8005/docs

---

## Pasul 6 — `comun.py` + `s50_ui.py` (gata scrise)

`api(metoda, cale, ...)` întoarce `(ok, rezultat)`; `s50_ui.py` face meniul cu
cele 4 pagini. `API_URL` din `comun.py` trebuie să aibă **același port** ca
`uvicorn.run(...)` din `s50_app.py`.

**Test:** API pornit + `streamlit run s50_ui.py`.

---

## Pasul 7 — `s50_pages/` (paginile)

- [ ] **`fise.py`** — TODO 1: filtrul de categorie; TODO 2: butonul Șterge
- [ ] **`adauga.py`** — TODO: `POST /fise` cu `timeout=30`
- [ ] **`cautare.py`** — TODO: afișarea fiecărei fișe găsite (titlu, distanță, text)
- [ ] **`asistent.py`** — TODO 1: istoricul; TODO 2: salvarea mesajelor în `st.session_state`

---

## Test final end-to-end

MySQL pornit → `export OPENAI_API_KEY=...` → `python3 s50_app.py` →
`streamlit run s50_ui.py`:

1. **Căutare:** „ce trebuie să scrie pe documentul prin care cer plata?” → primul
   rezultat: *Facturarea și sistemul e-Factura*
2. **Asistent AI:** „vreau 120.000 de lei pe an, cât cer pe oră?” → metoda orelor
   facturabile + sursa *Cum îți stabilești tariful*
3. **Adaugă fișă:** „Concediul ca freelancer” → **Asistent AI:** „cum îmi plănuiesc
   concediul dacă lucrez pe cont propriu?” → răspunsul vine din fișa nouă
4. **Fișe:** șterge „Concediul ca freelancer” → aceeași întrebare: asistentul spune că
   nu are informația
5. **Asistent AI:** „cât e exact cota de impozit pentru micro anul ăsta?” → nu inventează
