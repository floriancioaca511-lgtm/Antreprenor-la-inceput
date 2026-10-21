
import os
from datetime import date

from sqlalchemy import create_engine, String, Text, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


# #############################################################
# PARTEA 0 - CONEXIUNEA LA MySQL  (plan: 1.1)
# #############################################################
# Aceeasi conexiune ca la s49. Schimbati userul si parola cu ale voastre.

user = os.environ["MYSQL_USER"]
password = os.environ["MYSQL_PASSWORD"]
engine = create_engine(f"mysql+pymysql://{user}:{password}@localhost:3306/project50")
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


# #############################################################
# PARTEA 1 - MODELUL: Fisa  (plan: 1.2)
# #############################################################
# O singura tabela: fisele informative pentru antreprenori. MySQL este SURSA DE
# ADEVAR - aici stau fisele, intregi. Chroma (s50_rag.py) este doar un
# INDEX pentru cautarea dupa sens si se umple din MySQL la fiecare pornire.


# TODO 1.2: clasa Fisa (mosteneste Base)
#   O fisa = un subiect pentru cei care lucreaza pe cont propriu, ex: "PFA sau SRL".
#
#   1. __tablename__ = "s50_fisa"
#   2. coloanele:
#        id         int    cheie primara, autoincrement=True
#        titlu      str    String(200), unique=True
#        categorie  str    String(30)   ex: "Taxe", "Facturare"
#        continut   str    mapped_column(Text)  - o fisa are mii de caractere
#        data       date   (fara mapped_column - ajunge Mapped[date])
#   3. metoda __str__(self) - textul afisat cand faci print(fisa):
#          Fisa #5: PFA sau SRL: ce forma juridica alegi (Forme juridice, 2010 caractere)
class Fisa(Base):
    __tablename__ = "s50_fisa"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    titlu: Mapped[str] = mapped_column(String(200), unique=True)
    categorie: Mapped[str] = mapped_column(String(30))
    continut: Mapped[str] = mapped_column(Text)
    data: Mapped[date]

    def __str__(self):
        return f'Fisa #{self.id}: {self.titlu} ({self.categorie}, {len(self.continut)} caractere)'



# #############################################################
# PARTEA 1b - PORNIREA BAZEI DE DATE  (plan: 1.3)
# #############################################################


def reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


# Fisele initiale sunt fisierele din folderul fise_initiale/.
# Prima linie a fiecarui fisier este titlul; restul este continutul.
FOLDER_FISE_INITIALE = "fise_initiale"

CATEGORIE_PE_FISIER = {
    "pfa_sau_srl.txt":             "Forme juridice",
    "pfa_impozitare.txt":          "Taxe",
    "srl_microintreprindere.txt":  "Taxe",
    "tva_freelanceri.txt":         "Taxe",
    "facturare.txt":               "Facturare",
    "contract_servicii.txt":       "Clienti si contracte",
    "clienti_din_strainatate.txt": "Clienti si contracte",
    "tarif_freelancer.txt":        "Freelancing",
}


def adauga_date_initiale(s):
    if s.scalars(select(Fisa)).all():
        return

    for nume_fisier in sorted(os.listdir(FOLDER_FISE_INITIALE)):
        cale = os.path.join(FOLDER_FISE_INITIALE, nume_fisier)
        with open(cale, encoding="utf-8") as f:
            text = f.read()

        prima_linie, rest = text.split("\n", 1)
        categorie = CATEGORIE_PE_FISIER.get(nume_fisier, "Altele")
        s.add(Fisa(titlu=prima_linie.strip(), categorie=categorie,
                     continut=rest.strip(), data=date.today()))
    s.commit()


def init_db():
    Base.metadata.create_all(engine)
    with SessionLocal() as s:
        adauga_date_initiale(s)


# #############################################################
# PARTEA 2 - CRUD Fisa  (plan: 1.4)
# #############################################################


# TODO 1.4a: adauga_fisa(s, titlu, categorie, continut)
#   1. l = Fisa(titlu=..., categorie=..., continut=..., data=date.today())
#   2. s.add(l), s.commit()
#   3. return l      -> obiectul, acum cu id
def adauga_fisa(s, titlu, categorie, continut):
    l = Fisa(titlu=titlu, categorie=categorie, continut=continut, data=date.today())
    s.add(l)
    s.commit()
    return l


# TODO 1.4b: toate_fisele(s, categorie=None)
#   Intoarce LISTA fiselor, ordonate alfabetic dupa titlu.
#   Filtrul categorie e optional: daca e None, nu se aplica.
#
#   1. query = select(Fisa)
#   2. if categorie: query = query.where(Fisa.categorie == categorie)
#   3. query = query.order_by(Fisa.titlu)
#   4. return s.scalars(query).all()
def toate_fisele(s, categorie=None):
    query = select(Fisa)
    if categorie:
        query = query.where(Fisa.categorie == categorie)
    query = query.order_by(Fisa.titlu)
    return s.scalars(query).all()


# TODO 1.4c: gaseste_fisa_dupa_titlu(s, titlu)
#   Intoarce fisa cu titlul dat, sau None.
#   Ruta POST /fise o foloseste ca sa verifice titlul duplicat INAINTE
#   de salvare (coloana titlu e unique).
#   return s.scalar(select(Fisa).where(Fisa.titlu == titlu))
def gaseste_fisa_dupa_titlu(s, titlu):
    return s.scalar(select(Fisa).where(Fisa.titlu == titlu))

# TODO 1.4d: sterge_fisa(s, fisa_id)
#   Intoarce True daca a sters fisa, False daca nu exista.
#   1. l = s.get(Fisa, fisa_id)
#   2. daca l este None -> return False
#   3. altfel: s.delete(l), s.commit(), return True
def sterge_fisa(s, fisa_id):
    l = s.get(Fisa, fisa_id)
    if l is None:
        return False
    s.delete(l)
    s.commit()
    return True


# #############################################################
# PARTEA 3 - get_db()
# #############################################################


def get_db():
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()
