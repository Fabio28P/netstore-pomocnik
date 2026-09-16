const assert=require('node:assert/strict');
const {checkPhotos,parseDescription}=require('./quick.js');
for(const count of [13,16])checkPhotos(Array.from({length:count},(_,i)=>({name:i+'.png',size:9000000})));
assert.throws(()=>checkPhotos(Array(17).fill({size:10})),/16/);
assert.throws(()=>checkPhotos([{name:'duzy.png',size:10000001}]),/duzy.png/);
assert.throws(()=>checkPhotos(Array(3).fill({size:10}),14),/16/);
const s=parseDescription('Wstęp.\n\n**Najważniejsze zalety:**\n\n**Czarny kolor**\n\n**Szybka wymiana**\n\n## Montaż\n- Wyjmij baterie.\n![Zdjęcie](https://example.com/img.png)');
assert.equal(s.length,3);assert.match(s[1].text,/Czarny kolor/);assert.match(s[1].text,/Szybka wymiana/);assert.equal(s[2].title,'Montaż');assert(!s[2].text.includes('https://'));assert.throws(()=>parseDescription(' '));
console.log('Import 13/16 zdjęć, duże foldery i gotowe opisy: OK');
