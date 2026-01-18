# 1. Wybieramy bazowy obraz Pythona (lekka wersja slim)
FROM python:3.11-slim

# 2. Ustawiamy folder roboczy wewnątrz kontenera
WORKDIR /app

# 3. Instalujemy absolutne minimum (tylko curl i kompilatory jeśli potrzebne)
# 3. Instalujemy biblioteki systemowe
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 4. Kopiujemy requirements (zauważ, że nie ma \ powyżej!)
COPY requirements.txt .

# 5. Instalujemy biblioteki Pythona
RUN pip install --no-cache-dir -r requirements.txt

# 6. Kopiujemy resztę plików projektu (app.py, foldery, itp.)
COPY . .

# 7. Informujemy, że aplikacja działa na porcie 8501
EXPOSE 8501

# 8. Komenda startowa dla Streamlit
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]