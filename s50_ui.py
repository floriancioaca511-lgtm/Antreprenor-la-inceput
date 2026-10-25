import streamlit as st

st.set_page_config(page_title="Antreprenor la inceput", page_icon="🚀", layout="wide")

pagina_fise = st.Page("s50_pages/fise.py", title="Fise", icon="📚", default=True)
pagina_adauga = st.Page("s50_pages/adauga.py", title="Adauga fisa", icon="➕")
pagina_cautare = st.Page("s50_pages/cautare.py", title="Cautare", icon="🔎")
pagina_asistent = st.Page("s50_pages/asistent.py", title="Asistent AI", icon="🤖")

navigare = st.navigation([pagina_fise, pagina_adauga, pagina_cautare, pagina_asistent])

navigare.run()
