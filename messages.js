(function(root){
 function warning(w){
  const original=w.userMessage||w.message||w.code||'Sprawdź uwagę Allegro.';
  if(w.code==='SAFETY_INFO_DESCRIPTION_SUGGESTED_DATA_VERIFICATION_NEEDED')return 'Bezpieczeństwo produktu: sprawdź dane producenta oraz treść informacji o bezpieczeństwie. Podpowiedź AI jest przykładem i wymaga Twojej weryfikacji przed publikacją.';
  if(w.code==='ConstraintViolationException.OfferValidation'&&/Wysyłasz za granicę|dostawę zagraniczną/i.test(original))return 'Dostawa zagraniczna: ta oferta umożliwia wysyłkę poza Polskę. Sprawdź wymagania dla krajów dostawy. Jeśli chcesz sprzedawać tylko w Polsce, zmień cennik dostawy w Allegro i ponownie pobierz ustawienia ze wzoru.';
  return original;
 }
 function summarize(r){const v=r.validation||{};const errors=v.errors||[],warnings=v.warnings||[];let title=r.message||'Otrzymano odpowiedź Allegro.';
 if(r.publication?.status){const labels={ACTIVE:'Oferta jest opublikowana.',INACTIVE:'Oferta jest szkicem — nie jest opublikowana.',ENDED:'Oferta jest zakończona.',ACTIVATING:'Trwa publikowanie oferty.'};title=labels[r.publication.status]||'Status oferty: '+r.publication.status;}
 if(errors.length)title='Oferta wymaga poprawek ('+errors.length+').';
 return {title,errors:errors.map(e=>e.userMessage||e.message||e.code),warnings:warnings.map(warning),hasValidation:!!r.validation};}
 const api={summarize,warning};if(typeof module!=='undefined')module.exports=api;else root.NetstoreMessages=api;
})(typeof window!=='undefined'?window:globalThis);
