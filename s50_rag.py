# =============================================================
# RAG  -  indexul Chroma al fiselor  (ca s49_rag.py)
# =============================================================
# Acest modul implementeaza componenta de cautare din RAG, la fel ca in
# 48.1:
#   - add()   -> salveaza fisele in Chroma
#   - query() -> regaseste fisele cu sensul cel mai apropiat de o intrebare
#
# Fiecare fisa din MySQL devine un document in Chroma, cu acelasi id.
# MySQL ramane sursa de adevar; Chroma este doar un index, pastrat in
# memorie si reconstruit din MySQL la fiecare pornire.
#
# De ce este nevoie de Chroma, pe langa MySQL:
#   MySQL cauta dupa potrivire de text (WHERE titlu = ..., LIKE '%factura%').
#   Utilizatorii formuleaza insa intrebarile in propriii termeni - de
#   exemplu "ce trebuie sa scrie pe documentul prin care cer plata?", in
#   timp ce fisa relevanta vorbeste despre "facturare" si "e-Factura".
#   Chroma reprezinta fiecare text printr-un embedding (un vector numeric
#   care descrie sensul textului) si regaseste documentele cu sens
#   apropiat, chiar daca nu au cuvinte in comun cu intrebarea.
#
# Unde sunt folosite functiile din acest modul:
#   s50_app.py   -> la pornire:        indexeaza_toate(...)
#                -> POST /fise:         indexeaza_fisa(f)
#                -> DELETE /fise:       sterge_din_index(id)
#                -> GET /cauta:         cauta(intrebare, n)
#   s50_agent.py -> tool-ul cauta_in_fise apeleaza cauta(intrebare)
#                   pentru a furniza modelului contextul din care raspunde.
#
# Setup: pip install chromadb openai
#        export OPENAI_API_KEY="sk-..."   (cheia NU se scrie in cod)
# =============================================================

import os
import chromadb
from chromadb.utils import embedding_functions

# #############################################################
# PARTEA 0 - COLECTIA CHROMA  (gata scrisa)
# #############################################################
# O colectie Chroma este echivalentul unei tabele: contine toate fisele.
# functie_embedding transforma textul in vectori. Chroma o apeleaza
# automat, atat la adaugare (add), cat si la cautare (query), deci
# functiilor de mai jos le transmitem doar text.
#
# api_key_env_var = NUMELE variabilei de mediu din care se citeste cheia
# (nu cheia insasi!).
functie_embedding = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.environ["OPENAI_API_KEY"],
    model_name="text-embedding-3-small"
)

# chromadb.Client() pastreaza datele doar in memorie: la oprirea
# serverului indexul se pierde. Din acest motiv, s50_app.py il
# reconstruieste din MySQL la fiecare pornire.
client = chromadb.Client()
colectie = client.create_collection(
    name="s50_fise",
    embedding_function=functie_embedding,
)


# #############################################################
# PARTEA 1 - INDEXARE  (plan: 3.1)
# #############################################################
# Indexarea inseamna adaugarea unei fise in Chroma, astfel incat sa poata
# fi regasita la cautare. O fisa prezenta in MySQL, dar absenta din index,
# nu va fi niciodata folosita de asistentul AI.


# TODO 3.1a: indexeaza_fisa(fisa)
#
#   Scop: adauga o singura fisa in Chroma.
#
#   De ce este necesara: este operatia de baza pe care se sprijina restul
#   indexarii. Este folosita in doua locuri:
#     - indexeaza_toate(), pentru fiecare fisa, la pornirea aplicatiei;
#     - POST /fise din s50_app.py, imediat dupa salvarea fisei noi
#       in MySQL. Fara acest pas, fisa noua nu ar aparea in rezultatele
#       cautarii pana la urmatoarea repornire a serverului.
#
#   Parametri: fisa - obiect Fisa (din s50_model.py), cu .id, .titlu, .continut
#   Returneaza: nimic
#
#   Implementare: un singur apel colectie.add(...), cu trei liste de cate
#   un element:
#     ids        [str(fisa.id)]            id-ul din MySQL, convertit la str
#                                          (Chroma accepta doar id-uri text).
#                                          Pastrarea aceluiasi id permite
#                                          ulterior stergerea exacta a fisei.
#     documents  [fisa.continut]           textul pe baza caruia Chroma
#                                          calculeaza embedding-ul si in care
#                                          se face cautarea.
#     metadatas  [{"titlu": fisa.titlu}]   informatii asociate documentului,
#                                          care nu participa la cautare. Titlul
#                                          ne permite sa identificam sursa
#                                          fiecarui rezultat, pe care asistentul
#                                          o citeaza in raspuns.
#
#   Parametrii sunt liste deoarece add() poate primi mai multe documente
#   simultan; aici transmitem cate unul.
def indexeaza_fisa(fisa):
    colectie.add(ids=[str(fisa.id)], documents=[fisa.continut], metadatas=[{"titlu": fisa.titlu}] )


