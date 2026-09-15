const assert=require('node:assert/strict');
const {summarize}=require('./messages.js');
const r=summarize({message:'Szkic zapisany',validation:{errors:[],warnings:[
 {code:'SAFETY_INFO_DESCRIPTION_SUGGESTED_DATA_VERIFICATION_NEEDED'},
 {code:'ConstraintViolationException.OfferValidation',userMessage:'Wysyłasz za granicę – zadbaj o zgodność z przepisami'},
 {code:'UNKNOWN',userMessage:'Nieznana uwaga'}]}});
assert.equal(r.errors.length,0);assert.equal(r.warnings.length,3);
assert(r.warnings[0].includes('weryfikacji'));assert(r.warnings[1].includes('poza Polskę'));
assert.equal(r.warnings[2],'Nieznana uwaga');assert(!r.title.includes('błęd'));
assert.equal(summarize({publication:{status:'ACTIVE'}}).title,'Oferta jest opublikowana.');
assert.equal(summarize({validation:{errors:[{userMessage:'Brak marki'}]}}).errors[0],'Brak marki');
console.log('Komunikaty Allegro: OK');
