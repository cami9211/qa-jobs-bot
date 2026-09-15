import os
import re
import smtplib
import requests

from datetime import date
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# ============================================================
# CONFIGURACIÓN
# ============================================================

MAGNETO_URL = "https://www.magneto365.com/co"

EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_APP_PASSWORD = os.environ["EMAIL_APP_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_TO"]

PAGINAS_BUSQUEDA = [
    "https://www.magneto365.com/co/trabajos/ofertas-empleo-de-analista-prueba-software",
]

PALABRAS_CLAVE_QA = [
    "qa",
    "quality assurance",
    "qa engineer",
    "qa analyst",
    "qa tester",
    "tester qa",
    "analista qa",
    "ingeniero qa",
    "ingeniero de pruebas",
    "analista de pruebas",
    "automatización de pruebas",
    "automatizacion de pruebas",
    "pruebas de software",
    "software testing",
    "testing",
]

PALABRAS_SOFTWARE = [
    "software",
    "pruebas",
    "testing",
    "qa",
    "quality assurance",
    "automatización",
    "automatizacion",
    "selenium",
    "cypress",
    "appium",
    "java",
    "javascript",
    "sql",
    "api",
    "postman",
    "jira",
    "git",
    "casos de prueba",
    "caso de prueba",
]

session = requests.Session()

session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
})


def limpiar_texto(texto):
    if not texto:
        return ""

    texto = texto.replace("\xa0", " ")
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def normalizar(texto):
    return limpiar_texto(texto).lower()


def obtener_html(url):
    print(f"Consultando: {url}")

    respuesta = session.get(
        url,
        timeout=30,
        allow_redirects=True,
    )

    respuesta.raise_for_status()

    return respuesta.text


def crear_soup(url):
    return BeautifulSoup(
        obtener_html(url),
        "html.parser"
    )


def es_oferta_qa(texto):
    texto_normalizado = normalizar(texto)

    tiene_qa = any(
        palabra in texto_normalizado
        for palabra in PALABRAS_CLAVE_QA
    )

    tiene_software = any(
        palabra in texto_normalizado
        for palabra in PALABRAS_SOFTWARE
    )

    return tiene_qa and tiene_software


def extraer_enlaces_ofertas(soup):
    ofertas = {}

    for enlace in soup.find_all("a", href=True):
        href = enlace.get("href", "").strip()

        texto = limpiar_texto(
            enlace.get_text(" ", strip=True)
        )

        if not href or not texto:
            continue

        url = urljoin(MAGNETO_URL, href)

        if "/co/empleos/" not in url:
            continue

        ofertas[url] = texto

    return ofertas


def buscar_ofertas():
    ofertas = {}

    for pagina in PAGINAS_BUSQUEDA:
        try:
            soup = crear_soup(pagina)
        except requests.RequestException as error:
            print(f"Error consultando {pagina}: {error}")
            continue

        enlaces = extraer_enlaces_ofertas(soup)

        print(f"Enlaces encontrados: {len(enlaces)}")

        for url, titulo in enlaces.items():
            if url not in ofertas:
                ofertas[url] = {
                    "titulo": titulo,
                    "url": url,
                }

    print(f"Total de ofertas encontradas: {len(ofertas)}")

    return list(ofertas.values())


def extraer_dato(texto, palabras):
    texto_minusculas = texto.lower()

    for palabra in palabras:
        posicion = texto_minusculas.find(palabra.lower())

        if posicion == -1:
            continue

        fragmento = texto[posicion:posicion + 250]
        return limpiar_texto(fragmento)

    return "No especificado"


def detectar_modalidad(texto):
    texto_normalizado = normalizar(texto)

    if "remota" in texto_normalizado or "remoto" in texto_normalizado:
        return "Remota"

    if "híbrida" in texto_normalizado or "hibrida" in texto_normalizado:
        return "Híbrida"

    if "presencial" in texto_normalizado:
        return "Presencial"

    return "No especificada"


def detectar_fecha(texto):
    patrones = [
        r"\b20\d{2}-\d{2}-\d{2}\b",
        r"\b\d{1,2}/\d{1,2}/20\d{2}\b",
    ]

    for patron in patrones:
        coincidencia = re.search(
            patron,
            texto
        )

        if coincidencia:
            return coincidencia.group(0)

    return "No especificada"


def detectar_experiencia(texto):
    patrones = [
        r"\b\d+\+?\s+años?\s+de\s+experiencia\b",
        r"\b\d+\+?\s+meses?\s+de\s+experiencia\b",
    ]

    for patron in patrones:
        coincidencia = re.search(
            patron,
            texto,
            flags=re.IGNORECASE
        )

        if coincidencia:
            return limpiar_texto(
                coincidencia.group(0)
            )

    return "No especificada"


