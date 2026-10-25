import streamlit as st
from comun import api

st.title("📚 Fise pentru antreprenori")

CATEGORII = ["Toate", "Forme juridice", "Taxe", "Facturare", "Clienti si contracte", "Freelancing", "Altele"]

categorie = st.sidebar.selectbox("Categorie", CATEGORII)

params = {}
if categorie != "Toate":
    params["categorie"] = categorie

ok, fise = api("GET", "/fise", params=params)
if not ok:
    st.error(fise)
    st.stop()

if not fise:
    st.info("Nicio fisa pentru categoria aleasa. Adauga una din 'Adauga fisa'.")
    st.stop()

st.caption(f"{len(fise)} fise")

for l in fise:
    with st.container(border=True):
        c_info, c_sterge = st.columns([6, 1])

        with c_info:
            st.markdown(f"**{l['titlu']}**")
            st.caption(f"{l['categorie']} · adaugata pe {l['data']} · {len(l['continut'])} caractere")
            with st.expander("Continut"):
                st.markdown(l["continut"])

        with c_sterge:
            if st.button("Sterge", key=f"sterge_{l['id']}"):
                ok, rezultat = api("DELETE", f"/fise/{l['id']}")
                if ok:
                    st.rerun()
                else:
                    st.error(rezultat)
