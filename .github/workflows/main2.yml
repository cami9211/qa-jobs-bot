name: Buscar ofertas QA diarias

on:
  schedule:
    - cron: "*/5 * * * *"

  workflow_dispatch:

jobs:
  buscar-ofertas:
    runs-on: ubuntu-latest

    steps:
      - name: Clonar repositorio
        uses: actions/checkout@v4
        with:
          ref: main
          fetch-depth: 0

      - name: Verificar commit
        run: |
          echo "Commit ejecutado:"
          git rev-parse HEAD
          git log -1 --oneline

      - name: Configurar Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Instalar dependencias
        run: |
          python -m pip install --upgrade pip
          pip install requests beautifulsoup4

      - name: Ejecutar búsqueda
        env:
          EMAIL_ADDRESS: ${{ secrets.EMAIL_ADDRESS }}
          EMAIL_APP_PASSWORD: ${{ secrets.EMAIL_APP_PASSWORD }}
          EMAIL_TO: ${{ secrets.EMAIL_TO }}
        run: |
          python find_qa_jobs.py