def obtener_descripcion(soup, texto_completo):
    for etiqueta in ["article", "main"]:
        elemento = soup.find(etiqueta)

        if elemento:
            texto = limpiar_texto(
                elemento.get_text(
                    " ",
                    strip=True
                )
            )

            if len(texto) > 100:
                return texto[:2000]

    return texto_completo[:2000]


def extraer_datos_oferta(oferta):
    url = oferta["url"]

    try:
        soup = crear_soup(url)
    except requests.RequestException as error:
        print(f"No fue posible consultar {url}: {error}")
        return None

    texto_completo = limpiar_texto(
        soup.get_text(" ", strip=True)
    )

    titulo = oferta["titulo"]

    h1 = soup.find("h1")

    if h1:
        titulo_h1 = limpiar_texto(
            h1.get_text(" ", strip=True)
        )

        if titulo_h1:
            titulo = titulo_h1

    texto_filtro = f"{titulo} {texto_completo}"

    if not es_oferta_qa(texto_filtro):
        return None

    return {
        "titulo": titulo,
        "empresa": extraer_dato(
            texto_completo,
            ["empresa", "compañía"]
        ),
        "salario": extraer_dato(
            texto_completo,
            ["salario"]
        ),
        "ubicacion": extraer_dato(
            texto_completo,
            ["ubicación", "ubicacion", "lugar"]
        ),
        "modalidad": detectar_modalidad(
            texto_completo
        ),
        "fecha": detectar_fecha(
            texto_completo
        ),
        "experiencia": detectar_experiencia(
            texto_completo
        ),
        "descripcion": obtener_descripcion(
            soup,
            texto_completo
        ),
        "url": url,
    }


def obtener_ofertas_qa():
    ofertas_encontradas = buscar_ofertas()

    ofertas_qa = []
    urls_procesadas = set()

    for numero, oferta in enumerate(
        ofertas_encontradas,
        start=1
    ):
        print(
            f"Procesando oferta "
            f"{numero}/{len(ofertas_encontradas)}"
        )

        url = oferta["url"]

        if url in urls_procesadas:
            continue

        urls_procesadas.add(url)

        datos = extraer_datos_oferta(oferta)

        if datos:
            ofertas_qa.append(datos)

    return ofertas_qa


def generar_reporte(ofertas):
    hoy = date.today().strftime("%d/%m/%Y")

    lineas = [
        "OFERTAS QA - MAGNETO365",
        "=======================",
        "",
        f"Fecha de búsqueda: {hoy}",
        f"Total encontradas: {len(ofertas)}",
        "",
    ]

    if not ofertas:
        lineas.append(
            "No se encontraron ofertas QA de software."
        )
        return "\n".join(lineas)

    for numero, oferta in enumerate(ofertas, start=1):
        lineas.extend([
            f"{numero}. {oferta['titulo']}",
            f"Empresa: {oferta['empresa']}",
            f"Salario: {oferta['salario']}",
            f"Ubicación: {oferta['ubicacion']}",
            f"Modalidad: {oferta['modalidad']}",
            f"Experiencia: {oferta['experiencia']}",
            f"Fecha publicación: {oferta['fecha']}",
            "",
            "Descripción:",
            oferta["descripcion"],
            "",
            f"ENLACE: {oferta['url']}",
            "",
            "-" * 70,
            "",
        ])

    return "\n".join(lineas)


def enviar_correo(reporte):
    hoy = date.today().strftime("%d/%m/%Y")

    mensaje = MIMEText(
        reporte,
        "plain",
        "utf-8"
    )

    mensaje["Subject"] = (
        f"Ofertas QA Magneto - {hoy}"
    )

    mensaje["From"] = EMAIL_ADDRESS
    mensaje["To"] = EMAIL_TO

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
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


def main():
    print("=" * 70)
    print("BUSCADOR DE OFERTAS QA - MAGNETO365")
    print("=" * 70)
    print(f"Fuente: {MAGNETO_URL}")
    print("Sin Google")
    print("Sin Gemini")
    print("Sin Claude")
    print("Sin API externa")
    print("=" * 70)

    ofertas = obtener_ofertas_qa()

    print(
        f"\nOfertas QA válidas: {len(ofertas)}"
    )

    reporte = generar_reporte(ofertas)

    print("\n" + reporte)

    enviar_correo(reporte)

    print("\nCorreo enviado correctamente.")


if __name__ == "__main__":
    main()
