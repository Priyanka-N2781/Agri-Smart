from pathlib import Path
from shutil import copytree, rmtree
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agri_smart.web_app import create_app

DOCS = ROOT / "docs"

PAGES = {
    "/": "index.html",
    "/yield-prediction": "yield-prediction.html",
    "/disease-prediction": "disease-prediction.html",
    "/fertilizer-recommendation": "fertilizer-recommendation.html",
    "/weather-prediction": "weather-prediction.html",
    "/about": "about.html",
}


def make_static_links(html: str) -> str:
    replacements = {
        'href="/static/': 'href="static/',
        'src="/static/': 'src="static/',
        'href="/"': 'href="index.html"',
        'href="/yield-prediction"': 'href="yield-prediction.html"',
        'href="/disease-prediction"': 'href="disease-prediction.html"',
        'href="/fertilizer-recommendation"': 'href="fertilizer-recommendation.html"',
        'href="/weather-prediction"': 'href="weather-prediction.html"',
        'href="/about"': 'href="about.html"',
        'action="/yield-prediction"': 'action="yield-prediction.html"',
        'action="/disease-prediction"': 'action="disease-prediction.html"',
        'action="/fertilizer-recommendation"': 'action="fertilizer-recommendation.html"',
        'action="/weather-prediction"': 'action="weather-prediction.html"',
    }
    for old, new in replacements.items():
        html = html.replace(old, new)
    return html


def main() -> None:
    if DOCS.exists():
        rmtree(DOCS)
    DOCS.mkdir()

    app = create_app()
    with app.test_client() as client:
        for route, filename in PAGES.items():
            response = client.get(route)
            if response.status_code >= 400:
                raise RuntimeError(f"Could not render {route}: HTTP {response.status_code}")
            html = make_static_links(response.get_data(as_text=True))
            (DOCS / filename).write_text(html, encoding="utf-8")

    copytree(ROOT / "static", DOCS / "static")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")


if __name__ == "__main__":
    main()
