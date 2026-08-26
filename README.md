# Bot diario de ofertas QA

Este automatismo corre TODOS LOS DÍAS en la nube de GitHub (no en tu laptop),
busca ofertas de empleo QA senior/semi-senior remoto, y te envía un resumen
por correo electrónico.

## Pasos para activarlo (una sola vez, ~10 minutos)

### 1. Crear el repositorio en GitHub
1. Entra a github.com, haz clic en "New repository".
2. Nómbralo por ejemplo `qa-jobs-bot`. Puede ser privado.
3. Sube estos dos archivos manteniendo la misma carpeta:
   - `find_qa_jobs.py`
   - `.github/workflows/qa-jobs.yml`
   (Puedes arrastrarlos en la interfaz web de GitHub o usar `git push`.)

### 2. Conseguir tu API key de Anthropic
1. Entra a https://console.anthropic.com
2. Ve a "API Keys" y crea una nueva key.
3. Cópiala (empieza con `sk-ant-...`). Nota: esto usa la API de pago de
   Anthropic (facturación por uso), es independiente de tu cuenta de Claude.ai.
   El costo diario de esta búsqueda es muy bajo (unos pocos centavos de dólar
   al mes).

### 3. Crear una "contraseña de aplicación" de Gmail
(Necesaria porque Gmail no permite usar tu contraseña normal desde scripts)
1. Activa la verificación en dos pasos en tu cuenta de Gmail si no la tienes.
2. Ve a https://myaccount.google.com/apppasswords
3. Genera una contraseña de aplicación y cópiala (16 caracteres).

### 4. Configurar los "Secrets" en GitHub
En tu repositorio: Settings → Secrets and variables → Actions → New repository secret.
Crea estos 4 secrets:

| Nombre               | Valor                                      |
|----------------------|---------------------------------------------|
| ANTHROPIC_API_KEY    | tu API key de Anthropic                    |
| EMAIL_ADDRESS        | tu correo de Gmail (el que envía)          |
| EMAIL_APP_PASSWORD   | la contraseña de aplicación de 16 caracteres|
| EMAIL_TO             | el correo donde quieres recibir el reporte |

### 5. Probarlo
En tu repositorio, ve a la pestaña "Actions" → "Buscar ofertas QA diarias" →
"Run workflow" → Run workflow. En 1-2 minutos deberías recibir el primer
correo de prueba.

## ¿Cuándo corre?
Todos los días a las 8:00 AM hora Colombia, automáticamente, sin que tengas
que abrir tu computador ni Claude. Corre en los servidores de GitHub.

## Cambiar la hora
Edita la línea `cron: "0 13 * * *"` en `qa-jobs.yml`. El formato es
`minuto hora * * *` en horario UTC (Colombia = UTC-5, así que réstale 5
horas a la hora que quieras en Colombia).

## Cambiar los criterios de búsqueda
Edita el texto de la variable `PROMPT` en `find_qa_jobs.py` (nivel, ubicación,
palabras clave, fuentes a revisar, etc.).
