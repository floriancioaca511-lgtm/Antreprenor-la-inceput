from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

# Fisierul asta contine REGULILE pentru datele care vin din exterior:
# din formularele Streamlit (prin s50_app.py). Pydantic verifica fiecare
# camp; daca o regula nu e respectata, FastAPI raspunde singur cu 422.


# #############################################################
# PARTEA 1 - LECTIE  (plan: 2.1)
# #############################################################


# TODO 2.1a: clasa Categorie(str, Enum) - categoriile permise
#   Numele membrului nu poate avea spatii, dar valoarea poate:
#       FORME_JURIDICE = "Forme juridice"
#       TAXE           = "Taxe"
#       FACTURARE      = "Facturare"
#       CLIENTI        = "Clienti si contracte"
#       FREELANCING    = "Freelancing"
#       ALTELE         = "Altele"
class Categorie(str, Enum):
    FORME_JURIDICE = "Forme juridice"
    TAXE = "Taxe"
    FACTURARE = "Facturare"
    CLIENTI = "Clienti si contracte"
    FREELANCING = "Freelancing"
    ALTELE = "Altele"



# TODO 2.1b: clasa FisaIn(BaseModel) - o fisa NOUA (POST /fise)
#   Nu are id si nici data - le pun MySQL si s50_model.
#
#   camp        tip         regula (cu Field)
#   titlu       str         min_length=3, max_length=200
#   categorie   Categorie   (enum-ul de la 2.1a, fara Field)
#   continut    str         min_length=50
#
#   Exemple:
#     FisaIn(titlu="Concediul ca freelancer", categorie="Freelancing", continut="...50+ caractere...")
#         -> OK
#     FisaIn(titlu="Concediul ca freelancer", categorie="Vacante", continut="...")
#         -> ValidationError: "Vacante" nu e o categorie permisa
class FisaIn(BaseModel):
    titlu: str = Field(min_length=3, max_length=200)
    categorie: Categorie
    continut: str = Field(min_length=50)


# #############################################################
# PARTEA 2 - CHAT CU ASISTENTUL  (plan: 2.2)
# #############################################################
# Identic cu s49: serverul NU tine minte conversatia - Streamlit trimite
# de fiecare data tot istoricul.
#
#   cerere:   {"mesaj": "Ce aleg: PFA sau SRL?", "istoric": [...]}
#   raspuns:  {"raspuns": "Depinde de venituri, cheltuieli si risc...",
#              "apeluri": [{"tool": "cauta_in_fise",
#                           "rezultat": "[PFA sau SRL: ...]\n..."}]}


# TODO 2.2a: clasa MesajChat(BaseModel)
#   role      Literal["user", "assistant"]
#   content   str
class MesajChat(BaseModel):
    role: Literal["user", "assistant"]
    content: str


# TODO 2.2b: clasa ChatIn(BaseModel)
#   mesaj     str               Field(min_length=1)
#   istoric   list[MesajChat]   implicit lista goala: = []
class ChatIn(BaseModel):
    mesaj: str = Field(min_length=1)
    istoric: list[MesajChat] = []

# TODO 2.2c: clasa ApelTool(BaseModel) - UN tool apelat de agent
#   tool       str   - numele tool-ului, ex: "cauta_in_fise"
#   rezultat   str   - ce a gasit tool-ul (fisele = sursele raspunsului)
class ApelTool(BaseModel):
    tool: str
    rezultat: str


# TODO 2.2d: clasa ChatOut(BaseModel)
#   raspuns   str
#   apeluri   list[ApelTool]
class ChatOut(BaseModel):
    raspuns: str
    apeluri: list[ApelTool]