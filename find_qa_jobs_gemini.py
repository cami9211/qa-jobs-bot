"""
Busca ofertas de empleo QA (senior/semi-senior, remoto) usando la API GRATUITA
de Gemini (Google) con búsqueda web integrada, y envía el resumen por correo.

Variables de entorno requeridas (se configuran como GitHub Secrets):
- GEMINI_API_KEY      : tu API key gratuita de Google AI Studio (aistudio.google.com)
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

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_APP_PASSWORD = os.environ["EMAIL_APP_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_TO"]

GEMINI_URL = (
    "https://www.google.com/"
)
PROMPT = (
    "Busca en Google usando el buscador de empleos integrado 'Google para "
    "Empleos' (Google Jobs) ofertas publicadas en las ultimas 24-48 horas "
    "para 'QA Engineer' o 'QA Analyst' o 'QA Tester', nivel senior o "
    "semi-senior, 100% remoto, abiertas a candidatos en Colombia o "
    "Latinoamerica. Usa consultas de busqueda como 'QA Engineer remoto "
    "empleos' o 'QA Tester senior remoto Latinoamerica empleos' para activar "
    "los resultados del panel de Google para Empleos, y revisa esos "
    "resultados en vez de blogs o articulos genericos. "
    "Para cada oferta que encuentres, entrega en texto plano (sin markdown): "
    "nombre de la empresa, titulo del cargo, modalidad, un resumen de 1 linea "
    "de los requisitos clave, y el link directo a la oferta. "
    "Si no encuentras ofertas nuevas relevantes, responde exactamente: "
    "'Sin novedades hoy.' No inventes ofertas ni links; solo incluye lo que "
    "confirmes con la busqueda."
)


def buscar_ofertas() -> str:
    response = requests.post(
        GEMINI_URL,
        headers={
            "content-type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY,
        },
        json={
            "contents": [{"parts": [{"text": PROMPT}]}],
            "tools": [{"google_search": {}}],
        },
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()

    candidatos = data.get("candidates", [])
    if not candidatos:
        return "No se recibio respuesta del modelo."

    partes = candidatos[0].get("content", {}).get("parts", [])
    texto = "\n".join(p.get("text", "") for p in partes if p.get("text"))
    return texto.strip() or "No se recibio texto en la respuesta."


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
