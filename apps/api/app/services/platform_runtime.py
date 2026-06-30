from datetime import datetime, timezone
from app.agent.llm import provider_catalog
from app.services.audit import events
from app.services.workflows import execution_history

def _now(): return datetime.now(timezone.utc).isoformat()

def platform_health() -> dict:
    providers = provider_catalog()
    recent = events()[-100:]
    failures = [e for e in recent if 'failed' in e['event_type'] or e.get('payload',{}).get('status') == 'failed']
    return {
        'status': 'ok' if any(p['name'] == 'mock' and p['enabled'] for p in providers) else 'degraded',
        'checked_at': _now(),
        'providers': providers,
        'persistence': __import__('app.services.repository', fromlist=['active_backend']).active_backend(),
        'metrics': {
            'recent_events': len(recent),
            'recent_failures': len(failures),
            'workflow_executions': len(execution_history()),
        }
    }

def cost_usage() -> dict:
    usage = {}
    for e in events():
        if e['event_type'] == 'ai.provider_used':
            p = e['payload'].get('provider', 'unknown')
            usage.setdefault(p, {'requests': 0, 'estimated_tokens': 0})
            usage[p]['requests'] += 1
            usage[p]['estimated_tokens'] += int(e['payload'].get('estimated_tokens', 0) or 0)
    return {'currency': 'USD', 'estimated_cost': 0, 'providers': usage, 'billing_ready': False}
