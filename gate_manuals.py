"""Single, editable manual source per language, also bundled in desktop builds."""
from pathlib import Path

MANUAL_ROOT = Path(__file__).resolve().parent / 'docs' / 'manual'
MANUALS = {language: (MANUAL_ROOT / f'{language}.md').read_text(encoding='utf-8')
           for language in ('pt-BR', 'en', 'es')}
