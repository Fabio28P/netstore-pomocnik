"""Read-only offer reconciliation. Never infer product identity from names."""
import hashlib
from urllib.parse import urlencode

def key(folder):
    if not isinstance(folder,str) or not folder.strip() or len(folder)>500:
        raise ValueError('Nieprawidłowy folder produktu.')
    return 'folder-'+hashlib.sha256(folder.encode()).hexdigest()

def inventory(api):
    offers=[]
    for offset in range(0,10000,1000):
        page=api('/sale/offers?'+urlencode({'limit':1000,'offset':offset})).get('offers',[])
        offers.extend(page)
        if len(page)<1000:return offers
    raise ValueError('Lista ofert jest zbyt duża do pełnego sprawdzenia. Nie uruchomiono kolejki.')

def scan(folders,api,read,environment):
    if not isinstance(folders,list) or len(folders)>200:raise ValueError('Wybierz maksymalnie 200 folderów.')
    offers=inventory(api); current=read('draft',{}) or {}; links=read('queue-links-'+environment,{})
    rows=[]; choices=read('queue-choices-'+environment,{})
    for folder in folders:
        stored=read(key(folder),{})
        draft=stored.get('draft',{})
        saved=stored.get('offers',{}).get(environment,{})
        if current.get('folder')==folder:
            draft=current;saved=read('offer-'+environment,{})
        identifier=saved.get('id') or links.get(folder)
        matches=[o for o in offers if (identifier and o['id']==identifier) or
                 (draft.get('local_id') and (o.get('external') or {}).get('id')==draft['local_id'])]
        if len(matches)>1:status='ambiguous'
        elif matches:status=matches[0].get('publication',{}).get('status','UNKNOWN')
        elif identifier or saved.get('pending'):status='unknown'
        else:status='unlinked'
        rows.append({'folder':folder,'status':status,'offers':[{'id':o['id'],'name':o.get('name','')} for o in matches],
                     'isNew':bool(choices.get(folder)) if status=='unlinked' else False, 'has_facts':bool(str(draft.get('ai_facts','')).strip()), 'prepared':bool(draft.get('sections'))})
    return {'rows':rows,'offers':[{'id':o['id'],'name':o.get('name',''),'status':o.get('publication',{}).get('status','UNKNOWN')} for o in offers]}

def merge_import(stored, incoming):
    """Fill missing input from newly selected files without losing offer identity or edits."""
    if not stored:return incoming
    merged=dict(stored)
    if not str(merged.get('ai_facts','')).strip() and str(incoming.get('ai_facts','')).strip():
        merged['ai_facts']=incoming['ai_facts']
    if not merged.get('sections') and incoming.get('sections'):
        merged['sections']=incoming['sections']
    if not merged.get('images') and incoming.get('images'):
        merged['images']=incoming['images']
    return merged
