from datetime import date


def formata_real(val):
    try:
        val = float(val)
        return f'R$ {val:.2f}'.replace('.', ',')
    except:
        val = val
        return f'R$ {val:.2f}'.replace('.', ',')


def cart_total_qtd(cart):
    return sum([item['quantidade'] for item in cart.values()])


def cart_totals(cart):
    return sum(
        [
            item.get('preco_quantitativo_promocional')
            if item.get('preco_quantitativo_promocional')
            else item.get('preco_quantitativo')
            for item
            in cart.values()
        ]
    )


def calc_age(bday):
    today = date.today()
    age = today.year - bday.year - \
        ((today.month, today.day) < (bday.month, bday.day))
    return age
