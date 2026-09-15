import os
import smtplib

from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright


# ============================================================
# CONFIGURACIÓN
# ============================================================

URL_MAGNETO = (
    "https://www.magneto365.com/co/"
    "trabajos/ofertas-empleo-de-analista-prueba-software"
)

EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_APP_PASSWORD = os.environ["EMAIL_APP_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_TO"]


# ============================================================
# PALABRAS CLAVE
# ============================================================

PALABRAS_QA = [
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


# ============================================================
# BUSCAR OFERTAS EN MAGNETO
# ============================================================

def buscar_ofertas():

    print("=" * 70)
    print("CONSULTANDO MAGNETO365")
    print("=" * 70)
    print()

    ofertas = []

    with sync_playwright() as p:

        navegador = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        pagina = navegador.new_page(
            viewport={
                "width": 1440,
                "height": 900,
            },
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/140.0.0.0 Safari/537.36"
            ),
        )

        print("Abriendo Magneto...")
        print(URL_MAGNETO)
        print()

        pagina.goto(
            URL_MAGNETO,
            wait_until="domcontentloaded",
            timeout=120000,
        )

        print(
            "Página cargada."
        )

        # Esperar a que aparezca el contenido.
        pagina.wait_for_timeout(8000)

        print(
            "Contenido cargado."
        )

        # ----------------------------------------------------
        # OBTENER TODOS LOS ENLACES
        # ----------------------------------------------------

        enlaces = pagina.locator(
            "a[href]"
        )

        cantidad = enlaces.count()

        print(
            f"Enlaces encontrados en la página: "
            f"{cantidad}"
        )

        vistos = set()

        for i in range(cantidad):

            enlace = enlaces.nth(i)

            try:

                href = enlace.get_attribute(
                    "href"
                )

                titulo = enlace.inner_text(
                    timeout=3000
                ).strip()

            except Exception:

                continue

            if not href:
                continue

            if not titulo:
                continue

            # Convertir URL relativa en absoluta.
            if href.startswith("/"):

                href = (
                    "https://www.magneto365.com"
                    + href
                )

            # Solo ofertas individuales.
            if "/co/empleos/" not in href:
                continue

            # Evitar duplicados.
            if href in vistos:
                continue

            vistos.add(href)

            titulo_minuscula = (
                titulo.lower()
            )

            # ------------------------------------------------
            # FILTRO QA
            # ------------------------------------------------

            es_qa = any(
                palabra in titulo_minuscula
                for palabra in PALABRAS_QA
            )

            if not es_qa:
                continue

            ofertas.append({
                "titulo": titulo,
                "url": href,
            })

        navegador.close()

    return ofertas


# ============================================================
# GENERAR REPORTE
# ============================================================

def generar_reporte(ofertas):

    lineas = [
        "OFERTAS QA - MAGNETO365",
        "=======================",
        "",
        f"Total de ofertas encontradas: {len(ofertas)}",
        "",
    ]

    if not ofertas:

        lineas.append(
            "No se encontraron ofertas QA."
        )

        return "\n".join(lineas)

    for numero, oferta in enumerate(
        ofertas,
        start=1,
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
        timeout=30,
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

    print(
        "Correo enviado correctamente."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("BUSCADOR DE OFERTAS QA")
    print("=" * 70)
    print("Fuente: Magneto365")
    print("Método: navegador Chromium")
    print("Google: NO")
    print("Gemini: NO")
    print("Claude: NO")
    print("API de búsqueda: NO")
    print("=" * 70)
    print()

    try:

        ofertas = buscar_ofertas()

        print()
        print("=" * 70)
        print(
            f"OFERTAS QA ENCONTRADAS: "
            f"{len(ofertas)}"
        )
        print("=" * 70)
        print()

        reporte = generar_reporte(
            ofertas
        )

        print(reporte)

        enviar_correo(
            reporte
        )

        print()
        print("=" * 70)
        print("PROCESO TERMINADO CORRECTAMENTE")
        print("=" * 70)

    except Exception as error:

        print()
        print("=" * 70)
        print("ERROR")
        print("=" * 70)
        print(error)

        raise


if __name__ == "__main__":
    main()
