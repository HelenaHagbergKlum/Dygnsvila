# Kompensationsapp för dygnsvila (v5)

**Nyhet i v5:** Alla tidenheter mappas till ett dygn definierat som 07:00 → 07:00. 
Det gör att tider som **06:00–07:00** hör till slutet av dygnet och räknas korrekt på vardagar (20–07) samt i helgberäkningen.

- **Vardag:** all registrerad tid inom 20:00–07:00.
- **Helg:** brist mot 11h sammanhängande vila inom 07:00–07:00.
- Total kompenserad tid summeras med avdrag på 4h.

## Körning
```bash
streamlit run app.py
```