# TODO 3.1b: indexeaza_toate(fise)
#
#   Scop: adauga in Chroma toate fisele primite.
#
#   De ce este necesara: indexul este pastrat doar in memorie (vezi
#   PARTEA 0), deci la fiecare pornire colectia este goala. s50_app.py
#   citeste toate fisele din MySQL si le transmite acestei functii,
#   pentru ca indexul sa reflecte din nou continutul bazei de date.
#
#   Parametri: fise - lista de obiecte Fisa (rezultatul
#              s50_model.toate_fisele)
#   Returneaza: nimic
#
#   Implementare:
#     1. for fisa in fise:  indexeaza_fisa(fisa)
#        (reutilizam 3.1a, fara a duplica apelul colectie.add)
#     2. La final, afisati un mesaj de verificare:
#           print(f"Index RAG: {colectie.count()} fise.")
#        colectie.count() intoarce numarul de documente din Chroma si ar
#        trebui sa coincida cu numarul de fise din MySQL.
def indexeaza_toate(fise):
    for fisa in fise:
        indexeaza_fisa(fisa)

    print(f"Index RAG: {colectie.count()} fise.")


# TODO 3.1c: sterge_din_index(fisa_id)
#
#   Scop: elimina o fisa din Chroma, pe baza id-ului.
#
#   De ce este necesara: MySQL si Chroma trebuie sa ramana sincronizate.
#   Daca o fisa ar fi stearsa doar din MySQL, textul ei ar ramane in index,
#   iar asistentul AI ar putea in continuare sa formuleze raspunsuri pe baza
#   unei fise care nu mai exista. Functia este apelata de
#   DELETE /fise/{fisa_id} din s50_app.py, dupa stergerea din MySQL.
#
#   Parametri: fisa_id - int, id-ul fisei din MySQL
#   Returneaza: nimic
#
#   Implementare:
#       colectie.delete(ids=[str(fisa_id)])
#   Conversia la str este obligatorie: in 3.1a id-ul a fost salvat ca text,
#   iar un id numeric nu ar corespunde niciunui document.
def sterge_din_index(fisa_id):
    colectie.delete(ids=[str(fisa_id)])


# #############################################################
# PARTEA 2 - CAUTARE  (plan: 3.2)
# #############################################################
# Aceasta este etapa de Retrieval (regasire) din RAG: pentru o intrebare,
# identificam fisele relevante. Modelul AI le primeste apoi ca context
# si isi construieste raspunsul exclusiv pe baza lor (Augmented Generation).


# TODO 3.2: cauta(intrebare, n_rezultate=2)
#
#   Scop: regaseste cele mai relevante n_rezultate fise pentru intrebare,
#   pe baza similaritatii de sens.
#
#   De ce este necesara: este punctul comun prin care API-ul si agentul
#   acceseaza indexul:
#     - GET /cauta din s50_app.py o apeleaza direct (pagina "Cautare" din
#       UI afiseaza rezultatele fara model AI, util pentru verificarea
#       calitatii cautarii);
#     - tool-ul cauta_in_fise din s50_agent.py o foloseste pentru a
#       furniza asistentului textele pe care isi bazeaza raspunsul.
#   Ambii consumatori au nevoie de un format simplu, nu de structura
#   imbricata returnata de Chroma; de aceea rezultatul este convertit
#   intr-o lista de dictionare.
#
#   Parametri: intrebare (str), n_rezultate (int, implicit 2)
#   Returneaza: o lista de dictionare, ordonata de la cea mai relevanta fisa:
#       [{"titlu": "Facturarea si sistemul e-Factura", "text": "...", "distanta": 0.58}, ...]
#   O distanta mai mica indica o fisa mai relevanta.
#
#   Implementare:
#     1. rezultat = colectie.query(query_texts=[intrebare], n_results=n_rezultate)
#        Chroma calculeaza embedding-ul intrebarii si il compara cu cele
#        ale fiselor indexate.
#
#     2. rezultat este un dictionar ale carui valori sunt liste de liste -
#        cate o lista interioara pentru fiecare intrebare transmisa. Intrucat
#        transmitem o singura intrebare, folosim elementul [0]:
#           texte    = rezultat["documents"][0]    textele fiselor gasite
#           metadate = rezultat["metadatas"][0]    dictionarele {"titlu": ...}
#           distante = rezultat["distances"][0]    distanta fata de intrebare
#        Cele trei liste sunt aliniate: pozitia i din fiecare corespunde
#        aceleiasi fise.
#
#     3. lista = []
#        for i in range(len(texte)): adaugati in lista un dictionar cu
#          "titlu"    -> metadate[i]["titlu"]
#          "text"     -> texte[i]
#          "distanta" -> round(distante[i], 3)
#
#     4. return lista
#
#   Verificare (s50_plan.md, Pasul 3): pentru intrebarea "ce trebuie sa
#   scrie pe documentul prin care cer plata?", primul rezultat trebuie sa
#   fie "Facturarea si sistemul e-Factura".
def cauta(intrebare, n_rezultate=2):
    rezultat = colectie.query(query_texts=[intrebare], n_results=n_rezultate)
    texte = rezultat['documents'][0]
    metadatas = rezultat['metadatas'][0]
    distante = rezultat['distances'][0]

    lista = []
    for i in range(len(texte)):
        lista.append(
            {
                'titlu': metadatas[i]['titlu'],
                'text': texte[i],
                'distanta': round(distante[i],3)

             }
        )
    return lista

