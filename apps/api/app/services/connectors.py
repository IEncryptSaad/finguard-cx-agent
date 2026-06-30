import os
from datetime import datetime, timezone
from app.services.audit import log_event

_CONNECTORS = {
    'webhook': {'required_env': 'WEBHOOK_URL', 'capabilities': ['receive','send','test']},
    'email': {'required_env': 'SMTP_HOST', 'capabilities': ['inbound_foundation','outbound_foundation','test']},
    'slack': {'required_env': 'SLACK_BOT_TOKEN', 'capabilities': ['messages','notifications','test']},
    'notion': {'required_env': 'NOTION_API_KEY', 'capabilities': ['pages','search','test']},
    'google_drive': {'required_env': 'GOOGLE_DRIVE_CREDENTIALS', 'capabilities': ['documents','search','test']},
    'confluence': {'required_env': 'CONFLUENCE_API_TOKEN', 'capabilities': ['spaces','pages','test']},
}

def _now(): return datetime.now(timezone.utc).isoformat()

def connector_catalog():
    items=[]
    for name,cfg in _CONNECTORS.items():
        enabled=bool(os.getenv(cfg['required_env']))
        items.append({'name':name,'enabled':enabled,'status':'ok' if enabled else 'disabled','required_env':cfg['required_env'],'capabilities':cfg['capabilities'],'free_tier_mode':not enabled,'last_checked_at':_now()})
    return items

def connector_health(name:str):
    cfg=_CONNECTORS.get(name)
    if not cfg: return {'name':name,'healthy':False,'status':'unknown','reason':'Connector is not registered'}
    enabled=bool(os.getenv(cfg['required_env']))
    return {'name':name,'healthy':enabled or True,'status':'configured' if enabled else 'demo_mode','enabled':enabled,'reason':None if enabled else f'Set {cfg["required_env"]} to enable real transport','capabilities':cfg['capabilities']}

def test_connector(name:str, payload:dict|None=None):
    health=connector_health(name)
    status='succeeded' if health['status'] in ('configured','demo_mode') else 'failed'
    result={'connector':name,'status':status,'demo':not health.get('enabled',False),'echo':payload or {},'checked_at':_now()}
    log_event('connector.tested', result)
    return result
