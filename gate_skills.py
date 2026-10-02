"""Full YAML metadata parsing, with bounded input and stable domain fields."""
import re
import unicodedata
import yaml


def skill_profile(path, text):
    if len(text) > 2_000_000:
        return None
    match = re.match(r'^---\s*\n(.*?)\n---(?:\s*\n|$)', text, re.S)
    if not match:
        return None
    try:
        fields = yaml.safe_load(match.group(1))
    except (yaml.YAMLError, RecursionError):
        return None
    if not isinstance(fields, dict) or not all(isinstance(fields.get(k), str) and fields[k].strip() for k in ('name','description')):
        return None
    outcomes = fields.get('gate_outcomes', '')
    if isinstance(outcomes, list):
        outcomes = ','.join(str(x) for x in outcomes)
    if not isinstance(outcomes, str):
        return None
    headings = [re.sub(r'^#{1,3}\s+', '', line).strip() for line in text.splitlines() if re.match(r'^#{1,3}\s+', line)]
    profile_text = ' '.join((fields['name'], fields['description'], ' '.join(headings[:16])))
    normalized = ''.join(c for c in unicodedata.normalize('NFD', profile_text.casefold()) if unicodedata.category(c) != 'Mn')
    words = sorted(set(re.findall(r'[a-z0-9-]{3,}', normalized)))
    return {'name': fields['name'].strip(), 'description': fields['description'].strip(),
            'gate_outcomes': outcomes, 'path': str(path), 'headings': ' | '.join(headings[:16]),
            'scope': text[match.end():].strip()[:6000],
            'keywords': ' '.join(words[:160])}
