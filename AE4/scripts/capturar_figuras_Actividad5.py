import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
SECCIONES = ["P0 ·", "P1 ·", "P2 ·", "P3 ·", "P4 ·", "P5 ·", "P6 ·"]
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge")
    pg = b.new_page(viewport={"width": 1500, "height": 1000}, device_scale_factor=2)
    pg.goto("http://localhost:8501", wait_until="networkidle")
    pg.wait_for_selector("[data-testid=stSidebar]", timeout=60000)
    pg.evaluate("document.querySelector('[data-testid=stSidebarCollapseButton] button, [data-testid=stSidebarCollapseButton]')?.click()")
    for s in SECCIONES:
        pg.get_by_text(s, exact=False).first.click()
        pg.wait_for_timeout(6000)
        charts = pg.locator("[data-testid=stPlotlyChart]")
        for k in range(charts.count()):
            c = charts.nth(k)
            c.scroll_into_view_if_needed()
            pg.wait_for_timeout(800)
            c.screenshot(path=str(OUT / f"{s[:2]}_{k + 1}.png"))
    b.close()
print(sorted(x.name for x in OUT.iterdir()))
