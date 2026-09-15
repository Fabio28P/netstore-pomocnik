"""NetStore Pomocnik — lokalny panel Allegro, Python 3.10+, bez zależności."""
import ai_writer
import parameters
import base64, hashlib, html, json, os, re, secrets, time, webbrowser
from decimal import Decimal, InvalidOperation
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.parse import urlencode, urlparse, parse_qs
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parent
DATA = Path(os.environ.get('NETSTORE_DATA', str(Path.home() / '.netstore-pomocnik')))
DATA.mkdir(parents=True, exist_ok=True)
try: DATA.chmod(0o700)
except OSError: pass
ORIGIN = 'http://localhost:8000'
CALLBACK = ORIGIN + '/allegro/callback'
UA = 'NetStore-Pomocnik/1.3 (+https://github.com/Fabio28P/netstore-pomocnik)'
CSRF = secrets.token_urlsafe(32)
OAUTH = {}
SCOPES = 'allegro:api:sale:offers:read allegro:api:sale:offers:write allegro:api:sale:settings:read'

def read(name, default=None):
    p = DATA / (name + '.json')
    return json.loads(p.read_text('utf-8')) if p.exists() else default

def save(name, value):
    p = DATA / (name + '.json')
    tmp = p.with_suffix('.tmp')
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as f: json.dump(value, f, ensure_ascii=False)
    tmp.replace(p)

def env():
    return read('config', {}).get('environment', 'production')

def hosts():
    suffix = '.allegrosandbox.pl' if env() == 'sandbox' else ''
    return 'https://allegro.pl' + suffix, 'https://api.allegro.pl' + suffix

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Allegro zwróciło nieoczekiwane przekierowanie. Żądanie przerwano.')

def request(url, method='GET', body=None, headers=None):
    h = {'User-Agent': UA, 'Accept': 'application/vnd.allegro.public.v1+json'}
    h.update(headers or {})
    if isinstance(body, dict):
        body = json.dumps(body).encode(); h['Content-Type'] = 'application/vnd.allegro.public.v1+json'
    try:
        with build_opener(NoRedirect).open(Request(url, data=body, method=method, headers=h), timeout=40) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except HTTPError as e:
        try:
            data = json.loads(e.read())
            errors = data.get('errors', [])
            message = '; '.join(str(x.get('userMessage') or x.get('message') or x.get('code')) for x in errors)
            message = message or data.get('error_description') or data.get('error') or 'Błąd API'
        except Exception: message = 'Błąd API'
        raise ValueError(f'Allegro HTTP {e.code}: {message}') from None
    except (URLError, TimeoutError):
        raise ValueError('Brak odpowiedzi Allegro. Sprawdź połączenie. Przy zapisie najpierw sprawdź status, aby nie utworzyć duplikatu.') from None

