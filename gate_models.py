"""Versioned model capabilities. Catalog support does not imply account access."""
from __future__ import annotations

APP_VERSION = '2.8.0'
CLI_DOWNLOAD_URL = 'https://learn.chatgpt.com/docs/codex/cli'
CLI_CHANGELOG_URL = 'https://learn.chatgpt.com/docs/changelog'
CATALOG_CHECKED_AT = '2026-10-01'
MODEL_IDS = {'luna': 'gpt-6-luna', 'sol': 'gpt-6.1-sol',
             'astra': 'gpt-6-astra', 'sol6': 'gpt-6-sol', 'terra': 'gpt-5.6-terra'}
MODEL_MINIMUM_CLI = {'sol': (0, 159, 1), 'luna': (0, 156, 1), 'sol6': (0, 156, 1)}
MODEL_EFFORTS = {key: ('low', 'medium', 'high', 'xhigh', 'max') for key in MODEL_IDS}
BASE_MODEL_IDS = dict(MODEL_IDS)
BASE_MODEL_EFFORTS = dict(MODEL_EFFORTS)


def supported_efforts(model: str) -> tuple[str, ...]:
    return MODEL_EFFORTS.get(model, ())


def model_label(model: str) -> str:
    return {'sol': 'Sol 6.1', 'sol6': 'Sol 6 (anterior)'}.get(model, model if model.startswith('gpt-') else model.capitalize())


def model_key(label: str) -> str:
    return next((k for k in MODEL_IDS if model_label(k).casefold() == label.casefold()), label.lower())


def local_catalog(home, version):
    """Read only public model metadata; never authentication or identity fields."""
    import json
    import re
    from pathlib import Path
    try:
        if not version:
            return []
        path = Path(home) / 'models_cache.json'
        if path.stat().st_size > 5_000_000:
            return []
        data = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(data, dict) or not isinstance(data.get('models'), list):
            return []
        if version and str(data.get('client_version')) != '.'.join(map(str, version)):
            return []
        result = []
        for entry in data['models']:
            if not isinstance(entry, dict):
                continue
            slug = entry.get('slug', '')
            if not isinstance(slug, str) or not re.fullmatch(r'gpt-[a-zA-Z0-9.-]{1,80}', slug):
                continue
            levels = entry.get('supported_reasoning_levels', [])
            efforts = tuple(x.get('effort') for x in levels if isinstance(x, dict)
                            and x.get('effort') in {'low', 'medium', 'high', 'xhigh', 'max', 'ultra'})
            if efforts:
                result.append({'id': slug, 'efforts': efforts})
        return result
    except (OSError, UnicodeError, ValueError, TypeError):
        return []


def latest_cli_release():
    """An explicit, bounded check of official release notes; no downloaded code."""
    import re
    from urllib.request import Request, urlopen
    request = Request(CLI_CHANGELOG_URL, headers={'User-Agent': 'CodexModelGate/2.7'})
    with urlopen(request, timeout=8) as response:
        if not response.geturl().startswith('https://learn.chatgpt.com/'):
            raise ValueError('O changelog redirecionou para uma origem inesperada.')
        content = response.read(2_000_000).decode('utf-8')
    from html.parser import HTMLParser
    class Headings(HTMLParser):
        def __init__(self):
            super().__init__(); self.active = False; self.parts = []
        def handle_starttag(self, tag, attrs):
            if tag in {'h1', 'h2', 'h3', 'h4'}:
                self.active = True; self.parts.append('\n')
        def handle_endtag(self, tag):
            if tag in {'h1', 'h2', 'h3', 'h4'}:
                self.active = False; self.parts.append('\n')
        def handle_data(self, data):
            if self.active:
                self.parts.append(data)
    parser = Headings(); parser.feed(content)
    versions = [tuple(map(int, m)) for m in re.findall(
        r'Codex CLI\s+(\d+)\.(\d+)\.(\d+)(?![\d.\-])', ''.join(parser.parts))]
    if not versions:
        raise ValueError('Não foi possível identificar uma versão estável no changelog oficial.')
    return max(versions)
