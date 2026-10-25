# =============================================================
# PAGINA  -  Cautare (fara modelul de chat)
# =============================================================
# Aceasta pagina NU este RAG complet - este doar pasul R (Retrieval).
# RAG complet = pagina Asistent AI (Retrieval + Augmented + Generation).
#
# Se folosesc doar modelul de EMBEDDING (transforma intrebarea in numere
# care reprezinta sensul ei; nu scrie text) si CHROMA (compara numerele
# si intoarce fisele cele mai apropiate). Textul afisat este textul
# fisai, exact cum e salvat.
# =============================================================

import streamlit as st
from comun import api

st.title("🔎 Cautare in fise")
st.caption("Cautarea se face dupa SENS: incearca o intrebare care nu foloseste "
           "cuvintele din fise, ex: *ce trebuie sa scrie pe documentul prin care cer plata?*")

with st.expander("ℹ️ Cum functioneaza pagina asta? (fara modelul de chat)"):
    st.markdown(
        "Pe aceasta pagina **nu se foloseste modelul de chat**. Nimeni nu "
        "formuleaza un raspuns - vezi fisele **exact cum sunt salvate**.\n\n"
        "1. **Embedding** - un model OpenAI dedicat transforma intrebarea intr-o "
        "lista de numere care reprezinta **sensul** ei (nu scrie text).\n"
        "2. **Chroma** - compara aceste numere cu cele ale fiecarei fise.\n"
        "3. **Rezultat** - fisele cu sensul cel mai apropiat, ordonate dupa "
        "**distanta** (mai mica = mai potrivita).\n\n"
        "**Este asta RAG?** Doar **prima parte** din el:\n\n"
        "| Pas | Ce face | Cautare | Asistent AI |\n"
        "|---|---|---|---|\n"
        "| **R**etrieval | gaseste fisele relevante | ✅ | ✅ |\n"
        "| **A**ugmented | da fisele gasite modelului de chat | ❌ | ✅ |\n"
        "| **G**eneration | modelul scrie raspunsul pe baza lor | ❌ | ✅ |\n\n"
        "Sistemul RAG complet este pagina **Asistent AI**."
    )

intrebare = st.text_input("Intrebare")
n = st.slider("Cate fise", min_value=1, max_value=5, value=2)

if intrebare:
    ok, rezultate = api("GET", "/cauta", params={"intrebare": intrebare, "n": n}, timeout=30)
    if not ok:
        st.error(rezultate)
        st.stop()

    for r in rezultate:
        with st.container(border=True):
            # TODO: afiseaza titlul fisai si distanta, apoi textul fisai
            st.markdown(
                f"**{r['titlu']}** — distanta: {r['distanta']}"
            )
            st.markdown(r["text"])

    st.caption("Distanta mai MICA = fisa mai potrivita. Chroma intoarce mereu "
               "n fise, chiar daca niciuna nu e relevanta - compara distantele.")
