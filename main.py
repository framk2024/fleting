import flet as ft
import flet.canvas as cv
from flet.controls.painting import Paint, PaintingStyle
import flet_charts as fc
import pandas as pd
import requests
import io
import math
import random
import threading
import time

# ── GOOGLE DRIVE CSV ────────────────────────────────────────────────────────
CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vQUuTOVr7WCaB9KxMeFRvTlqnVRqFIejNbJTABNocQUfbCojSAH6ODpWx966KCRHfiYTK_FDympkPZg"
    "/pub?gid=1248310866&single=true&output=csv"
)

# ── DESIGN TOKENS ────────────────────────────────────────────────────────────
C_BG     = "#030712"
C_CARD   = "#0a1628"
C_HEADER = "#0a1628"
C_BORDER = "#1e3a5f"
C_BLUE   = "#60A5FA"
C_GREEN  = "#34D399"
C_ORANGE = "#FB923C"
C_PURPLE = "#C084FC"
C_PINK   = "#F472B6"
C_YELLOW = "#FBBF24"
C_FG     = "#E2E8F0"
C_MUTED  = "#64748B"

PALETTE = [C_BLUE, C_GREEN, C_ORANGE, C_PURPLE, C_PINK, C_YELLOW]


# ── DATA ─────────────────────────────────────────────────────────────────────
def load_data() -> pd.DataFrame:
    try:
        r = requests.get(CSV_URL, timeout=15)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = [str(c).strip() for c in df.columns]
        names = ["Día", "Hora", "Total", "Aplicativo", "Marca", "SEDE", "Estado"]
        col_map = {df.columns[i]: n for i, n in enumerate(names) if i < len(df.columns)}
        df = df.rename(columns=col_map)
        for col, default in [("Día",""), ("Total",0.0), ("Aplicativo",""), ("Marca",""), ("SEDE","")]:
            if col not in df.columns:
                df[col] = default
        df["Total"] = (
            df["Total"].astype(str)
            .str.replace(r"[^\d,.-]", "", regex=True)
            .str.replace(",", ".", regex=False)
            .replace("", "0")
        )
        df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0.0)
        df["Día"] = df["Día"].astype(str).str.strip()
        print(f"[OK] {len(df)} rows, cols: {df.columns.tolist()}", flush=True)
        return df
    except Exception as exc:
        print(f"[ERROR] {exc}", flush=True)
        return pd.DataFrame(columns=["Día", "Total", "Aplicativo", "Marca", "SEDE"])


