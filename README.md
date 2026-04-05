# DAC Solutions Dashboard

Este es un tablero de control (dashboard) profesional desarrollado con **Flet** (un framework de Python para aplicaciones interactivas) que procesa datos en tiempo real desde una hoja de cálculo de Google Drive.

## Características
- **Pantalla de Inicio Estilo Presentación**: Con el mensaje "DAC Solutions - Optimal and cutting-edge solutions for companies".
- **Dashboard Interactivo**:
  - Filtros por **Aplicativo** y **Día**.
  - **KPIs en tiempo real**: Ventas Totales, Total Pedidos y Ticket Promedio.
  - **Cuadro de Mando 1**: Gráficos de Ventas por Sede y Participación por App.
  - **Cuadro de Mando 2**: Gráficos de Ventas por Marca y Ventas por Día.
- **Datos en vivo**: Lee directamente del CSV publicado en Google Drive.
- **Corrección de Errores**: El filtrado funciona correctamente tanto para una selección específica como para la vista general (sin filtros).

## Requisitos
- Python 3.7 o superior
- Bibliotecas: `flet`, `pandas`, `requests`

## Cómo Ejecutar Localmente
1. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecutar la aplicación:
   ```bash
   python main.py
   ```

## Cómo Desplegar en GitHub
1. Crea un repositorio en GitHub.
2. Sube los archivos `main.py`, `requirements.txt` y `README.md`.
3. Para desplegar como una aplicación web, puedes usar **Flet Static Web Export** y subirlo a GitHub Pages:
   ```bash
   flet publish main.py
   ```
   Esto creará una carpeta `dist` que puedes subir a la rama `gh-pages` de tu repositorio.

---
Desarrollado para **DAC Solutions**.
