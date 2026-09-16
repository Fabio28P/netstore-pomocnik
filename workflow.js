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
async function rowAction(fn){if(busy)return;busy=true;try{await fn();}catch(e){notice(e.message,true);}finally{busy=false;}}
function showLocalFolders(){queueRows=[...folderGroups.keys()].map(folder=>({folder,status:'unscanned',offers:[]}));drawQueue();$('queue-progress').textContent='Wczytano listę folderów. Kliknij „Sprawdź foldery na Allegro”, aby powiązać je z ofertami.';}
function drawQueue(){
 $('queue-items').replaceChildren();
 for(const row of queueRows){
 const box=el('div',undefined,'section-editor'),files=folderGroups.get(row.folder)||[];
 box.append(el('strong',row.folder.split('/').pop()),el('p',row.message||queueLabels[row.status]||'Nie sprawdzono jeszcze na Allegro'));
 const notes=files.filter(f=>/^(opis|produkt)\.(txt|md)(\.txt)?$/i.test(f.name));
 box.append(el('small',files.filter(f=>/\.(png|jpe?g)$/i.test(f.name)).length+' zdjęć · '+(notes.length?'Plik: '+notes.map(f=>f.name).join(', '):row.has_facts?'Dane produktu zapisane w programie':'Brak opis.txt w wybranym zestawie plików')));
 for(const o of row.offers||[])box.append(el('p','Powiązana oferta: '+o.name+' · '+o.id));
 if(row.status==='unlinked'){
 const search=el('input');search.placeholder='Szukaj swojej aukcji po tytule lub numerze…';search.setAttribute('aria-label','Szukaj oferty dla '+row.folder);
 const select=el('select');select.setAttribute('aria-label','Oferta Allegro dla '+row.folder);
 function options(){select.replaceChildren(new Option('Wybierz z listy…',''),new Option('Nowy produkt — przygotuj nową ofertę','new'));const q=search.value.toLocaleLowerCase('pl');for(const o of queueOffers.filter(o=>(o.name+' '+o.id).toLocaleLowerCase('pl').includes(q)))select.append(new Option(o.name+' · '+o.id+' · '+o.status,o.id));select.value=row.isNew?'new':'';}
 search.oninput=options;options();
 select.onchange=()=>{const choice=select.value;rowAction(async()=>{if(choice==='new'||!choice){await call('/queue-choice',{folder:row.folder,is_new:choice==='new'});row.isNew=choice==='new';row.message=row.isNew?'Nowy produkt — możesz przygotować opis.':'';}else{await call('/queue-link',{folder:row.folder,id:choice});const o=queueOffers.find(o=>o.id===choice);row.status=o.status;row.offers=[o];row.isNew=false;row.message='';}drawQueue();});};
 box.append(search,select);
 if(row.isNew&&!row.prepared){const prepare=el('button','Przygotuj ten produkt');prepare.onclick=()=>rowAction(async()=>{$('queue-enabled').checked=true;await runQueue(row.folder);});box.append(prepare);}
 }
 const buttons=el('div',undefined,'actions');
 const open=el('button',row.prepared?'Otwórz gotowy szkic':'Otwórz produkt','secondary');open.onclick=()=>rowAction(async()=>{await importFolder(row.folder);$('folder-choice').value=row.folder;if(draft.ai_questions?.length)notice('Do sprawdzenia: '+draft.ai_questions.join(' '));$('name').scrollIntoView({behavior:'smooth'});});buttons.append(open);
 const picker=el('input');picker.type='file';picker.accept='.txt,.md';picker.hidden=true;
 const add=el('button','Dodaj opis z pliku','secondary');add.onclick=()=>{if(!busy)picker.click();};picker.onchange=()=>{const file=picker.files[0];if(!file)return;rowAction(async()=>{if(file.size>150000)throw Error('Plik przekracza 150 KB.');const text=(await file.text()).trim();if(!text)throw Error('Wybrany plik jest pusty. Zapisz w nim opis i wybierz go ponownie.');await importFolder(row.folder);const ready=/^gotowy-opis\./i.test(file.name);if(ready){if(draft.sections.length&&!confirm('Zastąpić bieżący opis treścią wybranego pliku?'))return;draft.sections=NetstoreQuick.parseDescription(text);spreadImages(draft.sections,draft.images.length);}else{if(draft.ai_facts.trim()&&!confirm('Zastąpić obecne fakty produktu treścią wybranego pliku?'))return;draft.ai_facts=text;}fill();await call('/save',collect());row.has_facts=!!draft.ai_facts.trim();row.prepared=!!draft.sections.length;row.message='Wczytano '+file.name+' ('+text.length+' znaków).';drawQueue();});};buttons.append(add,picker);box.append(buttons);$('queue-items').append(box);
 }
}
async function scanQueue(){if(!folderGroups.size)throw Error('Najpierw wybierz folder z produktami.');await call('/save',collect());const r=await call('/queue-scan',{folders:[...folderGroups.keys()]});queueRows=r.rows;queueOffers=r.offers;drawQueue();$('queue-progress').textContent='Sprawdzono '+queueRows.length+' produktów. Wybierz przy folderze nowy produkt albo istniejącą aukcję.';}
action('scan-queue',scanQueue);
async function runQueue(onlyFolder=null){
 if(!$('queue-enabled').checked)throw Error('Włącz automatyczne przygotowanie opisów.');
 if(!queueRows.length)throw Error('Najpierw sprawdź foldery na Allegro i oznacz nowe produkty.');
 await scanQueue(); // Refresh live states immediately before preparing the batch.
 const pending=queueRows.filter(r=>(!onlyFolder||r.folder===onlyFolder)&&r.status==='unlinked'&&r.isNew&&!r.prepared);
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
 if(draft.sections.length){row.prepared=true;row.message='Wczytano gotowy opis z folderu — otwórz i sprawdź szkic.';await call('/save',collect());done++;drawQueue();continue;}
 if(!draft.ai_facts.trim()){row.message='Uzupełnij fakty o produkcie lub dodaj opis.txt. Nie wygenerowano opisu.';drawQueue();continue;}
 const proposal=await call('/ai-generate',{facts:draft.ai_facts,images:$('ai-use-images').checked?await compactImages(draft.images):[]});
 draft.name=proposal.name;draft.sections=proposal.sections;draft.ai_questions=proposal.questions||[];
 if(!$('ai-use-images').checked)spreadImages(draft.sections,draft.images.length);
 fill();await call('/save',collect());row.prepared=true;row.message='Opis gotowy do sprawdzenia. Uzupełnij kategorię, parametry, cenę i ilość, jeśli ich brakuje.';done++;
 }catch(e){row.message='Zatrzymano: '+e.message;drawQueue();throw e;}
 drawQueue();for(const n of $('queue-items').querySelectorAll('input,select,button'))n.disabled=true;
 }
 }finally{for(const n of document.querySelectorAll('input,select,textarea'))n.disabled=false;for(const [n,disabled]of frozen)n.disabled=disabled;drawQueue();$('queue-progress').textContent='Przygotowano '+done+' opisów. '+(!$('queue-enabled').checked?'Kolejka zatrzymana. ':'')+'Otwórz szkic, sprawdź dane i zatwierdź publikację.';}
}
action('run-queue',()=>runQueue());
