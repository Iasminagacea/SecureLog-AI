# SecureLog AI – Analizator Inteligent de Securitate

**SecureLog AI** este o aplicație modernă de securitate cibernetică bazată pe Inteligență Artificială (RAG/Prompt Engineering), construită cu **Python (Flask)** și **MongoDB**, capabilă să analizeze fișiere de log-uri pentru a detecta suspiciuni de atacuri cibernetice (ex. Brute Force, SQL Injection, XSS) și să ofere rapoarte structurate cu nivel de risc și pași de rezolvare.

---

## 🚀 Pornire Rapidă (Docker Compose)

Cea mai simplă metodă de a rula aplicația este utilizând **Docker Compose**. Tot ce trebuie să faci este:

### 1. Clonarea proiectului și configurarea variabilelor de mediu
Creează un fișier `.env` în rădăcina proiectului (copiind conținutul din `.env.example`) și adaugă cheia ta API Gemini obținută gratuit din [Google AI Studio](https://aistudio.google.com/):

```bash
cp .env.example .env
```

Editează `.env` și adaugă cheia:
```env
GEMINI_API_KEY=cheia_ta_gemini_aici
```

### 2. Lansarea aplicației
Rulează următoarea comandă în terminal:

```bash
docker-compose up --build
```

Această comandă va descărca și va configura automat:
* **Containerul Web (Python/Flask)** pe portul `5000`
* **Containerul Database (MongoDB)** pe portul `27017`

---

## 🛠️ API Endpoints & Testare

Poți testa aplicația folosind utilitare precum **Postman** sau comenzi simple **cURL** în terminal.

### 1. Verificare Status (Health Check)
Verifică dacă Flask este conectat cu succes la MongoDB și dacă API Key-ul Gemini este configurat:

* **Endpoint:** `GET http://localhost:5000/health`
* **Comandă cURL:**
```bash
curl http://localhost:5000/health
```

### 2. Analiză Log-uri (Upload de fișier)
Poți trimite un fișier text ce conține log-uri (de exemplu, [sample_logs.json](sample_logs.json)):

* **Endpoint:** `POST http://localhost:5000/analyze`
* **Comandă cURL:**
```bash
curl -X POST -F "file=@sample_logs.json" http://localhost:5000/analyze
```

### 3. Analiză Log-uri (Body JSON direct)
Poți trimite log-urile direct în corpul cererii (request body):

* **Endpoint:** `POST http://localhost:5000/analyze`
* **Comandă cURL:**
```bash
curl -X POST -H "Content-Type: application/json" -d '[{"timestamp":"2026-06-22","ip_address":"192.168.1.50","message":"Failed login attempt"}]' http://localhost:5000/analyze
```

#### Exemplu de răspuns (JSON generat de AI):
```json
{
  "risk_level": "High",
  "detalii_atac": "Au fost detectate 4 tentative eșuate de autentificare consecutive pentru utilizatorul admin de la aceeași adresă IP (Brute Force), urmate de o tentativă de SQL Injection la path-ul /products.",
  "pasi_rezolvare": [
    "Blocarea temporară sau permanentă a IP-ului 192.168.1.50 la nivel de firewall.",
    "Implementarea unui mecanism de rate-limiting pe endpoint-ul /login.",
    "Validarea și igienizarea parametrilor de intrare pe endpoint-ul /products pentru a preveni SQL Injection."
  ],
  "report_id": "649495..."
}
```

### 4. Vizualizare Rapoarte Salvate
Aplicația salvează fiecare raport generat de AI în baza de date MongoDB. Poți vedea ultimele 20 de analize:

* **Endpoint:** `GET http://localhost:5000/reports`
* **Comandă cURL:**
```bash
curl http://localhost:5000/reports
```

---

## 📦 Rulare Locală (fără Docker)

Dacă dorești să dezvolți sau să rulezi aplicația direct pe calculatorul tău (necesită Python 3.10+ și o instanță locală de MongoDB activă):

1. Instalează dependențele:
   ```bash
   pip install -r requirements.txt
   ```
2. Modifică în fișierul `.env`:
   `MONGO_URI=mongodb://localhost:27017/`
3. Rulează aplicația:
   ```bash
   python app.py
   ```
