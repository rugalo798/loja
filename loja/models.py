from django.db import models

# Create your models here.
class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    imagem_url = models.URLField()
    link_download = models.URLField()

    def __str__(self):
        return self.nome


class Pedido(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default="pending")
    email_client = models.EmailField()
    link_entrega = models.URLField(null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.produto.nome} - {self.status}"