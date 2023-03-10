from django.contrib import admin
from home.forms import Mascara, FormUsuario
from .models import Usuario, Locatario, Imovei, Contrato, Pagamento, Gasto, Anotacoe, MensagemDev, ImovGrupo, Parcela, \
    Tarefa
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
    list_display = ("email", "is_staff", "is_active", 'first_name', 'last_name', 'email')
    list_filter = ("is_staff", "is_active",)
    search_fields = ('first_name', 'email')
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
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
    ordering = ("email",)


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


@admin.register(MensagemDev)
class MensagemDevAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'do_usuario', 'data_registro', 'imagem')
    list_filter = ('tipo_msg',)
    search_fields = ('titulo',)


@admin.register(Tarefa)
class Tarefas(admin.ModelAdmin):
    list_display = ('do_usuario', 'autor_tipo', 'data_registro')
    list_filter = ('autor_tipo', 'lida', )
