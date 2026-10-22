# =============================================================
# AGENTUL  -  Asistentul pentru antreprenori  (LangChain + RAG)
# =============================================================
# Acelasi agent ca la s49: un singur tool, care cauta in fisele de
# pentru antreprenori (prin s50_rag.py), iar modelul raspunde pe baza lor.
#
# Fisierul nu stie nimic de FastAPI sau Streamlit. Il poti testa singur:
#   python3 s50_agent.py
#
# Setup: pip install langchain langchain-openai
#        export OPENAI_API_KEY="sk-..."   (cheia NU se scrie in cod)
# =============================================================

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

import s50_model
import s50_rag


# #############################################################
# PARTEA 1 - TOOL-UL DE CAUTARE  (plan: 4.1)
# #############################################################


# TODO 4.1: tool-ul cauta_in_fise(intrebare: str) -> str
#   La fel ca cauta_in_notite de la s49.
#
#   1. rezultate = s50_rag.cauta(intrebare)
#   2. Pentru fiecare rezultat r, o bucata de text:
#          f"[{r['titlu']}]\n{r['text']}"
#      Bucatile le pui intr-o lista.
#   3. return bucatile unite cu "\n\n".join(...)
@tool
def cauta_in_fise(intrebare: str) -> str:
    """Cauta in fisele pentru antreprenori fisele relevante pentru
    intrebare. Foloseste-l pentru ORICE intrebare despre lucrul pe cont
    propriu: PFA, SRL, microintreprindere, taxe si contributii, TVA,
    facturare, e-Factura, contracte, clienti din strainatate, tarife."""
    rezultate = s50_rag.cauta(intrebare)
    bucati = []
    for r in rezultate:
        bucati.append(f"[{r['titlu']}]\n{r['text']}")
    return "\n\n".join(bucati)


# #############################################################
# PARTEA 2 - AGENTUL  (gata scris)
# #############################################################
# Pe langa regulile RAG (raspunde DOAR din fise, spune sursa, nu
# inventa), asistentul are si LIMITE, ca la s45: explica notiuni, dar nu
# da consultanta fiscala sau juridica personalizata si nu inventeaza cifre.
SYSTEM_PROMPT = (
    "Esti un asistent pentru persoanele care incep sa lucreze pe cont propriu "
    "(PFA, SRL, freelancing). Pentru orice intrebare folosesti tool-ul "
    "cauta_in_fise si raspunzi DOAR pe baza fiselor gasite. Explici clar, cu "
    "exemple simple, si aplici ideile pe situatia utilizatorului. La final spui "
    "din ce fise ai luat informatia (titlurile dintre parantezele drepte). Daca "
    "fisele nu acopera subiectul, spui clar asta - nu inventa. NU dai cote de "
    "impozitare, plafoane sau termene exacte daca nu apar in fise: regulile "
    "fiscale se schimba des, iar pentru decizii personale recomanzi un contabil "
    "sau un avocat. Raspunzi scurt, in romana."
)

llm = ChatOpenAI(model="gpt-4.1-mini")

agent = create_agent(
    llm,
    tools=[cauta_in_fise],
    system_prompt=SYSTEM_PROMPT,
)


# #############################################################
# PARTEA 3 - ruleaza_agent  (plan: 4.2)
# #############################################################


# TODO 4.2: ruleaza_agent(mesaj, istoric)
#   1. messages = istoric + [{"role": "user", "content": mesaj}]
#   2. rezultat = agent.invoke({"messages": messages})
#   3. apeluri = []; pentru fiecare mesaj m din rezultat["messages"] de tip
#      "ToolMessage" (type(m).__name__), adaugi {"tool": m.name, "rezultat": m.content}
#   4. raspuns = rezultat["messages"][-1].content
#   5. return raspuns, apeluri
def ruleaza_agent(mesaj: str, istoric: list[dict]):
    messages = istoric + [{"role": "user", "content": mesaj}]
    rezultat = agent.invoke({"messages": messages})
    apeluri = []
    for m in rezultat["messages"]:
        if type(m).__name__ == "ToolMessage":
            apeluri.append({"tool": m.name, "rezultat": m.content})
    raspuns = rezultat["messages"][-1].content
    return raspuns, apeluri