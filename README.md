# Kompensationsapp för dygnsvila

Detta är en Streamlit-app för att beräkna kompenserad vila för beredskapspersonal enligt 11-timmarsregeln. 
Dygnsbrytet är satt till 07:00.

## Funktioner
- Registrera ett valfritt antal dygn (vardag eller helg).
- Ange störningar med start- och sluttider (hanterar även pass som går över midnatt).
- Beräkna kompenserad tid per dygn och totalt.
- Automatisk justering med avdrag på 4 timmar.
- Exportera resultat till Excel.

## Installation

1. Klona repot eller ladda ner zip-filen och extrahera:
   ```bash
   git clone <din-github-url>
   cd kompensation_app
   ```

2. Skapa och aktivera ett virtuellt Python-miljö (rekommenderas):
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate    # Windows
   ```

3. Installera beroenden:
   ```bash
   pip install -r requirements.txt
   ```

## Kör lokalt

Starta appen med:
```bash
streamlit run app.py
```

Öppna sedan länken som visas i terminalen (vanligtvis `http://localhost:8501`).

## Deploy på Streamlit Cloud

1. Ladda upp projektet till ett publikt GitHub-repo.
2. Gå till [Streamlit Cloud](https://share.streamlit.io/).
3. Koppla ditt GitHub-konto och välj ditt repo.
4. Ange `app.py` som startfil och `requirements.txt` för beroenden.
5. Klicka **Deploy**.

## Exempel

- Dygn 1, helg: störning från 22:00 till 23:00 och från 04:00 till 05:00.  
- Appen räknar korrekt sammanhängande vila (22:00–04:00 = 6h, 05:00–07:00 = 2h, 07:00–22:00 = 15h).  
- Längsta vilan = 15h ⇒ kompensation = 0h (ingen brist).

---

Utvecklad för att förenkla beräkningen av kompensationstid för beredskapspersonal.
