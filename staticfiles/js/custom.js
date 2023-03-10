var SPMaskBehavior = function (val) {
return val.replace(/\D/g, '').length === 11 ? '(00) 00000-0000' : '(00) 0000-00009';
},
spOptions = {
onKeyPress: function(val, e, field, options) {
field.mask(SPMaskBehavior.apply({}, arguments), options);
}
};

django.jQuery(function(){
django.jQuery('.mask-telefone1, .mask-telefone2').mask(SPMaskBehavior, spOptions);
django.jQuery('.mask-cpf').mask('000.000.000-00', {reverse: true});

django.jQuery('#locatario_form').submit(function(){
django.jQuery('#locatario_form').find(":input[class*='mask']").unmask();
});
});