# ── ANIMATED SPACE BACKGROUND ─────────────────────────────────────────────
class SpaceBg(ft.Stack):
    """
    Space canvas: 120 drifting+twinkling stars, 4 comets with smooth gradient tail.
    Stars move at 0.5–1.5 px/frame. Comets at 3–7 px/frame.
    Canvas on_resize tracks real size. Background rect clears each frame.
    """
    N_STARS  = 120
    N_COMETS = 4

    def __init__(self):
        super().__init__(expand=True)
        self._running = False
        self._page   = None
        self._w = 1280.0
        self._h = 800.0

        def _on_resize(e: cv.CanvasResizeEvent):
            self._w = float(e.width)
            self._h = float(e.height)
            # Rescale stars to new bounds
            for s in self._stars:
                s["x"] = min(s["x"], self._w)
                s["y"] = min(s["y"], self._h)

        self._canvas = cv.Canvas(expand=True, on_resize=_on_resize)

        # Stars: pixel coords, drift velocity, twinkle phase
        self._stars = [
            {
                "x":  random.uniform(0, 1280),
                "y":  random.uniform(0, 800),
                "r":  random.uniform(0.7, 2.2),
                "t":  random.uniform(0, math.pi * 2),
                "dt": random.uniform(0.012, 0.04),   # twinkle phase step
                # VISIBLE drift: 0.5–1.5 px/frame = 10–30 px/sec at 20fps
                "vx": random.uniform(-0.5, 0.5),
                "vy": random.uniform(-0.3, 0.3),
            }
            for _ in range(self.N_STARS)
        ]
        # Ensure at least half stars have noticeable speed
        for s in self._stars:
            if abs(s["vx"]) < 0.2:
                s["vx"] = 0.2 * (1 if s["vx"] >= 0 else -1)

        self._comets = [self._make_comet() for _ in range(self.N_COMETS)]
        # Stagger starting positions so they don't all appear at once
        for i, c in enumerate(self._comets):
            c["x"] += (1280 / self.N_COMETS) * i

        self.controls = [self._canvas]

    def _make_comet(self) -> dict:
        h = max(self._h, 100.0)
        return {
            "x":    random.uniform(-180, -20),
            "y":    random.uniform(h * 0.05, h * 0.92),
            "spd":  random.uniform(3.0, 7.0),   # px/frame — clearly visible
            "tail": random.randint(35, 75),      # tail length px
        }

    def _draw(self):
        w, h = self._w, self._h
        if w < 10 or h < 10:
            return
        shapes: list[cv.Shape] = []

        # 1. Clear frame with dark background
        shapes.append(cv.Rect(
            x=0, y=0, width=w, height=h,
            paint=Paint(color="#030712", style=PaintingStyle.FILL),
        ))

        # 2. Stars — drift + twinkle
        for s in self._stars:
            s["t"] += s["dt"]
            bri   = 0.2 + 0.8 * (0.5 + 0.5 * math.sin(s["t"]))
            val   = int(bri * 255)
            r_val = int(val * 0.80)
            g_val = int(val * 0.88)
            color = f"#{r_val:02x}{g_val:02x}{val:02x}"

            s["x"] += s["vx"]
            s["y"] += s["vy"]
            # wrap-around
            if s["x"] < -3:   s["x"] = w + 3
            if s["x"] > w+3:  s["x"] = -3
            if s["y"] < -3:   s["y"] = h + 3
            if s["y"] > h+3:  s["y"] = -3

            shapes.append(cv.Circle(
                x=s["x"], y=s["y"], radius=s["r"],
                paint=Paint(color=color, style=PaintingStyle.FILL),
            ))

        # 3. Comets — dense gradient dot trail (1 dot per 3px = smooth)
        for c in self._comets:
            c["x"] += c["spd"]
            if c["x"] > w + c["tail"] + 15:
                nc = self._make_comet()
                c.update(nc)

            tail = c["tail"]
            step = 3          # pixels between tail dots → smooth look
            n    = max(1, tail // step)

            for i in range(n + 1):
                frac  = i / n                      # 0 = far tail, 1 = head
                dot_x = c["x"] - tail * (1 - frac)
                dot_y = c["y"]

                # color: near-black at tail → bright blue-white at head
                # blend from #030a18 → #c8e8ff
                r_c = int(3   + frac * frac * 197)   # 3 → 200
                g_c = int(10  + frac * frac * 222)   # 10 → 232
                b_c = int(24  + frac * frac * 231)   # 24 → 255
                r_c = min(255, r_c)
                g_c = min(255, g_c)
                b_c = min(255, b_c)
                col = f"#{r_c:02x}{g_c:02x}{b_c:02x}"

                # radius: tiny tail → 2.5 head
                dot_r = 0.3 + frac * frac * 2.2

                shapes.append(cv.Circle(
                    x=dot_x, y=dot_y, radius=dot_r,
                    paint=Paint(color=col, style=PaintingStyle.FILL),
                ))

        self._canvas.shapes = shapes
        # page.update() flushes all pending diffs to the frontend —
        # canvas.update() alone does NOT repaint from a background thread
        if self._page:
            self._page.update()

    def start(self, page: ft.Page):
        if self._running:
            return
        self._page   = page
        self._running = True

        def _loop():
            while self._running:
                try:
                    if self._w < 10:
                        self._w = float(page.width or 1280)
                        self._h = float(page.height or 800)
                    self._draw()
                except Exception as exc:
                    # Stop cleanly if the WebSocket has closed
                    msg = str(exc).lower()
                    if any(k in msg for k in ("disconnect", "closing", "closed", "invalid state")):
                        self._running = False
                        break
                    # Otherwise silently ignore transient errors
                time.sleep(0.05)   # 20 fps

        threading.Thread(target=_loop, daemon=True).start()

    def stop(self):
        self._running = False


# ── CHART HELPERS ────────────────────────────────────────────────────────────
def bar_chart(df: pd.DataFrame, grp: str, val: str, title: str) -> ft.Control:
    if df.empty or grp not in df.columns:
        return ft.Text("Sin datos", color=C_MUTED)
    grouped = (
        df.groupby(grp)[val].sum().reset_index()
        .sort_values(val, ascending=False).head(8).reset_index(drop=True)
    )
    groups = [
        fc.BarChartGroup(x=i, rods=[fc.BarChartRod(
            from_y=0, to_y=float(row[val]), width=18,
            color=PALETTE[i % len(PALETTE)],
            tooltip=ft.Text(f"S/ {row[val]:,.0f}", size=10),
        )])
        for i, row in grouped.iterrows()
    ]
    labels = [
        fc.ChartAxisLabel(
            value=i,
            label=ft.Container(
                content=ft.Text(str(row[grp])[:10], size=9, color=C_MUTED),
                padding=ft.Padding(4, 4, 4, 0),
            ),
        )
        for i, row in grouped.iterrows()
    ]
    return ft.Column(expand=True, controls=[
        ft.Text(title, size=13, weight=ft.FontWeight.BOLD, color=C_FG),
        fc.BarChart(
            groups=groups,
            left_axis=fc.ChartAxis(
                title=ft.Text("S/", size=9, color=C_MUTED),
                title_size=40,
                label_size=65,
            ),
            bottom_axis=fc.ChartAxis(labels=labels, label_size=40),
            expand=True,
        ),
    ])


def pie_chart(df: pd.DataFrame, grp: str, val: str, title: str) -> ft.Control:
    if df.empty or grp not in df.columns:
        return ft.Text("Sin datos", color=C_MUTED)
    grouped = (
        df.groupby(grp)[val].sum().reset_index()
        .sort_values(val, ascending=False).reset_index(drop=True)
    )
    total = grouped[val].sum()
    if total == 0:
        return ft.Text("Sin datos", color=C_MUTED)
    sections = [
        fc.PieChartSection(
            value=float(row[val]),
            title=f"{row[val]/total*100:.0f}%",
            title_style=ft.TextStyle(size=9, color="white", weight=ft.FontWeight.BOLD),
            color=PALETTE[i % len(PALETTE)],
            radius=80,
        )
        for i, row in grouped.iterrows()
    ]
    legend = ft.Column(spacing=5, controls=[
        ft.Row(spacing=6, controls=[
            ft.Container(width=9, height=9, bgcolor=PALETTE[i % len(PALETTE)], border_radius=2),
            ft.Text(f"{str(row[grp])[:16]}: S/{row[val]:,.0f}", size=10, color=C_MUTED),
        ])
        for i, row in grouped.head(6).iterrows()
    ])
    return ft.Column(expand=True, controls=[
        ft.Text(title, size=13, weight=ft.FontWeight.BOLD, color=C_FG),
        ft.Row(expand=True, controls=[
            fc.PieChart(sections=sections, sections_space=2, center_space_radius=22, expand=True),
            legend,
        ]),
    ])


def kpi_card(label: str, value: str, accent: str) -> ft.Container:
    return ft.Container(
        col={"xs": 12, "sm": 4},    # full width on xs, 1/3 on sm+
        bgcolor="#0f172a",
        border_radius=12,
        padding=ft.Padding(20, 16, 20, 16),
        border=ft.Border(
            top=ft.BorderSide(3, accent),
            bottom=ft.BorderSide(1, C_BORDER),
            left=ft.BorderSide(1, C_BORDER),
            right=ft.BorderSide(1, C_BORDER),
        ),
        content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, controls=[
            ft.Text(label, size=12, color=C_MUTED),
            ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=accent),
        ]),
    )