def token(form):
    c = read('config', {})
    if not c.get('client_id') or not c.get('client_secret'): raise ValueError('Najpierw zapisz Client ID i Client Secret.')
    auth = base64.b64encode((c['client_id'] + ':' + c['client_secret']).encode()).decode()
    t = request(hosts()[0] + '/auth/oauth/token', 'POST', urlencode(form).encode(),
                {'Authorization': 'Basic ' + auth, 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'})
    t['expires_at'] = time.time() + t['expires_in'] - 90
    save('tokens-' + env(), t)
    return t

def api(path, method='GET', body=None, raw_type=None):
    t = read('tokens-' + env(), {})
    if not t: raise ValueError('Kliknij „Połącz z Allegro”.')
    if time.time() >= t.get('expires_at', 0):
        t = token({'grant_type': 'refresh_token', 'refresh_token': t['refresh_token']})
    headers = {'Authorization': 'Bearer ' + t['access_token']}
    if raw_type: headers['Content-Type'] = raw_type
    base = ('https://upload.allegro.pl' + ('.allegrosandbox.pl' if env() == 'sandbox' else '')) if path.startswith('/sale/images') else hosts()[1]
    return request(base + path, method, body, headers)

def offer_id(value):
    match = re.search(r'(\d{6,})(?:[/?#].*)?$', str(value).strip())
    if not match: raise ValueError('Podaj numer lub link do oferty.')
    return match.group(1)

def rich_text(text):
    def inline(value):
        return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', html.escape(value))
    result=[]; in_list=False
    for line in text.splitlines():
        if line.startswith('- '):
            if not in_list: result.append('<ul>'); in_list=True
            result.append('<li>'+inline(line[2:])+'</li>')
        else:
            if in_list:result.append('</ul>');in_list=False
            if line.strip():result.append('<p>'+inline(line)+'</p>')
    if in_list:result.append('</ul>')
    return ''.join(result)

def ai_config():
    c=read('ai-config', {})
    if not c:return {'provider':'gemini','model':'gemini-2.5-flash-lite','profile':ai_writer.DEFAULT_PROFILE}
    return c

def parameter_definitions(category):
    if not str(category).isdigit():raise ValueError('Wczytaj kategorię oferty.')
    offer=api('/sale/categories/'+str(category)+'/parameters').get('parameters',[])
    product=api('/sale/categories/'+str(category)+'/product-parameters').get('parameters',[])
    return parameters.merge(offer,product)

def description(sections, images):
    result = []; used=set()
    for i, section in enumerate(sections):
        title, text = str(section.get('title', '')).strip(), str(section.get('text', '')).strip()
        if not text: continue
        content = ('<h2>' + html.escape(title) + '</h2>' if title else '')
        content += rich_text(text)
        # Allegro supports p, h1, h2, ul, ol, li and b, not br.
        content = content.replace('<br>', '</p><p>')
        items = [{'type': 'TEXT', 'content': content}]
        idx=section.get('image_index', i if i<len(images) else -1)
        if type(idx)==int and 0<=idx<len(images) and idx not in used:
            used.add(idx)
            picture = {'type': 'IMAGE', 'url': images[idx]}
            items = [picture] + items if i % 2 == 0 else items + [picture]
        result.append({'items': items})
    if not result: raise ValueError('Dodaj co najmniej jedną sekcję opisu.')
    remaining=[{'type':'IMAGE','url':url} for idx,url in enumerate(images) if idx not in used]
    for pos in range(0,len(remaining),2):result.append({'items':remaining[pos:pos+2]})
    return {'sections': result}

def validate(d):
    name = str(d.get('name', '')).strip()
    if not 12 <= len(name) <= 75: raise ValueError('Tytuł musi mieć od 12 do 75 znaków.')
    try:
        price = Decimal(str(d.get('price', '')).replace(',', '.'))
        stock = int(d.get('stock', 0))
        if not price.is_finite() or price <= 0 or price != price.quantize(Decimal('.01')) or stock < 1: raise ValueError()
    except (ValueError, InvalidOperation): raise ValueError('Podaj dodatnią cenę (maks. 2 miejsca po przecinku) i całkowitą liczbę sztuk.')
    return name, format(price, '.2f'), stock

LOCATION_FIELDS = ('countryCode', 'province', 'postCode', 'city')

def shipping_location(d):
    source = d.get('shipping_location', read('shipping-default', {}))
    if not isinstance(source, dict): raise ValueError('Uzupełnij miejsce wysyłki.')
    location = {key: str(source.get(key, '')).strip() for key in LOCATION_FIELDS}
    if not all(location.values()): raise ValueError('Uzupełnij kraj, województwo, kod pocztowy i miejscowość wysyłki.')
    if location['countryCode'] != 'PL' or not re.fullmatch(r'\d{2}-\d{3}', location['postCode']):
        raise ValueError('Wybierz Polskę i podaj kod pocztowy w formacie XX-XXX.')
    return location

def build_payload(d, template, images):
    name, price, stock = validate(d)
    if not images: raise ValueError('Dodaj zdjęcie produktu.')
    category = str(d.get('category', '')).strip()
    if not category.isdigit(): raise ValueError('Wczytaj kategorię ze wzoru lub wpisz jej numer.')
    product = {'id': d['product_id']} if d.get('product_id') else {
        'name': name, 'category': {'id': category}, 'images': images, 'parameters': d.get('product_parameters', [])}
    item = {'product': product, 'quantity': {'value': 1}}
    if d.get('producer_id'): item['responsibleProducer'] = {'type': 'ID', 'id': d['producer_id']}
    if d.get('safety', '').strip(): item['safetyInformation'] = {'type': 'TEXT', 'description': d['safety'].strip()}
    payload = {'name': name, 'language': 'pl-PL', 'category': {'id': category}, 'productSet': [item],
        'parameters': d.get('offer_parameters', []), 'images': images, 'description': description(d['sections'], images),
        'sellingMode': {'format': 'BUY_NOW', 'price': {'amount': price, 'currency': 'PLN'}},
        'stock': {'available': stock, 'unit': 'UNIT'}, 'publication': {'status': 'INACTIVE'},
        'external': {'id': d['local_id']}}
    # Only seller settings, never the source product, its images or parameters.
    for key in ('afterSalesServices', 'payments'):
        if template.get(key): payload[key] = template[key]
    payload['location'] = shipping_location(d)
    rates = template.get('delivery', {}).get('shippingRates')
    if not rates or not rates.get('id'): raise ValueError('Najpierw pobierz cennik dostawy z oferty wzorcowej.')
    payload['delivery'] = {'shippingRates': {'id': rates['id']}, 'handlingTime': 'P1D'}
    return payload

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass  # Never log OAuth query strings.
    def send(self, data, status=200, mime='application/json'):
        body = json.dumps(data, ensure_ascii=False).encode() if mime == 'application/json' else data.encode() if isinstance(data, str) else data
        self.send_response(status)
        self.send_header('Content-Type', mime + ('; charset=utf-8' if mime.startswith('text/') else ''))
        self.send_header('Cache-Control', 'no-store'); self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; img-src 'self' data: blob: https://a.allegroimg.com; style-src 'self' 'unsafe-inline'; script-src 'self'; frame-ancestors 'none'")
        self.end_headers(); self.wfile.write(body)
    def host_ok(self): return self.headers.get('Host') == 'localhost:8000'
    def do_GET(self):
        if not self.host_ok(): return self.send({'error': 'Nieprawidłowy adres. Otwórz http://localhost:8000'}, 403)
        p = urlparse(self.path)
        try:
            if p.path == '/': return self.send((ROOT / 'index.html').read_text('utf-8'), mime='text/html')
            if p.path == '/messages.js': return self.send((ROOT / 'messages.js').read_text('utf-8'), mime='text/javascript')
            if p.path == '/app.js': return self.send((ROOT / 'app.js').read_text('utf-8'), mime='text/javascript')
            if p.path == '/state':
                c = read('config', {})
                return self.send({'csrf': CSRF, 'environment': env(), 'client_id': c.get('client_id', ''),
                    'has_secret': bool(c.get('client_secret')), 'ai': {'provider': ai_config().get('provider','openai'), 'has_key': bool(ai_config().get('api_key')), 'model': ai_config().get('model', 'gpt-4.1-mini'), 'recommended_profile':ai_writer.DEFAULT_PROFILE, 'profile': ai_config().get('profile', ai_writer.DEFAULT_PROFILE)}, 'connected': bool(read('tokens-' + env())),
                    'shipping_default': read('shipping-default', {}), 'draft': read('draft', None), 'saved_offer': read('offer-' + env(), {}), 'callback': CALLBACK})
            if p.path == '/allegro/callback':
                q = parse_qs(p.query)
                state = q.get('state', [''])[0]
                if not OAUTH or not secrets.compare_digest(state, OAUTH.get('state', '')) or time.time() > OAUTH.get('expires', 0):
                    raise ValueError('Nieprawidłowa lub wygasła sesja logowania. Spróbuj ponownie.')
                verifier = OAUTH.pop('verifier'); OAUTH.clear()
                if 'error' in q: raise ValueError('Logowanie anulowane. Wróć do programu i spróbuj ponownie.')
                token({'grant_type': 'authorization_code', 'code': q.get('code', [''])[0], 'redirect_uri': CALLBACK, 'code_verifier': verifier})
                self.send_response(303); self.send_header('Location', '/'); self.end_headers(); return
            return self.send({'error': 'Nie znaleziono'}, 404)
        except ValueError as e: return self.send(html.escape(str(e)) + ' — wróć do http://localhost:8000', 400, 'text/plain')
    def do_POST(self):
        if not self.host_ok() or self.headers.get('Origin') != ORIGIN or not secrets.compare_digest(self.headers.get('X-CSRF', ''), CSRF):
            return self.send({'error': 'Odśwież stronę programu.'}, 403)
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 45_000_000: raise ValueError('Za duże żądanie (limit 45 MB).')
            d = json.loads(self.rfile.read(length))
            self.send(self.action(urlparse(self.path).path, d))
        except (ValueError, KeyError, TypeError) as e: self.send({'error': str(e)}, 400)
        except Exception: self.send({'error': 'Nie udało się wykonać operacji. Sprawdź dane i uruchom program ponownie.'}, 500)
    def action(self, path, d):
        if path == '/shipping-default':
            location = shipping_location(d)
            save('shipping-default', location)
            return {'location': location, 'message': 'Zapisano domyślne miejsce wysyłki na tym komputerze.'}
        if path == '/ai-config':
            old = read('ai-config', {})
            provider=d.get('provider','openai')
            if provider not in ('openai','gemini'):raise ValueError('Wybierz dostawcę AI.')
            key = str(d.get('api_key', '')).strip() or (old.get('api_key', '') if provider==old.get('provider','openai') else '')
            model = str(d.get('model', 'gpt-4.1-mini')).strip()
            profile = str(d.get('profile', ai_writer.DEFAULT_PROFILE)).strip()
            if not re.fullmatch(r'[A-Za-z0-9._:-]{1,100}', model): raise ValueError('Nieprawidłowa nazwa modelu.')
            if len(profile) > 8000 or len(key) > 1000: raise ValueError('Zbyt długie dane konfiguracji.')
            save('ai-config', {'provider':provider, 'api_key': key, 'model': model, 'profile': profile})
            return {'message': 'Zapisano ustawienia generatora na tym komputerze.'}
        if path == '/ai-remove-key':
            c = read('ai-config', {}); c.pop('api_key', None); save('ai-config', c)
            return {'message': 'Usunięto lokalny klucz OpenAI.'}
        if path == '/ai-generate':
            return ai_writer.generate(ai_config(), d.get('facts', ''), d.get('images', []))
        if path == '/configure':
            old = read('config', {})
            secret = str(d.get('client_secret', '')).strip() or old.get('client_secret', '')
            cid = str(d.get('client_id', '')).strip()
            if not cid or not secret: raise ValueError('Wpisz Client ID i Client Secret z panelu Allegro.')
            if d.get('environment') not in ('production', 'sandbox'): raise ValueError('Wybierz środowisko.')
            if cid != old.get('client_id') or secret != old.get('client_secret'):
                for name in ('tokens-production', 'tokens-sandbox'): (DATA / (name + '.json')).unlink(missing_ok=True)
            save('config', {'client_id': cid, 'client_secret': secret, 'environment': d['environment']})
            OAUTH.clear()
            return {'message': 'Konfiguracja zapisana na tym komputerze.'}
        if path == '/connect':
            c = read('config', {})
            if not c.get('client_secret'): raise ValueError('Najpierw zapisz konfigurację.')
            v = secrets.token_urlsafe(64); state = secrets.token_urlsafe(32)
            OAUTH.update(state=state, verifier=v, expires=time.time()+600)
            challenge = base64.urlsafe_b64encode(hashlib.sha256(v.encode()).digest()).rstrip(b'=').decode()
            return {'url': hosts()[0] + '/auth/oauth/authorize?' + urlencode({'response_type': 'code', 'client_id': c['client_id'],
                'redirect_uri': CALLBACK, 'scope': SCOPES, 'state': state, 'code_challenge': challenge, 'code_challenge_method': 'S256', 'prompt': 'confirm'})}
        if path == '/disconnect':
            (DATA / ('tokens-' + env() + '.json')).unlink(missing_ok=True)
            return {'message': 'Usunięto lokalne tokeny. Upoważnienie możesz odwołać także w ustawieniach Allegro.'}
        if path == '/switch-folder':
            folder=str(d.get('folder','')).strip()
            if not folder or len(folder)>500:raise ValueError('Wybierz folder produktu.')
            current=read('draft',{})
            if current:
                key=hashlib.sha256(str(current.get('folder','previous')).encode()).hexdigest()
                save('folder-'+key, {'draft':current,'offers':{e:read('offer-'+e,{}) for e in ('production','sandbox')}})
            key=hashlib.sha256(folder.encode()).hexdigest()
            target=read('folder-'+key,{})
            new=target.get('draft') or d['draft']
            new['folder']=folder
            save('draft',new)
            for e in ('production','sandbox'):save('offer-'+e,target.get('offers',{}).get(e,{}))
            return {'draft':new,'saved_offer':read('offer-'+env(),{})}
        if path == '/save':
            save('draft', d); return {'message': 'Zapisano szkic na komputerze.'}
        if path == '/template':
            source = api('/sale/product-offers/' + offer_id(d['reference']))
            template = {k: source[k] for k in ('delivery','afterSalesServices','location','payments') if source.get(k)}
            template['source_id'] = source['id']; save('template-' + env(), template)
            return {'template': template, 'category': source.get('category', {}).get('id'), 'name': source.get('name')}
        if path == '/parameters':
            if not str(d['category']).isdigit(): raise ValueError('Nieprawidłowy numer kategorii.')
            return {'parameters':parameter_definitions(d['category'])}
        if path == '/products': return api('/sale/products?' + urlencode({'phrase': d['phrase'], 'category.id': d['category']}))
        if path == '/producers': return api('/sale/responsible-producers?limit=100')
        if path == '/status':
            saved = read('offer-' + env(), {})
            if not saved.get('id'):
                if not saved.get('local_id'): raise ValueError('Nie zapisano jeszcze oferty w Allegro.')
                found = api('/sale/offers?' + urlencode({'external.id': saved['local_id']})).get('offers', [])
                if len(found) != 1: raise ValueError('Nie znaleziono jednoznacznie oferty. Sprawdź Moje oferty w Allegro przed kolejnym zapisem.')
                saved['id'] = found[0]['id']; save('offer-' + env(), saved)
            result = api('/sale/product-offers/' + saved['id'])
            saved['pending'] = False; save('offer-' + env(), saved)
            return {'id': saved['id'], 'publication': result.get('publication'), 'validation': result.get('validation'), 'message': 'Pobrano aktualny status.'}
        if path in ('/draft', '/publish'):
            saved = read('offer-' + env(), {})
            if path == '/publish':
                if not saved.get('id') or not d.get('confirm') or saved.get('pending') or not saved.get('confirmed'): raise ValueError('Najpierw zapisz szkic w Allegro i potwierdź publikację.')
                if saved.get('hash') != hashlib.sha256(json.dumps(d['draft'], sort_keys=True).encode()).hexdigest():
                    raise ValueError('Treść zmieniła się od zapisu. Najpierw ponownie zapisz szkic w Allegro.')
                result = api('/sale/product-offers/' + saved['id'], 'PATCH', {'publication': {'status': 'ACTIVE'}})
                return {'id': saved['id'], 'publication': result.get('publication'), 'message': 'Zlecono publikację. Kliknij „Sprawdź status”, aby potwierdzić wynik.'}
            original_hash=hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
            draft = json.loads(json.dumps(d))
            validate(draft)
            shipping_location(draft)
            if saved.get('pending'): raise ValueError('Poprzedni zapis ma nieznany wynik. Kliknij „Sprawdź status” przed kolejnym zapisem.')
            if saved.get('id'):
                current = api('/sale/product-offers/' + saved['id'])
                if current.get('publication', {}).get('status') != 'INACTIVE': raise ValueError('Ta oferta nie jest szkicem. Edycja aktywnej oferty jest zablokowana w tej wersji.')
            parameters.normalize(draft, parameter_definitions(draft.get('category','')))
            uploaded = []
            for item in draft.get('images', []):
                match = re.fullmatch(r'data:(image/(?:png|jpeg));base64,([A-Za-z0-9+/=\r\n]+)', item)
                if not match: raise ValueError('Obsługiwane są zdjęcia PNG i JPG.')
                raw = base64.b64decode(match.group(2), validate=True)
                if len(raw) > 10_000_000: raise ValueError('Zdjęcie przekracza 10 MB.')
                if not (raw.startswith(b'\x89PNG\r\n\x1a\n') or raw.startswith(b'\xff\xd8\xff')): raise ValueError('Plik nie jest zdjęciem PNG/JPG.')
                uploaded.append(api('/sale/images', 'POST', raw, match.group(1))['location'])
            payload = build_payload(draft, read('template-' + env(), {}), uploaded)
            fingerprint = original_hash
            if saved.get('local_id') and saved['local_id'] != draft['local_id']: raise ValueError('Najpierw zakończ pracę z bieżącą ofertą.')
            state = {'local_id': draft['local_id'], 'pending': True, 'id': saved.get('id'), 'hash': fingerprint, 'confirmed': False}
            save('offer-' + env(), state)
            try:
                result = api('/sale/product-offers' + ('/' + saved['id'] if saved.get('id') else ''), 'PATCH' if saved.get('id') else 'POST', payload)
            except ValueError as e:
                # Validation failures are definitive. Network/5xx results remain ambiguous.
                if re.search(r'HTTP 4\d\d:', str(e)):
                    state['pending'] = False; save('offer-' + env(), state)
                raise
            state.update(id=result.get('id', saved.get('id')), pending=False, confirmed=True)
            if not state['id']: state['pending'] = True
            save('offer-' + env(), state)
            return {'id': state['id'], 'message': 'Wysłano szkic do Allegro. Nie jest jeszcze opublikowany.', 'validation': result.get('validation')}
        raise ValueError('Nieznana operacja.')

if __name__ == '__main__':
    try: server = HTTPServer(('127.0.0.1', 8000), Handler)
    except OSError:
        print('Port 8000 jest zajęty. Zamknij poprzednie okno programu i spróbuj ponownie.'); raise SystemExit(1)
    print('NetStore Pomocnik: ' + ORIGIN + '\nZostaw to okno otwarte. Ctrl+C kończy program.')
    if not os.environ.get('NETSTORE_NO_BROWSER'): webbrowser.open(ORIGIN)
    try: server.serve_forever()
    except KeyboardInterrupt: server.server_close()
