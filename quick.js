(function(root){
'use strict';
function checkPhotos(files,existing=0){if(existing+files.length>16)throw Error('Wybrano '+(existing+files.length)+' zdjęć. Maksymalnie 16 — wybierz zdjęcia w galerii lub usuń nadmiar z folderu.');for(const f of files)if(f.size>10000000)throw Error('Zdjęcie „'+f.name+'” przekracza 10 MB.');}
function parseDescription(text){
 if(!text.trim())throw Error('Wklej gotowy opis.');if(text.length>50000)throw Error('Opis jest za długi (maks. 50 000 znaków).');
 const sections=[];let current={title:'',text:''};
 for(let line of text.replace(/\r/g,'').split('\n')){
 if(/^\s*!?\[[^\]]*\]\(https?:\/\/[^)]*\)\s*$/.test(line))continue;
 const heading=line.match(/^\s*#{1,6}\s+(.+?)\s*#*$/)||line.match(/^\s*\*\*([^*]+:)\*\*\s*$/)||line.match(/^([^\n:*]{2,80}):\s*$/);
 if(heading){if(current.text.trim())sections.push(current);current={title:heading[1].replace(/\*\*/g,'').replace(/:$/,''),text:''};}
 else{line=line.replace(/^\s*[•*]\s+/,'- ').replace(/\[([^\]]+)\]\(https?:\/\/[^)]+\)/g,'$1');current.text+=line+'\n';}
 }
 if(current.text.trim())sections.push(current);
 if(!sections.length)throw Error('Opis musi zawierać treść, nie tylko nagłówki.');
 return sections.map(s=>({...s,text:s.text.trim()}));
}
const api={checkPhotos,parseDescription};if(typeof module!=='undefined')module.exports=api;else root.NetstoreQuick=api;
})(globalThis);
