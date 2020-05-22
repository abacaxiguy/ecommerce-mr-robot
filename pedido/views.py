from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, DetailView
from django.http import HttpResponse
from django.views import View
from django.contrib import messages
from produto.models import Variacao
from django.utils import timezone
from utils import utils

from .models import Pedido, ItemPedido


class DispatchLoginRequiredMixin(View):
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('profile:create')

        return super().dispatch(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(user=self.request.user)
        return qs


class PayOrder(DispatchLoginRequiredMixin, DetailView):
    template_name = 'pedido/pay.html'
    model = Pedido
    pk_url_kwarg = 'pk'
    context_object_name = 'pedido'


class FinishOrder(View):
    template_name = 'pedido/pay.html'

    def get(self, *args, **kwargs):

        if not self.request.user.is_authenticated:
            messages.error(
                self.request,
                'Você precisa fazer login.'
            )
            return redirect('profile:create')

        if not self.request.session.get('cart'):
            messages.error(
                self.request,
                'Carrinho vazio.'
            )
            return redirect('product:list')

        carrinho = self.request.session.get('cart')
        carrinho_variacao_ids = [v for v in carrinho]
        bd_variacoes = list(
            Variacao.objects.select_related('produto')
            .filter(id__in=carrinho_variacao_ids)
        )

        for variacao in bd_variacoes:
            vid = str(variacao.id)

            estoque = variacao.estoque
            qtd_carrinho = carrinho[vid]['quantidade']
            preco_unt = carrinho[vid]['preco_unitario']
            preco_unt_promo = carrinho[vid]['preco_unitario_promocional']

            error_msg_estoque = ''

            if estoque < qtd_carrinho:
                carrinho[vid]['quantidade'] = estoque
                carrinho[vid]['preco_quantitativo'] = estoque * preco_unt
                carrinho[vid]['preco_quantitativo_promocional'] = estoque * \
                    preco_unt_promo

                error_msg_estoque = 'Estoque insuficiente em alguns produtos em seu carrinho. Reduzimos seu carrinho, por favor verifique quais produtos foram esses.'

            if error_msg_estoque:
                messages.error(
                    self.request,
                    error_msg_estoque
                )
                self.request.session.save()
                return redirect('product:cart')

        qtd_total_carrinho = utils.cart_total_qtd(carrinho)
        valor_total_carrinho = utils.cart_totals(carrinho)

        pedido = Pedido(
            user=self.request.user,
            total=valor_total_carrinho,
            qtd_total=qtd_total_carrinho,
            status='C',

        )

        pedido.save()

        ItemPedido.objects.bulk_create(
            [
                ItemPedido(
                    pedido=pedido,
                    produto=v['produto_nome'],
                    produto_id=v['produto_id'],
                    variacao=v['variacao_nome'],
                    variacao_id=v['variacao_id'],
                    preco=v['preco_quantitativo'],
                    preco_promocional=v['preco_quantitativo_promocional'],
                    quantidade=v['quantidade'],
                    imagem=v['imagem'],
                ) for v in carrinho.values()
            ]
        )

        del self.request.session['cart']
        return redirect(
            reverse(
                'order:pay',
                kwargs={
                    'pk': pedido.pk
                }
            )
        )


class OrderDetails(DispatchLoginRequiredMixin, DetailView):
    model = Pedido
    context_object_name = 'pedido'
    template_name = 'pedido/details.html'
    pk_url_kwarg = 'pk'


class ListOrders(DispatchLoginRequiredMixin, ListView):
    model = Pedido
    context_object_name = 'pedidos'
    template_name = 'pedido/list_orders.html'
    paginate_by = 5
    ordering = ['-id']


class Over(DispatchLoginRequiredMixin):
    template_name = 'pedido/game_over.html'

    def get(self, *args, **kwargs):
        return render(self.request, self.template_name)
