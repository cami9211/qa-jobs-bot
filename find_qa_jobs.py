"""
Busca ofertas de empleo QA (senior/semi-senior, remoto) usando la API de Claude
con la herramienta de búsqueda web, y envía el resumen por correo.

Variables de entorno requeridas (se configuran como GitHub Secrets):
- ANTHROPIC_API_KEY   : tu API key de Anthropic (console.anthropic.com)
- EMAIL_ADDRESS       : correo Gmail desde el que se envía (ej: tucuenta@gmail.com)
- EMAIL_APP_PASSWORD  : contraseña de aplicación de Gmail (NO tu contraseña normal)
- EMAIL_TO            : correo destino donde quieres recibir el reporte
"""

import os
import smtplib
import sys
from datetime import date
from email.mime.text import MIMEText

import requests

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_APP_PASSWORD = os.environ["EMAIL_APP_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_TO"]

PROMPT = (
    "Busca ofertas de empleo publicadas en las ultimas 24-48 horas para "
    "'QA Engineer' o 'QA Analyst' o 'QA Tester', nivel senior o semi-senior, "
    "100% remoto, abiertas a candidatos en Colombia o Latinoamerica. "
    "Revisa fuentes como LinkedIn Jobs, Get on Board, Workana, RemoteOK, "
    "We Work Remotely y paginas de empleo de empresas tech. "
    "Para cada oferta que encuentres, entrega en texto plano (sin markdown): "
    "nombre de la empresa, titulo del cargo, modalidad, un resumen de 1 linea "
    "de los requisitos clave, y el link directo a la oferta. "
    "Si no encuentras ofertas nuevas relevantes, responde exactamente: "
    "'Sin novedades hoy.' No inventes ofertas ni links; solo incluye lo que "
    "confirmes con la busqueda."
)


def buscar_ofertas() -> str:
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": PROMPT}],
            "tools": [{"type": "web_search_20250305", "name": "web_search"}],
        },
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()

    partes_texto = [
        block.get("text", "")
        for block in data.get("content", [])
        if block.get("type") == "text"
    ]
    texto = "\n".join(p for p in partes_texto if p).strip()
    return texto or "No se recibio respuesta de texto del modelo."


def enviar_correo(cuerpo: str) -> None:
    hoy = date.today().strftime("%d/%m/%Y")
    mensaje = MIMEText(cuerpo, "plain", "utf-8")
    mensaje["Subject"] = f"Ofertas QA del {hoy}"
    mensaje["From"] = EMAIL_ADDRESS
    mensaje["To"] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
        servidor.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        servidor.sendmail(EMAIL_ADDRESS, [EMAIL_TO], mensaje.as_string())


def main() -> None:
    try:
        resultado = buscar_ofertas()
    except Exception as exc:  # noqa: BLE001
        resultado = f"Ocurrio un error al buscar las ofertas: {exc}"
        print(resultado, file=sys.stderr)

    enviar_correo(resultado)
    print("Correo enviado correctamente.")


if __name__ == "__main__":
    main()
