from django.contrib import admin
from .models import Produto, Variacao


class VariacaoInline(admin.TabularInline):
    model = Variacao
    extra = 1


class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao_curta',
                    'get_preco_format', 'get_preco_promo_format']
    inlines = [
        VariacaoInline
    ]


admin.site.register(Produto, ProdutoAdmin)
admin.site.register(Variacao)
