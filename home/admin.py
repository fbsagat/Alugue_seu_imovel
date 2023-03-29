from django.contrib import admin
from .models import Usuario, Locatario, Imovei, Contrato, Pagamento, Gasto, Anotacoe, DevMensagen, ImovGrupo, Parcela, \
    Tarefa, ContratoDocConfig, ContratoModelo
from django.contrib.auth.admin import UserAdmin


# class LocatarioAdmin(admin.ModelAdmin):
#     form = Mascara
#
#
# campos = list(UserAdmin.fieldsets)
# UserAdmin.fieldsets = tuple(campos)
# admin.site.register(Usuario, UserAdmin)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    model = Usuario
    list_display = ('first_name', 'last_name', 'email', 'is_staff', 'is_active')
    list_filter = ("is_staff", "is_active", 'is_superuser',)
    search_fields = ('first_name', 'email',)
    fieldsets = (
        ('Informações', {"fields": (
            'first_name', 'last_name', 'telefone', 'RG', 'CPF', 'locat_slots', 'email', 'nacionalidade', 'estadocivil',
            'ocupacao', 'endereco_completo', 'password', 'data_eventos_i', 'itens_eventos', 'qtd_eventos',
            'ordem_eventos', 'recibo_ultimo', 'recibo_preenchimento', 'tabela_ultima_data_ger', 'tabela_meses_qtd',
            'tabela_imov_qtd',)}),

        ("Permissões", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
         ),
    )
    ordering = ("first_name",)


@admin.register(Locatario)
class LocatarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'do_locador', 'telefone1', 'telefone2', 'email', 'docs',
                    'data_registro', 'estadocivil')
    search_fields = ('nome',)


@admin.register(ImovGrupo)
class ImovGrupoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'do_usuario')
    search_fields = ('nome',)


@admin.register(Imovei)
class ImoveisAdmin(admin.ModelAdmin):
    list_display = ('nome', 'do_locador', 'com_locatario', 'contrato_atual', 'grupo', 'data_registro')
    search_fields = ('nome', 'grupo')


@admin.register(Contrato)
class ContratosAdmin(admin.ModelAdmin):
    list_display = ('do_locador', 'do_locatario', 'do_imovel', 'data_entrada', 'duracao', 'valor_mensal',
                    'data_registro')
    list_filter = ('em_posse', 'rescindido', 'vencido')


@admin.register(ContratoDocConfig)
class ContratoDocConfigsAdmin(admin.ModelAdmin):
    list_display = ('do_contrato', 'do_modelo',)


@admin.register(ContratoModelo)
class ContratoModeloAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'data_criacao',)


@admin.register(Pagamento)
class PagamentosAdmin(admin.ModelAdmin):
    list_display = ('ao_locador', 'ao_contrato', 'do_locatario', 'valor_pago', 'data_pagamento',
                    'data_de_recibo', 'data_criacao')
    list_filter = ('forma',)


@admin.register(Parcela)
class ParcelasAdmin(admin.ModelAdmin):
    list_display = ('do_contrato', 'codigo', 'data_pagm_ref')


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('do_locador', 'do_imovel', 'valor', 'data', 'comprovante', 'data_criacao')


@admin.register(Anotacoe)
class AnotacoeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'do_usuario', 'data_registro')
    search_fields = ('titulo',)


@admin.register(DevMensagen)
class MensagemDevAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'do_usuario', 'data_registro', 'imagem')
    list_filter = ('tipo_msg',)
    search_fields = ('titulo',)


@admin.register(Tarefa)
class Tarefas(admin.ModelAdmin):
    list_display = ('do_usuario', 'autor_tipo', 'data_registro')
    list_filter = ('autor_tipo', 'lida', 'apagada')
