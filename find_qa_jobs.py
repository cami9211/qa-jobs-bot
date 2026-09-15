import os
import smtplib
import requests

from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# ============================================================
# CONFIGURACIÓN
# ============================================================

URL_MAGNETO = "https://www.magneto365.com/co"

URL_BUSQUEDA = (
    "https://www.magneto365.com/co/"
    "trabajos/ofertas-empleo-de-analista-prueba-software"
)

EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_APP_PASSWORD = os.environ["EMAIL_APP_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_TO"]


# ============================================================
# CONEXIÓN
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-CO,es;q=0.9",
}


def obtener_pagina(url):
    print(f"Consultando:")
    print(url)
    print()

    respuesta = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
    )

    respuesta.raise_for_status()

    print(f"HTTP: {respuesta.status_code}")
    print(f"Tamaño: {len(respuesta.text)} bytes")
    print()

    return BeautifulSoup(
        respuesta.text,
        "html.parser",
    )


# ============================================================
# BUSCAR ENLACES DE OFERTAS
# ============================================================

def buscar_ofertas():

    soup = obtener_pagina(URL_BUSQUEDA)

    resultados = []
    enlaces_vistos = set()

    for enlace in soup.find_all("a", href=True):

        href = enlace["href"].strip()

        titulo = enlace.get_text(
            " ",
            strip=True,
        )

        if not href:
            continue

        if not titulo:
            continue

        url = urljoin(
            URL_MAGNETO,
            href,
        )

        # Solamente enlaces de ofertas individuales.
        if "/co/empleos/" not in url:
            continue

        if url in enlaces_vistos:
            continue

        enlaces_vistos.add(url)

        resultados.append({
            "titulo": titulo,
            "url": url,
        })

    return resultados


# ============================================================
# FILTRO QA
# ============================================================

def filtrar_qa(resultados):

    palabras = [
        "qa",
        "tester",
        "testing",
        "quality assurance",
        "analista de pruebas",
        "ingeniero de pruebas",
        "automatización de pruebas",
        "automatizacion de pruebas",
        "pruebas de software",
    ]

    ofertas_qa = []

    for oferta in resultados:

        titulo = oferta["titulo"].lower()

        if any(
            palabra in titulo
            for palabra in palabras
        ):
            ofertas_qa.append(oferta)

    return ofertas_qa


# ============================================================
# REPORTE
# ============================================================

def generar_reporte(ofertas):

    if not ofertas:

        return (
            "OFERTAS QA - MAGNETO365\n"
            "=======================\n\n"
            "No se encontraron ofertas QA."
        )

    lineas = [
        "OFERTAS QA - MAGNETO365",
        "=======================",
        "",
        f"Total de ofertas: {len(ofertas)}",
        "",
    ]

    for numero, oferta in enumerate(
        ofertas,
        start=1,
    ):

        lineas.append(
            f"{numero}. {oferta['titulo']}"
        )

        lineas.append(
            f"Enlace: {oferta['url']}"
        )

        lineas.append("")

        lineas.append(
            "-" * 60
        )

        lineas.append("")

    return "\n".join(lineas)


# ============================================================
# CORREO
# ============================================================

def enviar_correo(reporte):

    mensaje = MIMEText(
        reporte,
        "plain",
        "utf-8",
    )

    mensaje["Subject"] = (
        "Ofertas QA - Magneto365"
    )

    mensaje["From"] = EMAIL_ADDRESS
    mensaje["To"] = EMAIL_TO

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
    ) as servidor:

        servidor.login(
            EMAIL_ADDRESS,
            EMAIL_APP_PASSWORD,
        )

        servidor.sendmail(
            EMAIL_ADDRESS,
            [EMAIL_TO],
            mensaje.as_string(),
        )


# ============================================================
# EJECUCIÓN
# ============================================================

def main():

    print("=" * 60)
    print("BUSCADOR QA - MAGNETO365")
    print("=" * 60)
    print()

    try:

        resultados = buscar_ofertas()

        print(
            f"Enlaces de ofertas encontrados: "
            f"{len(resultados)}"
        )

        print()

        ofertas_qa = filtrar_qa(
            resultados
        )

        print(
            f"Ofertas QA encontradas: "
            f"{len(ofertas_qa)}"
        )

        print()

        reporte = generar_reporte(
            ofertas_qa
        )

        print(reporte)

        enviar_correo(
            reporte
        )

        print()
        print(
            "Correo enviado correctamente."
        )

    except requests.RequestException as error:

        print()
        print(
            "ERROR AL CONSULTAR MAGNETO:"
        )
        print(error)

        raise

    except Exception as error:

        print()
        print(
            "ERROR:"
        )
        print(error)

        raise


if __name__ == "__main__":
    main()
