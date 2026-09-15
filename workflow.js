'use strict';
async function categoryLabel(){if(!$('category').value)return;const c=await call('/category',{id:$('category').value});draft.category_name=c.name;$('chosen-category').textContent='Wybrano: '+c.name;}
async function chooseCategory(c){
 const detail=await call('/category',{id:c.id});
 if(!detail.leaf){await browseCategories(c.id);return;}
 if(draft.category!==c.id){draft.product_parameters=[];draft.offer_parameters=[];draft.product_id='';parameters=[];$('parameters').replaceChildren();$('product-id').replaceChildren(new Option('Nowy produkt',''));}
 $('category').value=c.id;draft.category=c.id;draft.category_name=detail.name;$('chosen-category').textContent='Wybrano: '+detail.name;
 $('category-results').replaceChildren();await loadParameters();await call('/save',collect());
}
function categoryButtons(items){$('category-results').replaceChildren();if(!items.length)$('category-results').append(el('p','Brak wyników. Spróbuj innej nazwy lub przeglądaj działy.'));for(const item of items){const c=item.category||item;const label=(Array.isArray(c.path)?c.path.map(x=>x.name).join(' → ')+' → ':'')+c.name;const b=el('button',label,'secondary');b.style.margin='5px';b.onclick=async()=>{if(busy)return;busy=true;try{await chooseCategory(c);}catch(e){notice(e.message,true);}finally{busy=false;}};$('category-results').append(b);}}
async function browseCategories(parent=''){const r=await call('/categories-list',{parent});categoryButtons(r.categories||[]);if(parent){const b=el('button','Wróć do wszystkich działów','secondary');b.onclick=()=>{if(!busy)browseCategories().catch(e=>notice(e.message,true));};$('category-results').prepend(b);}}
action('search-categories',async()=>{const r=await call('/categories-search',{name:$('category-query').value||$('name').value});categoryButtons(r.matchingCategories||[]);});
action('browse-categories',()=>browseCategories());
let queueRows=[],queueOffers=[];
function resetQueue(){queueRows=[];queueOffers=[];$('queue-items').replaceChildren();$('queue-progress').textContent='';}
const queueLabels={ACTIVE:'Już wystawiony — pomijam',ACTIVATING:'Publikacja w toku — pomijam',INACTIVE:'Szkic w Allegro — pomijam',ENDED:'Oferta zakończona — sprawdź w Allegro',unknown:'Niepewny stan — sprawdź ofertę',ambiguous:'Kilka ofert — sprawdź powiązanie',unlinked:'Brak powiązania — sprawdź czy to nowy produkt'};
function drawQueue(){
 $('queue-items').replaceChildren();
 for(const row of queueRows){const box=el('div',undefined,'section-editor');box.append(el('strong',row.folder.split('/').pop()),el('p',row.message||queueLabels[row.status]||'Stan wymaga sprawdzenia'));
 for(const o of row.offers||[])box.append(el('p',o.name+' · '+o.id));
 if(row.status==='unlinked'){
 const label=el('label'),check=el('input');check.type='checkbox';check.style.width='auto';check.checked=!!row.isNew;check.onchange=()=>row.isNew=check.checked;label.append(check,document.createTextNode(' Sprawdziłem: to nowy produkt, przygotuj opis'));box.append(label);
 const select=el('select');select.setAttribute('aria-label','Istniejąca oferta dla '+row.folder);select.append(new Option('Lub wybierz istniejącą ofertę…',''));for(const o of queueOffers)select.append(new Option(o.name+' · '+o.id+' · '+o.status,o.id));
 const link=el('button','Powiąż z ofertą','secondary');link.onclick=async()=>{if(busy)return;if(!select.value)return notice('Wybierz ofertę z listy.',true);busy=true;try{await call('/queue-link',{folder:row.folder,id:select.value});const o=queueOffers.find(o=>o.id===select.value);row.status=o.status;row.offers=[o];row.isNew=false;drawQueue();}catch(e){notice(e.message,true);}finally{busy=false;}};box.append(select,link);
 }
 if(row.prepared||row.status==='unlinked'||row.status==='INACTIVE'){
 const open=el('button',row.prepared?'Otwórz przygotowany szkic':'Otwórz produkt','secondary');open.onclick=async()=>{if(busy)return;busy=true;try{await importFolder(row.folder);$('folder-choice').value=row.folder;if(draft.ai_questions?.length)notice('Do sprawdzenia: '+draft.ai_questions.join(' '));$('name').scrollIntoView({behavior:'smooth'});}catch(e){notice(e.message,true);}finally{busy=false;}};box.append(open);
 }
 $('queue-items').append(box);
 }
}
async function scanQueue(){if(!folderGroups.size)throw Error('Najpierw wybierz folder z produktami.');await call('/save',collect());const r=await call('/queue-scan',{folders:[...folderGroups.keys()]});const previous=new Map(queueRows.map(r=>[r.folder,r]));queueRows=r.rows.map(r=>({...r,isNew:previous.get(r.folder)?.isNew||false}));queueOffers=r.offers;drawQueue();$('queue-progress').textContent='Sprawdzono '+queueRows.length+' produktów. Zaznacz nowe produkty bez powiązania.';}
action('scan-queue',scanQueue);
action('run-queue',async()=>{
 if(!$('queue-enabled').checked)throw Error('Włącz automatyczne przygotowanie opisów.');
 if(!queueRows.length)throw Error('Najpierw sprawdź foldery na Allegro i oznacz nowe produkty.');
 await scanQueue(); // Refresh live states immediately before preparing the batch.
 const pending=queueRows.filter(r=>r.status==='unlinked'&&r.isNew&&!r.prepared);
 if(!pending.length)return notice('Brak nowych produktów do przygotowania. Istniejące szkice otworzysz na liście.');
 const frozen=[...document.querySelectorAll('input,select,textarea')].filter(n=>n.id!=='queue-enabled').map(n=>[n,n.disabled]);for(const [n]of frozen)n.disabled=true;
 let done=0;
 try{
 for(const row of pending){
 if(!$('queue-enabled').checked)break;
 $('queue-progress').textContent='Przygotowuję '+(done+1)+' / '+pending.length+': '+row.folder;
 try{
 await importFolder(row.folder);
 for(const n of document.querySelectorAll('input,select,textarea'))if(n.id!=='queue-enabled')n.disabled=true;
 if(!$('queue-enabled').checked)break;
 if(!draft.ai_facts.trim()){row.message='Uzupełnij fakty o produkcie lub dodaj opis.txt. Nie wygenerowano opisu.';drawQueue();continue;}
 const proposal=await call('/ai-generate',{facts:draft.ai_facts,images:$('ai-use-images').checked?await compactImages(draft.images):[]});
 draft.name=proposal.name;draft.sections=proposal.sections;draft.ai_questions=proposal.questions||[];
 if(!$('ai-use-images').checked)spreadImages(draft.sections,draft.images.length);
 fill();await call('/save',collect());row.prepared=true;row.message='Opis gotowy do sprawdzenia. Uzupełnij kategorię, parametry, cenę i ilość, jeśli ich brakuje.';done++;
 }catch(e){row.message='Zatrzymano: '+e.message;drawQueue();throw e;}
 drawQueue();for(const n of $('queue-items').querySelectorAll('input,select,button'))n.disabled=true;
 }
 }finally{for(const n of document.querySelectorAll('input,select,textarea'))n.disabled=false;for(const [n,disabled]of frozen)n.disabled=disabled;drawQueue();$('queue-progress').textContent='Przygotowano '+done+' opisów. '+(!$('queue-enabled').checked?'Kolejka zatrzymana. ':'')+'Otwórz szkic, sprawdź dane i zatwierdź publikację.';}
});
