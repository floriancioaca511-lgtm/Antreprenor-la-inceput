import streamlit as st
from comun import api

st.title("➕ Adauga fisa")
st.caption("La salvare, fisa intra si in indexul RAG - asistentul o poate folosi imediat.")

with st.form("form_fisa_noua", clear_on_submit=True):
    c1, c2 = st.columns([3, 1])
    titlu = c1.text_input("Titlu", placeholder="ex: Concediul ca freelancer")
    categorie = c2.selectbox("Categorie", ["Forme juridice", "Taxe", "Facturare",
                                           "Clienti si contracte", "Freelancing", "Altele"])
    continut = st.text_area("Continut", height=300,
                            placeholder="Ca freelancer nu ai concediu platit, deci...")

    trimis = st.form_submit_button("Adauga", type="primary")

if trimis:
    # TODO: POST /fise cu cheile "titlu", "categorie", "continut" si timeout=30
    #   ok -> st.success cu titlul din rezultat; altfel -> st.error(rezultat)
    ok, rezultat = api(
        "POST","/fise",
        json={
            "titlu": titlu,
            "categorie": categorie,
            "continut": continut
        },
        timeout=30
    )
    if ok:
        st.success(f"Fisa '{rezultat['titlu']}' a fost adaugata.")
    else:
        st.error(rezultat)
