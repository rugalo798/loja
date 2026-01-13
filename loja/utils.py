from django.core.mail import send_mail
from django.conf import settings
import mercadopago
import os

sdk = mercadopago.SDK(os.getenv("MP_ACCESS_TOKEN"))
def criar_pix(produto, email_client, request):

    base_url = "https://3kgames-store.up.railway.app"  # seu ngrok
    success_url = f"{base_url}/?status=approved&external_reference={produto.id}&payer_email={email_client}"
    failure_url = f"{base_url}/?status=failure"
    pending_url = f"{base_url}/?status=pending&external_reference={produto.id}&payer_email={email_client}"

    preference_data = {
        "items": [
            {
                "title": produto.nome,
                "quantity": 1,
                "unit_price": float(produto.preco),
            }
        ],
        "payer": {"email": email_client},
        "back_urls": {
            "success": success_url,  # obrigatoriamente precisa existir
            "failure": failure_url,
            "pending": pending_url
        },
        "auto_return": "approved",
        "external_reference": str(produto.id),
        "metadata": {
            "email_client": email_client
        }
    }

    preference_response = sdk.preference().create(preference_data)
    print(preference_response)
    return preference_response

def enviar_email(email_client, produto_nome, link_download):
    assunto = f"SEU PEDIDO DE {produto_nome} FOI APROVADO!"
    mensagem = f"""
    OLÁ


    O PAGAMENTO DO SEU PEDIDO FOI APROVADO!

    VOCÊ PODE BAIXAR NO LINK ABAIXO:

    {link_download}

    ENTRE NO NOSSO DISCORD PARA SABER COMO ATIVAR O JOGO: 
    
    https://discord.gg/AtSbsTrU


    Aproveite!
    """

    send_mail(
        subject=assunto,
        message=mensagem,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email_client],
        fail_silently=False     
    )