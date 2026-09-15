```python
"""
Busca ofertas de empleo QA (Senior/Semi-Senior, remoto) directamente
en Google y envía los resultados por correo.

NO utiliza inteligencia artificial.

Variables de entorno requeridas (GitHub Secrets):
- GOOGLE_API_KEY       : API Key de Google
- GOOGLE_CX            : ID del buscador personalizado de Google
- EMAIL_ADDRESS        : correo Gmail desde el que se envía
- EMAIL_APP_PASSWORD   : contraseña de aplicación de Gmail
- EMAIL_TO             : correo destino del reporte
"""

import os
import smtplib
import sys
from datetime import date
from email.mime.text import MIMEText

import requests


# ============================================================
# CONFIGURACIÓN
# ============================================================

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
GOOGLE_CX = os.environ["GOOGLE_CX"]

EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_APP_PASSWORD = os.environ["EMAIL_APP_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_TO"]


# ============================================================
# BÚSQUEDAS EN GOOGLE
# ============================================================

BUSQUEDAS = [
    '"QA Engineer" "Senior" remote Colombia',
    '"QA Engineer" "Semi Senior" remote Colombia',
    '"QA Analyst" "Senior" remote Colombia',
    '"QA Analyst" "Semi Senior" remote Colombia',
    '"QA Tester" "Senior" remote Colombia',
    '"QA Tester" "Semi Senior" remote Colombia',

    '"QA Engineer" remote Latin America',
    '"QA Analyst" remote Latin America',
    '"QA Tester" remote Latin America',

    '"QA Automation Engineer" remote Colombia',
    '"QA Automation" remote Latin America',
]


# ============================================================
# GOOGLE SEARCH API
# ============================================================

def buscar_google(query: str) -> list:
    """
    Ejecuta una búsqueda directamente en Google
    utilizando Google Custom Search JSON API.
    """

    url = "https://www.google.com/"

    parametros = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "num": 10,
        "dateRestrict": "d2",
        "hl": "es",
        "gl": "co",
    }

    response = requests.get(
        url,
        params=parametros,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    return data.get("items", [])


# ============================================================
# PROCESAR RESULTADOS
# ============================================================

def procesar_resultados() -> list:
    """
    Realiza todas las búsquedas y elimina resultados duplicados.
    """

    resultados = []
    urls_vistas = set()

    for query in BUSQUEDAS:

        print(f"Buscando en Google: {query}")

        try:
            items = buscar_google(query)

        except Exception as exc:
            print(
                f"Error en búsqueda '{query}': {exc}",
                file=sys.stderr,
            )
            continue

        for item in items:

            titulo = item.get("title", "").strip()
            link = item.get("link", "").strip()
            descripcion = item.get("snippet", "").strip()

            if not link:
                continue

            # Evitar duplicados
            if link in urls_vistas:
                continue

            urls_vistas.add(link)

            resultados.append(
                {
                    "titulo": titulo,
                    "link": link,
                    "descripcion": descripcion,
                }
            )

    return resultados


# ============================================================
# GENERAR REPORTE
# ============================================================

def generar_reporte(resultados: list) -> str:

    if not resultados:
        return "Sin novedades hoy."

    lineas = []

    lineas.append("OFERTAS QA ENCONTRADAS EN GOOGLE")
    lineas.append("=" * 60)
    lineas.append("")

    for i, resultado in enumerate(resultados, start=1):

        lineas.append(f"{i}. {resultado['titulo']}")
        lineas.append("")
        lineas.append(
            f"Resumen: {resultado['descripcion']}"
        )
        lineas.append("")
        lineas.append(
            f"Link: {resultado['link']}"
        )
        lineas.append("")
        lineas.append("-" * 60)
        lineas.append("")

    return "\n".join(lineas)


# ============================================================
# ENVIAR CORREO
# ============================================================

def enviar_correo(cuerpo: str) -> None:

    hoy = date.today().strftime("%d/%m/%Y")

    mensaje = MIMEText(
        cuerpo,
        "plain",
        "utf-8",
    )

    mensaje["Subject"] = f"Ofertas QA del {hoy}"
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
# MAIN
# ============================================================

def main() -> None:

    try:

        resultados = procesar_resultados()

        reporte = generar_reporte(resultados)

        print(reporte)

        enviar_correo(reporte)

        print("")
        print("Correo enviado correctamente.")

    except Exception as exc:

        mensaje_error = (
            f"Ocurrio un error al buscar las ofertas: {exc}"
        )

        print(
            mensaje_error,
            file=sys.stderr,
        )

        try:
            enviar_correo(mensaje_error)
        except Exception as email_error:
            print(
                f"No fue posible enviar el correo: {email_error}",
                file=sys.stderr,
            )

            raise


if __name__ == "__main__":
    main()
```
