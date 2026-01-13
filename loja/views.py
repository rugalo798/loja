from django.shortcuts import render, redirect
from .models import Produto
from .utils import enviar_email, criar_pix
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
import os
import mercadopago

sdk = mercadopago.SDK(os.getenv("MP_ACCESS_TOKEN"))

@csrf_exempt
# Create your views here.
def index(request):
    produtos = Produto.objects.all()
    message = None

    # Pega os parâmetros da URL
    payment_status = request.GET.get("status")
    external_reference = request.GET.get("external_reference")
    payer_email_param = request.GET.get("payer_email")  # <-- só pega aqui

    # Só processa se vier tudo certinho
    if payment_status == "approved" and external_reference and payer_email_param:
        try:
            produto = Produto.objects.get(id=external_reference)
            
            # Envia o email com link de download
            enviar_email(
                email_client=payer_email_param,
                produto_nome=produto.nome,
                link_download=produto.link_download
            )

            message = f"💰 Pagamento aprovado! Email enviado para {payer_email_param}"
        except Produto.DoesNotExist:
            message = "Produto não encontrado."

    elif payment_status == 'pending':
        message = f"💰 Pagamento aprovado! Email enviado para {payer_email_param}"

    elif payment_status == 'failure':
        message = "❌ Pagamento falhou. Tente novamente."

    return render(request, "index.html", {"produtos": produtos, "message": message})


def comprar_view(request):
    if request.method == "POST":
        email_client = request.POST.get("email")
        produto_id = request.POST.get("produto_id")
        produto = Produto.objects.get(id=produto_id)

        redirect_url = request.build_absolute_uri("/")

        preference = criar_pix(produto, email_client, request)
        print(preference)

        checkout_url = preference["response"]["init_point"]
        return redirect(checkout_url)

    return redirect("index")


def enviar_email_view(request):
    message = None

    if request.method == "POST":
        produto_id = request.POST.get("produto_id")  # pega do form
        email_client = request.POST.get("email")

        from django.shortcuts import get_object_or_404
        produto = get_object_or_404(Produto, id=produto_id)

        enviar_email(
            email_client=email_client,
            produto_nome=produto.nome,
            link_download=produto.link_download
        )

        message = f"💌 Email enviado para {email_client}!"

    produtos = Produto.objects.all()

    
    return render(request, "index.html", {"produtos": produtos, "message": message})



@csrf_exempt
def mp_webhook(request):
    payment_id = request.GET.get("data.id")
    
    # Pega as infos do pagamento do MP
    payment_info = sdk.payment().get(payment_id)["response"]

    # Pega email do metadata, se não existir usa payer.email
    email_cliente = payment_info.get("metadata", {}).get("email_client") \
                    or payment_info.get("payer", {}).get("email")
    
    if not email_cliente:
        print("E-mail do cliente não encontrado")
        return HttpResponse("E-mail não encontrado", status=400)
    
    print("E-mail do cliente:", email_cliente)

    # Pega o produto
    produto_id = payment_info.get("external_reference")
    try:
        produto = Produto.objects.get(id=produto_id)
    except Produto.DoesNotExist:
        print("Produto não encontrado")
        return HttpResponse("Produto não encontrado", status=400)

    # Envia o email com link de download
    enviar_email(email_cliente, produto.nome, produto.link_download)

    return HttpResponse("OK", status=200)