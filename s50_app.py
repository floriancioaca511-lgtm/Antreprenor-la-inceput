from fastapi import Depends, FastAPI, HTTPException

import s50_model
import s50_rag
from s50_model import get_db, init_db
from s50_schema import Categorie, FisaIn, ChatIn, ChatOut
from s50_agent import ruleaza_agent


# La pornire: tabela + fisele initiale in MySQL, apoi indexul RAG
# umplut cu TOATE fisele din MySQL (vezi s50_rag.py).
init_db()
with s50_model.SessionLocal() as s:
    s50_rag.indexeaza_toate(s50_model.toate_fisele(s))

app = FastAPI(title="Antreprenor la inceput", version="1.0.0 (s50, RAG)")


def fisa_dict(l):
    return {"id": l.id, "titlu": l.titlu, "categorie": l.categorie,
            "continut": l.continut, "data": l.data.isoformat()}


# #############################################################
# PARTEA 1 - LECTII  (plan: 5.1)
# #############################################################
# Regula proiectului: orice modificare in MySQL se face si in Chroma.


# TODO 5.1a: GET /fise?categorie= - lista fiselor
#   1. categorie_text = None; daca categorie nu e None -> categorie.value
#   2. return o LISTA DE DICTIONARE: fisa_dict(l) pentru fiecare fisa din
#      s50_model.toate_fisele(db, categorie_text)
@app.get("/fise")
def lista_fise(categorie: Categorie | None = None, db=Depends(get_db)):
    categorie_text = None

    if categorie is not None:
        categorie_text = categorie.value

    return [
        fisa_dict(l)
        for l in s50_model.toate_fisele(db, categorie_text)
    ]


# TODO 5.1b: POST /fise - adauga o fisa
#   1. Titlu duplicat? s50_model.gaseste_fisa_dupa_titlu(db, data.titlu)
#      gaseste ceva -> HTTPException(400, "fisa '...' exista deja")
#   2. l = s50_model.adauga_fisa(db, data.titlu, data.categorie.value, data.continut)
#   3. s50_rag.indexeaza_fisa(l)   <- fisa devine cautabila
#   4. return fisa_dict(l)
@app.post("/fise", status_code=201)
def adauga_fisa(data: FisaIn, db=Depends(get_db)):
    existenta = s50_model.gaseste_fisa_dupa_titlu(db, data.titlu)

    if existenta is not None:
        raise HTTPException(
            status_code=400,
            detail=f"fisa '{data.titlu}' exista deja"
        )

    l = s50_model.adauga_fisa(
        db,
        data.titlu,
        data.categorie.value,
        data.continut
    )

    s50_rag.indexeaza_fisa(l)

    return fisa_dict(l)


# TODO 5.1c: DELETE /fise/{fisa_id} - sterge o fisa
#   1. s50_model.sterge_fisa(db, fisa_id) -> False -> HTTPException(404, ...)
#   2. s50_rag.sterge_din_index(fisa_id)   <- dispare si din cautare
#   3. return {"sters": fisa_id}
@app.delete("/fise/{fisa_id}")
def sterge_fisa(fisa_id: int, db=Depends(get_db)):
    rezultat = s50_model.sterge_fisa(db, fisa_id)

    if not rezultat:
        raise HTTPException(
            status_code=404,
            detail=f"Fisa cu ID-ul {fisa_id} nu exista"
        )

    s50_rag.sterge_din_index(fisa_id)

    return {"sters": fisa_id}


# #############################################################
# PARTEA 2 - CAUTARE  (plan: 5.2)
# #############################################################


# TODO 5.2: GET /cauta?intrebare=...&n=2 - doar cautarea, FARA model
#   1. Daca n < 1 sau n > 5 -> HTTPException(400, "n trebuie sa fie intre 1 si 5")
#   2. return s50_rag.cauta(intrebare, n)
@app.get("/cauta")
def cauta(intrebare: str, n: int = 2):
    if n < 1 or n > 5:
        raise HTTPException(
            status_code=400,
            detail="n trebuie sa fie intre 1 si 5"
        )

    return s50_rag.cauta(intrebare, n)


# #############################################################
# PARTEA 3 - /chat: ASISTENTUL  (plan: 5.3 - dupa Pasul 4)
# #############################################################


# TODO 5.3: POST /chat - ca la s49
#   1. istoric = lista cu m.model_dump() pentru fiecare m din data.istoric
#   2. try: raspuns, apeluri = ruleaza_agent(data.mesaj, istoric)
#      except Exception as e: HTTPException(502, f"Eroare la modelul AI: {e}")
#   3. return ChatOut(raspuns=raspuns, apeluri=apeluri)
@app.post("/chat", response_model=ChatOut)
def chat(data: ChatIn):
    istoric = [m.model_dump() for m in data.istoric]

    try:
        raspuns, apeluri = ruleaza_agent(data.mesaj, istoric)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Eroare la modelul AI: {e}"
        )

    return ChatOut(
        raspuns=raspuns,
        apeluri=apeluri
    )


import uvicorn
uvicorn.run(app, host="127.0.0.1", port=8005)
