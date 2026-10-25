# =============================================================
# PAGINA  -  Asistent AI  (ca Asistent AI de la s49)
# =============================================================
# Pagina trimite mesajul + istoricul la POST /chat, iar serverul ruleaza
# agentul. Sub fiecare raspuns aratam fisele gasite (sursele).
#
# Aceasta pagina este sistemul RAG COMPLET:
#   R - Retrieval   : tool-ul cauta_in_fise gaseste fisele
#   A - Augmented   : fisele gasite ajung la modelul de chat
#   G - Generation  : modelul scrie raspunsul pe baza lor
# =============================================================

import streamlit as st
from comun import api

st.title("🤖 Asistentul tau pentru afacerea proprie")
st.caption("Exemple: *Ce aleg la inceput: PFA sau SRL?* · "
           "*Cum calculez cat sa cer pe ora?* · *Ce trebuie sa contina contractul cu clientul?*")

with st.expander("ℹ️ Cum functioneaza pagina asta? (RAG complet)"):
    st.markdown(
        "Aceasta pagina este **sistemul RAG complet**. La fiecare intrebare:\n"
        "1. **R**etrieval - se cauta in fise, exact ca in pagina *Cautare*\n"
        "2. **A**ugmented - fisele gasite sunt date modelului de chat\n"
        "3. **G**eneration - modelul citeste fisele si scrie raspunsul\n\n"
        "Fisele folosite apar sub fiecare raspuns, la **📚 Surse**. Daca "
        "raspunsul contine ceva ce nu apare in surse, modelul a inventat.\n\n"
        "Asistentul explica notiuni - **nu** inlocuieste un contabil sau un avocat."
    )

if "messages" not in st.session_state:
    st.session_state.messages = []   # [{"role", "content", "apeluri"}]


def arata_apeluri(apeluri):
    if apeluri:
        with st.expander("📚 Surse - fisele gasite"):
            for a in apeluri:
                st.caption(a["rezultat"])


for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        arata_apeluri(m.get("apeluri"))


mesaj = st.chat_input("Intreaba-ma despre PFA, SRL, taxe, clienti...")

if mesaj:
    with st.chat_message("user"):
        st.markdown(mesaj)

    # TODO 1: istoricul pentru server - doar "role" si "content" din fiecare mesaj
    istoric = [
        {
            "role": m["role"],
            "content": m["content"]
        }
        for m in st.session_state.messages
    ]

    # TODO 2: salveaza in st.session_state.messages mesajul userului si raspunsul
    #   (raspunsul cu cheia "apeluri"), altfel conversatia se pierde la urmatorul mesaj
    st.session_state.messages.append({
        "role": "user",
        "content": mesaj
    })

    with st.chat_message("assistant"):
        ok, rezultat = api(
            "POST",
            "/chat",
            json={
                "mesaj": mesaj,
                "istoric": istoric
            },
            timeout=60
        )

        if ok:
            st.markdown(rezultat["raspuns"])
            arata_apeluri(rezultat["apeluri"])

            st.session_state.messages.append({
                "role": "assistant",
                "content": rezultat["raspuns"],
                "apeluri": rezultat["apeluri"]
            })
        else:
            st.error(rezultat)

    if st.session_state.messages and st.sidebar.button("Conversatie noua"):
        st.session_state.messages = []
        st.rerun()
