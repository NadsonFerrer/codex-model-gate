"""Usage parsing and per-turn aggregation independent of Tk widgets."""
from __future__ import annotations

import json

KEYS = ('input', 'cached_input', 'output', 'reasoning')


def parse_usage(raw: str) -> dict[str, int] | None:
    turns = []
    cumulative = None
    fallback = []

    def normalize(value):
        if not isinstance(value, dict):
            return None
        aliases = {'input_tokens': 'input', 'prompt_tokens': 'input',
                   'cached_input_tokens': 'cached_input', 'output_tokens': 'output',
                   'completion_tokens': 'output', 'reasoning_tokens': 'reasoning'}
        result = {k: 0 for k in KEYS}
        found = False
        for name, key in aliases.items():
            child = value.get(name)
            if isinstance(child, int) and not isinstance(child, bool):
                result[key] = max(result[key], max(0, child)); found = True
        for group, field, key in (('input_tokens_details', 'cached_tokens', 'cached_input'),
                                  ('output_tokens_details', 'reasoning_tokens', 'reasoning'),
                                  ('completion_tokens_details', 'reasoning_tokens', 'reasoning')):
            details = value.get(group)
            if isinstance(details, dict) and isinstance(details.get(field), int):
                result[key] = max(0, details[field]); found = True
        return result if found else None

    for line in raw.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        usage = normalize(event.get('usage')) or normalize(event)
        info = event.get('info')
        if isinstance(info, dict):
            cumulative = normalize(info.get('total_token_usage')) or cumulative
            usage = usage or normalize(info.get('last_token_usage'))
        if usage:
            (turns if event.get('type') == 'turn.completed' else fallback).append(usage)
    if cumulative:
        return cumulative
    metrics = turns or fallback[-1:]
    return {k: sum(u[k] for u in metrics) for k in KEYS} if metrics else None


def usage_records(records):
    """Yield one dated record per turn; old records retain their available total."""
    for record in records:
        if record.get('model_key') == 'sol' and not record.get('model_id'):
            record = {**record, 'model_key': 'sol6'}
        metrics = record.get('turn_metrics')
        if isinstance(metrics, list) and metrics:
            for metric in metrics:
                if not isinstance(metric, dict):
                    continue
                yield {**record, 'finished_at': metric.get('started_at') or record.get('finished_at'),
                       'token_usage': metric.get('token_usage'),
                       'model_key': metric.get('model_key') or record.get('model_key'),
                       'pricing': metric.get('pricing') or record.get('pricing'),
                       'exchange_rates': metric.get('exchange_rates') or record.get('exchange_rates')}
        else:
            yield record
