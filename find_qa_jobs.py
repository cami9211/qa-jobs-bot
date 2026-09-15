```python
import os
import smtplib
import requests

from bs4 import BeautifulSoup
from datetime import date
from email.mime.text import MIMEText


EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_APP_PASSWORD = os.environ["EMAIL_APP_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_TO"]


BUSQUEDAS = [
    '"QA Engineer" senior remote Colombia',
    '"QA Engineer" semi senior remote Colombia',
    '"QA Analyst" senior remote Colombia',
    '"QA Analyst" semi senior remote Colombia',
    '"QA Tester" senior remote Colombia',
    '"QA Tester" semi senior remote Colombia',
]


def buscar_google(query):

    url = "https://www.google.com/search"

    params = {
        "q": query,
        "num": 10,
        "hl": "es",
        "gl": "co",
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    resultados = []

    for resultado in soup.select("div.MjjYud"):

        enlace = resultado.select_one("a")
        titulo = resultado.select_one("h3")

        if not enlace or not titulo:
            continue

        link = enlace.get("href")

        if not link or not link.startswith("http"):
            continue

        descripcion = resultado.select_one(".VwiC3b")

        resultados.append({
            "titulo": titulo.get_text(" ", strip=True),
            "link": link,
            "descripcion": (
                descripcion.get_text(" ", strip=True)
                if descripcion
                else ""
            )
        })

    return resultados


def main():

    resultados = []
    links = set()

    for busqueda in BUSQUEDAS:

        print(f"Buscando: {busqueda}")

        for resultado in buscar_google(busqueda):

            if resultado["link"] in links:
                continue

            links.add(resultado["link"])
            resultados.append(resultado)

    if not resultados:
        reporte = "Sin novedades hoy."

    else:

        reporte = []

        for i, resultado in enumerate(resultados, 1):

            reporte.append(
                f"{i}. {resultado['titulo']}\n"
                f"{resultado['descripcion']}\n"
                f"{resultado['link']}\n"
            )

        reporte = "\n".join(reporte)

    print(reporte)

    hoy = date.today().strftime("%d/%m/%Y")

    mensaje = MIMEText(
        reporte,
        "plain",
        "utf-8"
    )

    mensaje["Subject"] = f"Ofertas QA del {hoy}"
    mensaje["From"] = EMAIL_ADDRESS
    mensaje["To"] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:

        servidor.login(
            EMAIL_ADDRESS,
            EMAIL_APP_PASSWORD
        )

        servidor.sendmail(
            EMAIL_ADDRESS,
            EMAIL_TO,
            mensaje.as_string()
        )


if __name__ == "__main__":
    main()
```
