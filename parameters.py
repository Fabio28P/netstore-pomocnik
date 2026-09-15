"""Merge offer/product metadata and validate before uploading images."""
def merge(offer, product):
    merged={str(p['id']):dict(p) for p in offer}
    for p in product:
        key=str(p['id']);old=merged.get(key,{})
        merged[key]={**old,**p,'options':{**old.get('options',{}),**p.get('options',{}),'describesProduct':True},
            'requiredForProduct':bool(p.get('required') or p.get('requiredForProduct') or old.get('requiredForProduct')),
            'required':bool(old.get('required'))}
    return list(merged.values())

def normalize(draft, definitions):
    supplied={str(v['id']):v for v in draft.get('product_parameters',[])+draft.get('offer_parameters',[])}
    product=[];offer=[];missing=[]
    for p in definitions:
        pid=str(p['id']); v=supplied.get(pid); is_product=p.get('options',{}).get('describesProduct',False)
        # Existing catalogue products already carry product parameters.
        if is_product and draft.get('product_id'): continue
        required=p.get('required') or (is_product and p.get('requiredForProduct'))
        if not v or not any(v.get(k) for k in ('values','valuesIds','rangeValue')):
            if required:missing.append(p['name'])
            continue
        ids=v.get('valuesIds',[])
        dictionary={str(i['id']) for i in p.get('dictionary',[])}
        if ids and any(str(i) not in dictionary for i in ids):raise ValueError('Wybierz poprawną wartość: '+p['name'])
        ambiguous=str(p.get('options',{}).get('ambiguousValueId',''))
        if ambiguous in ids and p.get('options',{}).get('customValuesEnabled') and not v.get('values'):
            missing.append(p['name']+' — własna wartość')
        (product if is_product else offer).append(v)
    if missing:raise ValueError('Uzupełnij wymagane pola przed wysłaniem: '+', '.join(missing))
    draft['product_parameters']=product;draft['offer_parameters']=offer
