# Implementation Plan - Flet Dashboard for DAC Solutions

## Goal
Build a Python Flet application with a presentation intro and a two-tab dashboard that fetches and processes data from a Google Drive CSV.

## Components
1. **Intro Screen**: A "PowerPoint-style" presentation screen featuring:
   - Title: "DAC Solutions"
   - Subtitle: "Optimal and cutting-edge solutions for companies"
   - A way to enter the dashboard.
2. **Dashboard Logic**:
   - Data Source: Fetches CSV from Google Sheets URL.
   - Filtering: Filter records by `Aplicativo` (Application) and `Día` (Day).
   - Initial State: All charts show data for the entire dataset when no filters are applied.
3. **Dashboard Tabs**:
   - **Tab 1: Cuadro de Mando 1**: Overall performance metrics and charts.
   - **Tab 2: Cuadro de Mando 2**: Detailed breakdown or different visualization angles.
   - Use Flet tabs for navigation.

## Technology Stack
- **Flet**: Core application framework.
- **Pandas**: For data manipulation and filtering.
- **Requests/Urllib**: To fetch the CSV from Google Drive.
- **Flet Charts (BarChart, LineChart, PieChart)**: For visualizations.

## Steps
1.  **Environment Setup**: Install `flet` and `pandas`.
2.  **Data Fetching & Cleaning**: 
    - Fetch the CSV from the Google Drive link.
    - Parse "Total" column (handle commas and currency if necessary).
    - Parse dates.
3.  **App Structure**:
    - Main entry points for the intro and the dashboard.
    - Router or simple state management to switch between them.
4.  **Intro Page Implementation**:
    - High-end aesthetics for "DAC Solutions".
5.  **Dashboard Implementation**:
    - Filtering UI (Dropdowns/Checkboxes for `Aplicativo` and `Día`).
    - Calculation of KPIs (Total Sales, Count of Orders, etc.).
    - Interactive charts.
6.  **Refinement**: Ensure the filtering works as requested (initially all data, then filtered).

## GitHub Deployment
- The app will be structured for deployment on GitHub (likely as a runnable script in a repo or using Flet's web export).
