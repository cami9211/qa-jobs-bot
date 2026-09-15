import os
import smtplib
import time
import requests

from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# ============================================================
# CONFIGURACIÓN
# ============================================================

URL_MAGNETO = "https://www.magneto365.com/co"

EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_APP_PASSWORD = os.environ["EMAIL_APP_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_TO"]


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/avif,"
        "image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
}


# ============================================================
# CONSULTAR MAGNETO
# ============================================================

def consultar_magneto():

    print("=" * 70)
    print("CONSULTANDO MAGNETO365")
    print("=" * 70)
    print()
    print(f"URL: {URL_MAGNETO}")
    print()

    for intento in range(1, 4):

        print(
            f"Intento {intento}/3..."
        )

        try:

            respuesta = requests.get(
                URL_MAGNETO,
                headers=HEADERS,
                timeout=(15, 90),
                allow_redirects=True,
            )

            print(
                f"HTTP: {respuesta.status_code}"
            )

            print(
                f"URL final: {respuesta.url}"
            )

            print(
                f"Tamaño recibido: "
                f"{len(respuesta.content)} bytes"
            )

            print()

            respuesta.raise_for_status()

            return respuesta.text

        except requests.exceptions.Timeout:

            print(
                "Magneto tardó demasiado en responder."
            )

            if intento < 3:
                print(
                    "Esperando 5 segundos antes "
                    "del siguiente intento..."
                )
                time.sleep(5)

        except requests.exceptions.RequestException as error:

            print(
                f"Error de conexión: {error}"
            )

            if intento < 3:
                print(
                    "Esperando 5 segundos antes "
                    "del siguiente intento..."
                )
                time.sleep(5)

    raise RuntimeError(
        "No fue posible acceder a Magneto365 "
        "después de 3 intentos."
    )


# ============================================================
# BUSCAR ENLACES
# ============================================================

def buscar_enlaces(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    resultados = []
    vistos = set()

    print("=" * 70)
    print("BUSCANDO OFERTAS")
    print("=" * 70)
    print()

    for enlace in soup.find_all(
        "a",
        href=True
    ):

        href = enlace.get(
            "href",
            ""
        ).strip()

        titulo = enlace.get_text(
            " ",
            strip=True
        )

        if not href:
            continue

        if not titulo:
            continue

        url = urljoin(
            URL_MAGNETO,
            href
        )

        if "/co/empleos/" not in url:
            continue

        if url in vistos:
            continue

        vistos.add(url)

        resultados.append({
            "titulo": titulo,
            "url": url,
        })

    print(
        f"Enlaces de empleo encontrados: "
        f"{len(resultados)}"
    )

    return resultados


# ============================================================
# FILTRAR QA
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

    ofertas = []

    for oferta in resultados:

        titulo = oferta["titulo"].lower()

        for palabra in palabras:

            if palabra in titulo:

                ofertas.append(oferta)

                break

    return ofertas


# ============================================================
# REPORTE
# ============================================================

def generar_reporte(ofertas):

    lineas = [
        "OFERTAS QA - MAGNETO365",
        "=======================",
        "",
    ]

    if not ofertas:

        lineas.append(
            "No se encontraron ofertas QA "
            "en la página consultada."
        )

        return "\n".join(lineas)

    lineas.append(
        f"Total: {len(ofertas)}"
    )

    lineas.append("")

    for numero, oferta in enumerate(
        ofertas,
        1
    ):

        lineas.append(
            f"{numero}. {oferta['titulo']}"
        )

        lineas.append(
            f"Link: {oferta['url']}"
        )

        lineas.append("")

        lineas.append(
            "-" * 70
        )

        lineas.append("")

    return "\n".join(lineas)


# ============================================================
# ENVIAR CORREO
# ============================================================

def enviar_correo(reporte):

    print()
    print("=" * 70)
    print("ENVIANDO CORREO")
    print("=" * 70)

    mensaje = MIMEText(
        reporte,
        "plain",
        "utf-8"
    )

    mensaje["Subject"] = (
        "Ofertas QA - Magneto365"
    )

    mensaje["From"] = EMAIL_ADDRESS
    mensaje["To"] = EMAIL_TO

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
        timeout=30
    ) as servidor:

        servidor.login(
            EMAIL_ADDRESS,
            EMAIL_APP_PASSWORD
        )

        servidor.sendmail(
            EMAIL_ADDRESS,
            [EMAIL_TO],
            mensaje.as_string()
        )

    print(
        "Correo enviado correctamente."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("BUSCADOR QA - MAGNETO365")
    print("=" * 70)
    print()

    # 1. Consultar Magneto
    html = consultar_magneto()

    # 2. Buscar ofertas
    resultados = buscar_enlaces(html)

    # 3. Filtrar QA
    ofertas = filtrar_qa(resultados)

    print()
    print(
        f"Ofertas QA encontradas: "
        f"{len(ofertas)}"
    )

    # 4. Generar reporte
    reporte = generar_reporte(
        ofertas
    )

    print()
    print(reporte)

    # 5. Enviar correo
    enviar_correo(
        reporte
    )

    print()
    print("=" * 70)
    print("PROCESO FINALIZADO")
    print("=" * 70)


if __name__ == "__main__":
    main()
