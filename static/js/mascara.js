var SPMaskBehavior = function (val) {
  return val.replace(/\D/g, '').length === 11 ? '(00) 00000-0000' : '(00) 0000-00009';
},
spOptions = {
  onKeyPress: function(val, e, field, options) {
      field.mask(SPMaskBehavior.apply({}, arguments), options);
    }
};


$(function(){
    $('.mask-cpf, #id_CPF').mask('000.000.000-00', {reverse: true, placeholder: '___.___.___-__'});
    $('.mask-valor').mask("#.##0,00", {reverse: true});
    $('.mask-telefone1, .mask-telefone2, #id_telefone').mask(SPMaskBehavior, spOptions);

    $('.mask-x_form').submit(function(){
    $('.mask-x_form').find(":input[class*='mask']").unmask();
    $('.mask-x_form').find(":input[id*='mask-x_form']").unmask();
    $('.mask-x_form').find(":input[id*='id_telefone']").unmask();
    $('.mask-x_form').find(":input[id*='id_CPF']").unmask();
});
});
