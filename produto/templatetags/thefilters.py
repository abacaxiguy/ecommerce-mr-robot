from django.template import Library
from utils import utils

register = Library()


@register.filter
def formata_preco(val):
    return utils.formata_real(val)


@register.filter
def soma_qtd(cart):
    return utils.cart_total_qtd(cart)


@register.filter
def soma_total(cart):
    return utils.cart_totals(cart)
