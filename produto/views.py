from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from . import models
from perfil.models import Perfil
from django.views import View


class ProductList(ListView):
    model = models.Produto
    template_name = 'produto/list.html'
    context_object_name = 'products'
    paginate_by = 6


class Search(ProductList):
    def get_queryset(self, *args, **kwargs):
        template_name = 'produto/list.html'
        termo = self.request.GET.get('termo') or self.request.session['termo']
        qs = super().get_queryset(*args, **kwargs)

        if termo is None:
            messages.error(
                self.request,
                'Termo não encontrado.'
            )

        self.request.session['termo'] = termo

        qs = qs.filter(
            Q(nome__icontains=termo) |
            Q(descricao_curta__icontains=termo) |
            Q(descricao_longa__icontains=termo)
        )

        if not qs:
            messages.error(
                self.request,
                'Termo não encontrado.'
            )

        self.request.session.save()
        return qs


class ProductDetails(DetailView):
    model = models.Produto
    template_name = 'produto/details.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'


class AddToCart(View):
    def get(self, *args, **kwargs):

        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('product:list')
        )

        variacao_id = self.request.GET.get('vid')

        if not variacao_id:
            messages.error(
                self.request,
                'Produto não existe'
            )
            return redirect(http_referer)

        variacao = get_object_or_404(models.Variacao, id=variacao_id)
        variacao_estoque = variacao.estoque
        produto = variacao.produto

        produto_id = produto.id
        produto_nome = produto.nome
        variacao_nome = variacao.nome if variacao.nome != produto_nome else ''
        preco_unitario = variacao.preco
        preco_unitario_promocional = variacao.preco_promocional
        quantidade = 1
        slug = produto.slug
        imagem = produto.imagem

        if imagem:
            imagem = imagem.name
        else:
            imagem = ''

        if variacao.estoque < 1:
            messages.error(
                self.request,
                f'Produto {produto_nome} {variacao_nome} com estoque insuficiente.'
            )
            return redirect(http_referer)

        if not self.request.session.get('cart'):
            self.request.session['cart'] = {}
            self.request.session.save()

        cart = self.request.session['cart']

        if variacao_id in cart:
            quantidade_carrinho = cart[variacao_id]['quantidade']
            quantidade_carrinho += 1

            if variacao_estoque < quantidade_carrinho:
                messages.warning(
                    self.request,
                    f'Estoque insuficiente para {quantidade_carrinho} '
                    f'produtos "{produto_nome}" no seu carrinho. Adicionamos {variacao_estoque}x '
                    f'no seu carrinho.'
                )
                quantidade_carrinho = variacao_estoque

            cart[variacao_id]['quantidade'] = quantidade_carrinho
            cart[variacao_id]['preco_quantitativo'] = preco_unitario * \
                quantidade_carrinho
            cart[variacao_id]['preco_quantitativo_promocional'] = preco_unitario_promocional * \
                quantidade_carrinho
        else:
            cart[variacao_id] = {
                'produto_id': produto_id,
                'produto_nome': produto_nome,
                'variacao_nome': variacao_nome,
                'variacao_id': variacao_id,
                'preco_unitario': preco_unitario,
                'preco_unitario_promocional': preco_unitario_promocional,
                'preco_quantitativo': preco_unitario,
                'preco_quantitativo_promocional': preco_unitario_promocional,
                'quantidade': 1,
                'slug': slug,
                'imagem': imagem,
            }

        self.request.session.save()

        messages.success(
            self.request,
            f'Produto "{produto_nome} {variacao_nome}" adcionado ao carrinho. {cart[variacao_id]["quantidade"]}x'
        )

        return redirect(http_referer)


class RemoveFromCart(View):
    def get(self, *args, **kwargs):
        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('product:list')
        )
        variacao_id = self.request.GET.get('vid')

        if not variacao_id:
            return redirect(http_referer)

        if not self.request.session.get('cart'):
            return redirect(http_referer)

        if variacao_id not in self.request.session['cart']:
            return redirect(http_referer)

        cart = self.request.session['cart'][variacao_id]

        if cart['variacao_nome'] == cart['produto_nome']:
            variacao_nome = ''
        else:
            variacao_nome = cart['variacao_nome']

        messages.success(
            self.request,
            f'Produto "{cart["produto_nome"]} {variacao_nome}" removido do seu carrinho.'
        )

        del self.request.session['cart'][variacao_id]

        self.request.session.save()
        return redirect(http_referer)

        return HttpResponse('remove')


class Cart(View):
    def get(self, *args, **kwargs):
        contexto = {
            'cart': self.request.session.get('cart', {})
        }
        return render(self.request, 'produto/cart.html', contexto)


class CheckOut(View):
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('profile:create')

        perfil = Perfil.objects.filter(user=self.request.user).exists()

        if not perfil:
            messages.error(
                self.request,
                'Usuário sem perfil. Por favor atualize seus dados.'
            )
            return redirect('profile:create')

        if not self.request.session.get('cart'):
            messages.error(
                self.request,
                'Carrinho vazio.'
            )
            return redirect('product:list')

        contexto = {
            'usuario': self.request.user,
            'cart': self.request.session['cart']
        }
        return render(self.request, 'produto/checkout.html', contexto)
