from utils import utils
from django.conf import settings
from PIL import Image
import os
from django.db import models
from django.utils.text import slugify


class Produto(models.Model):
    nome = models.CharField(max_length=255)
    descricao_curta = models.TextField(max_length=255)
    descricao_longa = models.TextField()
    imagem = models.ImageField(
        upload_to='produto_imagens/%Y/%m', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    preco_marketing = models.FloatField(verbose_name='Preço')
    preco_marketing_promocional = models.FloatField(
        default=0, verbose_name='Preço Promo')
    tipo = models.CharField(
        default='V',
        max_length=1,
        choices=(
            ('V', 'Variável'),
            ('S', 'Simples'),
        )
    )

    def get_preco_format(self):
        return utils.formata_real(self.preco_marketing)

    get_preco_format.short_description = 'Preço em BRL'

    def get_preco_promo_format(self):
        return utils.formata_real(self.preco_marketing_promocional)

    get_preco_promo_format.short_description = 'Preço Promocional'

    @staticmethod
    def resize_image(img, new_width=800):
        img_full_path = os.path.join(settings.MEDIA_ROOT, img.name)
        img_pil = Image.open(img_full_path)
        original_width, original_height = img_pil.size

        if original_width <= new_width:
            img_pil.close()
            return

        new_height = round((new_width * original_height) / original_width)
        new_img = img_pil.resize((new_width, new_height), Image.LANCZOS)

        new_img.save(
            img_full_path,
            optimize=True,
            quality=50,
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = f'{slugify(self.nome)}'
            self.slug = slug

        super().save(*args, **kwargs)

        max_image_size = 800

        if self.imagem:
            self.resize_image(self.imagem, max_image_size)

    def __str__(self):
        return self.nome


class Variacao(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50, blank=True, null=True)
    preco = models.FloatField(blank=True, null=True)
    preco_promocional = models.FloatField(default=0, blank=True, null=True)
    estoque = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.nome or self.produto.nome

    def get_variacao_preco(self):
        return utils.formata_real(self.preco)

    def get_variacao_preco_promo(self):
        return utils.formata_real(self.preco_promocional)

    def save(self, *args, **kwargs):
        if not self.nome:
            self.nome = self.produto.nome
            self.preco = self.produto.preco_marketing
            self.preco_promocional = self.produto.preco_marketing_promocional

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Variação'
        verbose_name_plural = 'Variações'
