# Proiectul 3 — Antreprenor la început (PFA, SRL, freelancing)

## Tema

Mulți programatori lucrează, la un moment dat, pe cont propriu: ca freelanceri
pentru clienți din țară sau din străinătate, sau ca contractori pe proiecte. La
început apar întrebări pe care niciun curs de programare nu le acoperă: PFA sau
SRL? Ce taxe plătesc și când? Trebuie să pun TVA pe factură? Ce scriu în
contract? Cât cer pe oră?

**Antreprenor la început** este o bibliotecă de fișe informative despre lucrul pe
cont propriu, cu un **asistent AI** care explică noțiunile și le aplică pe
situația utilizatorului — **doar pe baza fișelor**, cu sursa fiecărui răspuns.

## Cui se adresează

Persoanelor de 25–40 de ani care se gândesc să lucreze ca freelanceri sau să își
deschidă o mică afacere în IT și vor să înțeleagă opțiunile înainte să vorbească
cu un contabil.

## Ce face aplicația

1. **Păstrează fișele informative** într-o bază de date MySQL — fiecare fișă are
   titlu, categorie și conținut.
2. **Permite adăugarea și ștergerea fișelor** dintr-o interfață web. O fișă nouă
   devine imediat cautabilă.
3. **Caută după sens**: întrebarea „ce trebuie să scrie pe documentul prin care
   cer plata?” găsește fișa *Facturarea și sistemul e-Factura*, deși cuvântul
   „factură” lipsește.
4. **Explică și aplică**: asistentul AI caută fișele potrivite, le citește și
   explică opțiunile pe situația concretă a utilizatorului — și spune din ce fișă
   a luat informația.
5. **Are limite clare**: nu inventează cote de impozitare, plafoane sau termene
   care nu apar în fișe și nu înlocuiește un contabil sau un avocat.

## Paginile aplicației

| Pagină | Ce face | Ce parte din RAG |
|---|---|---|
| 📚 **Fișe** | lista fișelor, filtru pe categorie, conținutul fiecărei fișe, ștergere | — (date) |
| ➕ **Adaugă fișă** | formular: titlu, categorie, conținut; fișa e salvată și indexată | — (date) |
| 🔎 **Căutare** | caută fișele după sens și arată distanța; **fără** modelul de chat | doar **R** |
| 🤖 **Asistent AI** | chat cu asistentul; sub fiecare răspuns, sursele folosite | **R + A + G** (RAG complet) |

## Cum funcționează

```
              ┌──────── MySQL ────────┐
  Fișe ─────► │ tabela s50_fisa       │  ← sursa de adevăr
              └───────────────────────┘
                         │ la pornire + la fiecare adăugare/ștergere
                         ▼
              ┌──────── Chroma ───────┐
              │ aceleași fișe,        │  ← indexul pentru căutare după sens
              │ cu embedding-uri      │
              └───────────────────────┘
                         ▲
  Asistent AI ── /chat ── agent ── cauta_in_fise  →  modelul scrie răspunsul
  Căutare ────── /cauta ───────────┘                  (doar rezultatele căutării)
```

## Fișele inițiale

Aplicația pornește cu 8 fișe (folderul `fise_initiale/`):

| Fișă | Categorie |
|---|---|
| PFA sau SRL: ce formă juridică alegi | Forme juridice |
| PFA: sistem real, normă de venit și contribuțiile sociale | Taxe |
| SRL microîntreprindere: impozitul pe venit și dividendele | Taxe |
| TVA pentru freelanceri: plătitor sau neplătitor | Taxe |
| Facturarea și sistemul e-Factura | Facturare |
| Contractul de prestări servicii | Clienți și contracte |
| Lucrul cu clienți din străinătate | Clienți și contracte |
| Cum îți stabilești tariful ca freelancer | Freelancing |

Fișele explică **mecanismele** (cum funcționează un PFA, ce e taxarea inversă,
cum calculezi un tarif), nu cifrele fiscale ale unui an anume — acelea se schimbă
des prin lege.

## Exemple de întrebări

| Întrebare | Comportament așteptat |
|---|---|
| „Încep ca freelancer IT cu un singur client. Ce aleg: PFA sau SRL?” | criteriile din *PFA sau SRL*; recomandă un calcul cu un contabil |
| „Lucrez pentru o firmă din Germania. Pun TVA pe factură?” | explică înregistrarea pentru operațiuni intracomunitare și taxarea inversă; sursa *TVA pentru freelanceri* |
| „Vreau 120.000 de lei pe an. Cât cer pe oră?” | metoda din *Cum îți stabilești tariful* (ore facturabile, ~100 lei/oră) |
| „Clientul îmi tot cere lucruri în plus. Ce fac?” | scope creep și clauza din *Contractul de prestări servicii* |
| „Cât e exact cota de impozit pentru microîntreprinderi anul ăsta?” | **nu inventează** o cifră; spune că se schimbă și trimite la valorile în vigoare / contabil |

## Cerințe

**Obligatorii** (vezi `s50_plan.md`, pașii 1–7):
- [ ] baza de date cu fișele și funcțiile CRUD
- [ ] validarea datelor cu Pydantic (`FisaIn`)
- [ ] indexul Chroma: adăugare, ștergere, căutare
- [ ] asistentul AI cu tool-ul `cauta_in_fise`
- [ ] API-ul FastAPI: `/fise`, `/cauta`, `/chat`
- [ ] cele 4 pagini Streamlit
- [ ] testul final din plan trece

**Extinderi opționale** (după ce merg cerințele obligatorii):
- [ ] adăugați 2–3 fișe noi, scrise de voi (ex: *Concediul și boala ca freelancer*,
  *Cum găsești primii clienți*, *Fluxul de numerar: când intră și când ies banii*)
- [ ] o pagină „Calculator de tarif”: utilizatorul introduce venitul dorit, costurile
  și orele facturabile și vede tariful minim pe oră (fără AI, doar Python și Streamlit)
- [ ] un al doilea tool pentru agent, `calculeaza_tarif(venit_dorit, costuri, ore)`,
  care face calculul **în Python**
- [ ] în pagina Căutare, colorați distanța: verde sub un prag, roșu peste

## Atenție

Fișele au scop **exclusiv educativ** și nu reprezintă consultanță fiscală,
contabilă sau juridică. Legislația fiscală din România (cote, plafoane, termene,
condiții) se modifică frecvent. Înainte de orice decizie, verificați regulile în
vigoare și discutați cu un contabil autorizat sau cu un avocat.
