"""Presentation-only home/navigation wheels; existing actions and translations stay authoritative."""
from pathlib import Path


def install(html: str) -> str:
    root = Path(__file__).parent / 'public_assets' / 'home-carousel'
    css = (root / 'carousel.css').read_text(encoding='utf-8')
    script = (root / 'carousel.js').read_text(encoding='utf-8')
    anchors = ['</style>', '(async function init() {',
               'function bindBottomNavNavigation() {',
               "app.classList.toggle('quiz-mode', id === 'screenQuiz');"]
    for anchor in anchors:
        if html.count(anchor) != 1:
            raise ValueError('home_carousels_web: expected one shell anchor: ' + anchor)
    html = html.replace('</style>', css + '\n</style>', 1)
    html = html.replace('(async function init() {', script + '\n(async function init() {\n  initHomeCarousels();', 1)
    html = html.replace('function bindBottomNavNavigation() {',
                        'function bindBottomNavNavigation() {\n  if (syncCarouselNavigation()) return;', 1)
    return html.replace("app.classList.toggle('quiz-mode', id === 'screenQuiz');",
                        "app.classList.toggle('home-carousel-mode', id === 'screenHome');\n"
                        "  syncCarouselNavigation(id);\n"
                        "  app.classList.toggle('quiz-mode', id === 'screenQuiz');", 1)