def chart_card(content: ft.Control, col_cfg: dict) -> ft.Container:
    return ft.Container(
        col=col_cfg,
        content=content,
        bgcolor="#0a1628cc",
        border_radius=12,
        padding=18,
        border=ft.Border.all(1, C_BORDER),
        height=320,
    )


# ── MAIN ─────────────────────────────────────────────────────────────────────
def main(page: ft.Page):
    page.title    = "DAC Solutions Dashboard"
    page.bgcolor  = C_BG
    page.theme_mode = ft.ThemeMode.DARK
    page.padding  = 0
    page.spacing  = 0
    page.window_maximized = True

    df_raw = load_data()

    # space background (singleton shared between views)
    space = SpaceBg()

    # ── DASHBOARD ──────────────────────────────────────────────────────────
    def show_dashboard(e=None):
        page.clean()

        apps = ["Todos"] + sorted(df_raw["Aplicativo"].dropna().unique().tolist())
        days = ["Todos"] + sorted(df_raw["Día"].dropna().unique().tolist())
        state = {"app": "Todos", "day": "Todos", "tab": 0}

        kpi_row  = ft.ResponsiveRow(spacing=14, run_spacing=10)
        tab1_row = ft.ResponsiveRow(spacing=14, run_spacing=14, expand=True)
        tab2_row = ft.ResponsiveRow(spacing=14, run_spacing=14, expand=True, visible=False)

        def refresh():
            df = df_raw.copy()
            if state["app"] != "Todos":
                df = df[df["Aplicativo"] == state["app"]]
            if state["day"] != "Todos":
                df = df[df["Día"] == state["day"]]

            s  = df["Total"].sum()
            n  = len(df)
            av = s / n if n > 0 else 0

            kpi_row.controls = [
                kpi_card("Ventas Totales",  f"S/ {s:,.0f}", C_BLUE),
                kpi_card("Total Pedidos",   f"{n:,}",        C_GREEN),
                kpi_card("Ticket Promedio", f"S/ {av:,.0f}", C_ORANGE),
            ]
            tab1_row.controls = [
                chart_card(bar_chart(df, "SEDE",       "Total", "Ventas por Sede"),
                           {"xs": 12, "md": 7}),
                chart_card(pie_chart(df, "Aplicativo", "Total", "Participación por App"),
                           {"xs": 12, "md": 5}),
            ]
            tab2_row.controls = [
                chart_card(bar_chart(df, "Marca", "Total", "Ventas por Marca"),
                           {"xs": 12, "md": 6}),
                chart_card(bar_chart(df, "Día",   "Total", "Ventas por Día"),
                           {"xs": 12, "md": 6}),
            ]
            page.update()

        def on_app(e):
            state["app"] = e.control.value
            refresh()

        def on_day(e):
            state["day"] = e.control.value
            refresh()

        dd_app = ft.Dropdown(label="Aplicativo", value="Todos", width=200, bgcolor="#0f172a",
                             options=[ft.dropdown.Option(a) for a in apps], on_select=on_app)
        dd_day = ft.Dropdown(label="Día",        value="Todos", width=160, bgcolor="#0f172a",
                             options=[ft.dropdown.Option(d) for d in days], on_select=on_day)

        header = ft.Container(
            bgcolor=C_HEADER,
            padding=ft.Padding(24, 12, 24, 12),
            border=ft.Border(bottom=ft.BorderSide(2, C_BLUE)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                wrap=True,
                controls=[
                    ft.Column(spacing=2, controls=[
                        ft.Text("DAC SOLUTIONS", size=20, weight=ft.FontWeight.BOLD, color=C_BLUE),
                        ft.Text("Dashboard de Gestión Operativa", size=11, color=C_MUTED),
                    ]),
                    ft.Row(spacing=10, wrap=True, controls=[dd_app, dd_day]),
                ],
            ),
        )

        # Custom tab bar — no ft.Tabs (avoids "Tab content must be provided" error)
        tab_btn_1 = ft.Container(
            content=ft.Text("CUADRO DE MANDO 1", size=12, weight=ft.FontWeight.BOLD,
                            color="white"),
            bgcolor=C_BLUE, border_radius=8,
            padding=ft.Padding(18, 10, 18, 10),
            on_click=lambda e: switch_tab(0),
            ink=True,
        )
        tab_btn_2 = ft.Container(
            content=ft.Text("CUADRO DE MANDO 2", size=12, weight=ft.FontWeight.BOLD,
                            color=C_MUTED),
            bgcolor="#1e3a5f", border_radius=8,
            padding=ft.Padding(18, 10, 18, 10),
            on_click=lambda e: switch_tab(1),
            ink=True,
        )
        tabs_row = ft.Row(spacing=10, controls=[tab_btn_1, tab_btn_2])

        def switch_tab(idx: int):
            state["tab"] = idx
            tab1_row.visible = (idx == 0)
            tab2_row.visible = (idx == 1)
            # Highlight active tab
            tab_btn_1.bgcolor = C_BLUE if idx == 0 else "#1e3a5f"
            tab_btn_2.bgcolor = C_BLUE if idx == 1 else "#1e3a5f"
            tab_btn_1.content.color = "white" if idx == 0 else C_MUTED
            tab_btn_2.content.color = "white" if idx == 1 else C_MUTED
            page.update()

        # ── Sticky header + scrollable body ──────────────────────────────────
        # header is OUTSIDE the scroll area so it stays visible on mobile
        body_col = ft.Column(
            expand=True,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,   # only body scrolls
            controls=[
                ft.Container(content=kpi_row,  padding=ft.Padding(20, 14, 20, 8)),
                ft.Container(content=tabs_row,  padding=ft.Padding(16, 8, 16, 8),
                             bgcolor=C_HEADER,
                             border=ft.Border(bottom=ft.BorderSide(1, C_BORDER))),
                ft.Container(content=tab1_row,  padding=ft.Padding(16, 12, 16, 16)),
                ft.Container(content=tab2_row,  padding=ft.Padding(16, 12, 16, 16)),
            ],
        )

        # outer Column: NO scroll — header is always visible (sticky)
        content_col = ft.Column(
            expand=True,
            spacing=0,
            controls=[
                header,     # ← sticky, never scrolls away
                body_col,   # ← scrollable content below
            ],
        )

        page.add(ft.Stack(
            expand=True,
            controls=[
                space,        # animated background
                content_col,  # dashboard on top
            ],
        ))
        space.start(page)
        page.on_disconnect = lambda _: space.stop()  # clean up on browser close
        refresh()

    # ── INTRO ──────────────────────────────────────────────────────────────
    def show_intro():
        page.clean()

        content = ft.Container(
            expand=True,
            content=ft.Column(
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Container(height=40),

                    # Glowing title
                    ft.Text(
                        "DAC Solutions",
                        size=72,
                        weight=ft.FontWeight.BOLD,
                        color=C_BLUE,
                        text_align=ft.TextAlign.CENTER,
                    ),

                    ft.Container(height=8),

                    ft.Text(
                        "Optimal and cutting-edge solutions for companies",
                        size=20,
                        italic=True,
                        color=C_MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),

                    ft.Container(height=50),

                    # CTA button
                    ft.Container(
                        ink=True,
                        on_click=show_dashboard,
                        bgcolor=C_BLUE,
                        border_radius=14,
                        padding=ft.Padding(48, 18, 48, 18),
                        shadow=ft.BoxShadow(
                            spread_radius=2,
                            blur_radius=20,
                            color="#6060A5FA",
                            offset=ft.Offset(0, 6),
                        ),
                        content=ft.Text(
                            "INGRESAR AL DASHBOARD",
                            size=17,
                            weight=ft.FontWeight.BOLD,
                            color="white",
                        ),
                    ),
                ],
            ),
        )

        page.add(ft.Stack(
            expand=True,
            controls=[space, content],
        ))
        space.start(page)
        page.on_disconnect = lambda _: space.stop()  # clean up on browser close
        page.update()

    show_intro()


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 80))
    ft.run(main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=port)
