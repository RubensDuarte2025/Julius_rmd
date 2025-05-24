import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import logging

# Assuming models from the same app.
# If products are in another app, you'd import them: from products.models import Produto, CategoriaProduto
# For now, we'll mock product/category fetching or assume they are passed in a simplified way.
from .models import PedidoWhatsApp

# Configure logging
logger = logging.getLogger(__name__)

# --- Mocked Data (replace with actual model queries later) ---
MOCKED_CATEGORIES = {
    "1": {"id": 1, "nome": "Pizzas Salgadas"},
    "2": {"id": 2, "nome": "Pizzas Doces"},
    "3": {"id": 3, "nome": "Bebidas"},
}

MOCKED_PRODUCTS = {
    "1": [ # Pizzas Salgadas
        {"id": 101, "nome": "Calabresa", "preco": 30.00, "categoria_id": 1},
        {"id": 102, "nome": "Margherita", "preco": 28.00, "categoria_id": 1},
        {"id": 103, "nome": "Frango com Catupiry", "preco": 32.00, "categoria_id": 1},
    ],
    "2": [ # Pizzas Doces
        {"id": 201, "nome": "Chocolate com Morango", "preco": 35.00, "categoria_id": 2},
        {"id": 202, "nome": "Romeu e Julieta", "preco": 33.00, "categoria_id": 2},
    ],
    "3": [ # Bebidas
        {"id": 301, "nome": "Refrigerante Lata", "preco": 5.00, "categoria_id": 3},
        {"id": 302, "nome": "Água Mineral", "preco": 3.00, "categoria_id": 3},
    ],
}

# --- Helper Functions ---
def get_categories_formatted():
    lines = ["Categorias:"]
    for key, cat in MOCKED_CATEGORIES.items():
        lines.append(f"{key}. {cat['nome']}")
    lines.append("\nDigite o número da categoria ou 'V' para voltar ao menu inicial.")
    return "\n".join(lines)

def get_products_formatted(category_id_str):
    category_id_int = MOCKED_CATEGORIES.get(category_id_str, {}).get("id")
    products_in_category = MOCKED_PRODUCTS.get(str(category_id_int), []) # Use str key for MOCKED_PRODUCTS

    if not products_in_category:
        return "Categoria não encontrada ou sem produtos. Digite 'V' para ver as categorias."

    lines = [f"{MOCKED_CATEGORIES[category_id_str]['nome']}:"]
    for i, prod in enumerate(products_in_category):
        lines.append(f"{i+1}. {prod['nome']} - R${prod['preco']:.2f}")
    lines.append("\nDigite o número do produto para adicionar ou 'V' para voltar às categorias.")
    return "\n".join(lines)


# Mocked Twilio message sending function (replace with actual Twilio client later)
def send_whatsapp_message(to_number, message_body):
    """
    Placeholder for sending a message via Twilio.
    In a real scenario, this would use the Twilio Python client.
    """
    logger.info(f"SIMULATING SENDING MESSAGE TO: {to_number}\nBODY: {message_body}")
    # Here you would integrate Twilio:
    # from twilio.rest import Client
    # account_sid = 'YOUR_TWILIO_ACCOUNT_SID'
    # auth_token = 'YOUR_TWILIO_AUTH_TOKEN'
    # client = Client(account_sid, auth_token)
    # message = client.messages.create(
    #     body=message_body,
    #     from_='whatsapp:YOUR_TWILIO_WHATSAPP_NUMBER',
    #     to=f'whatsapp:{to_number}'
    # )
    # logger.info(f"Message sent with SID: {message.sid}")
    pass


@csrf_exempt # Important for webhooks that don't send CSRF tokens
def whatsapp_webhook(request):
    if request.method == 'POST':
        try:
            # Twilio sends data as form-encoded, not JSON
            incoming_msg_body = request.POST.get('Body', '').strip().lower()
            from_number = request.POST.get('From', '').replace('whatsapp:', '') # Normalize number

            if not from_number:
                logger.error("Received POST without 'From' number.")
                return HttpResponse("Error: Missing 'From' number.", status=400)

            logger.info(f"Received message from {from_number}: '{incoming_msg_body}'")

            # --- Core Logic ---
            # Get or create user session/state
            pedido_conversa, created = PedidoWhatsApp.objects.get_or_create(
                telefone_cliente=from_number
            )

            if created:
                pedido_conversa.estado_conversa = 'INICIO' # Initial state
                # Fall through to INICIO state handling for new users

            # --- State Machine Logic ---
            current_state = pedido_conversa.estado_conversa
            response_message = "Desculpe, não entendi. Pode repetir?" # Default fallback

            if incoming_msg_body == 'cancelar': # Global cancel keyword
                pedido_conversa.reset_conversa() # Resets state to INICIO
                response_message = "Sua conversa foi reiniciada. " \
                                   "Olá! Bem-vindo à Pizzaria [Nome da Pizzaria]! 😊\n" \
                                   "Digite:\n1️⃣ Ver Cardápio e Fazer Pedido 🍕\n2️⃣ Falar com um Atendente 💬"
                pedido_conversa.estado_conversa = 'AGUARDANDO_OPCAO_INICIAL'

            elif current_state == 'INICIO': # Also handles reset state
                response_message = "Olá! Bem-vindo à Pizzaria [Nome da Pizzaria]! 😊\nDigite:\n1️⃣ Ver Cardápio e Fazer Pedido 🍕\n2️⃣ Falar com um Atendente 💬"
                pedido_conversa.estado_conversa = 'AGUARDANDO_OPCAO_INICIAL'

            elif current_state == 'AGUARDANDO_OPCAO_INICIAL':
                if incoming_msg_body == '1':
                    response_message = get_categories_formatted()
                    pedido_conversa.estado_conversa = 'AGUARDANDO_ESCOLHA_CATEGORIA'
                elif incoming_msg_body == '2':
                    response_message = "Um momento, vou te transferir para um de nossos atendentes. Se precisar recomeçar, digite 'cancelar'."
                    pedido_conversa.estado_conversa = 'TRANSFERIDO_ATENDENTE'
                else:
                    response_message = "Opção inválida. Digite:\n1️⃣ Ver Cardápio e Fazer Pedido 🍕\n2️⃣ Falar com um Atendente 💬\nOu 'cancelar' para recomeçar."

            elif current_state == 'AGUARDANDO_ESCOLHA_CATEGORIA':
                if incoming_msg_body.lower() == 'v':
                    response_message = "Olá! Bem-vindo à Pizzaria [Nome da Pizzaria]! 😊\nDigite:\n1️⃣ Ver Cardápio e Fazer Pedido 🍕\n2️⃣ Falar com um Atendente 💬"
                    pedido_conversa.estado_conversa = 'AGUARDANDO_OPCAO_INICIAL'
                elif incoming_msg_body in MOCKED_CATEGORIES:
                    pedido_conversa.dados_temporarios = {'categoria_selecionada': incoming_msg_body} # Store selected category
                    response_message = get_products_formatted(incoming_msg_body)
                    pedido_conversa.estado_conversa = 'AGUARDANDO_ESCOLHA_PRODUTO'
                else:
                    response_message = "Categoria inválida. " + get_categories_formatted()

            elif current_state == 'AGUARDANDO_ESCOLHA_PRODUTO':
                categoria_selecionada_numero = pedido_conversa.dados_temporarios.get('categoria_selecionada')
                if incoming_msg_body.lower() == 'v':
                    response_message = get_categories_formatted()
                    pedido_conversa.estado_conversa = 'AGUARDANDO_ESCOLHA_CATEGORIA'
                    pedido_conversa.dados_temporarios = {} # Clear temp data
                else:
                    try:
                        escolha_produto_idx = int(incoming_msg_body) - 1
                        categoria_id_int = MOCKED_CATEGORIES.get(categoria_selecionada_numero, {}).get("id")
                        produtos_na_categoria = MOCKED_PRODUCTS.get(str(categoria_id_int), [])

                        if 0 <= escolha_produto_idx < len(produtos_na_categoria):
                            produto_escolhido = produtos_na_categoria[escolha_produto_idx]
                            # Add to cart (using method from PedidoWhatsApp model)
                            # For this, we need a mock product object or adapt add_item_carrinho
                            mock_produto_obj = type('MockProduto', (), produto_escolhido)() # Create a mock object
                            pedido_conversa.adicionar_item_carrinho(mock_produto_obj) # uses .save()
                            total_carrinho = pedido_conversa.calcular_total_carrinho()
                            response_message = (
                                f"'{produto_escolhido['nome']}' adicionado! Seu carrinho tem {len(pedido_conversa.carrinho_atual)} item(ns), totalizando R${total_carrinho:.2f}.\n"
                                f"Digite:\n"
                                f"'C' para continuar comprando (na categoria '{MOCKED_CATEGORIES[categoria_selecionada_numero]['nome']}')\n"
                                f"'CAT' para ver outras categorias\n"
                                f"'F' para finalizar o pedido\n"
                                f"'R' para remover o último item."
                            )
                            pedido_conversa.estado_conversa = 'AGUARDANDO_ACAO_CARRINHO'
                        else:
                            response_message = "Número do produto inválido. " + get_products_formatted(categoria_selecionada_numero)
                    except ValueError:
                        response_message = "Entrada inválida. Por favor, digite o número do produto ou 'V' para voltar.\n" + get_products_formatted(categoria_selecionada_numero)
            
            elif current_state == 'AGUARDANDO_ACAO_CARRINHO':
                categoria_selecionada_numero = pedido_conversa.dados_temporarios.get('categoria_selecionada')
                if incoming_msg_body == 'c': # Continuar na mesma categoria
                    if categoria_selecionada_numero:
                        response_message = get_products_formatted(categoria_selecionada_numero)
                        pedido_conversa.estado_conversa = 'AGUARDANDO_ESCOLHA_PRODUTO'
                    else: # Should not happen if state is managed properly
                        response_message = get_categories_formatted()
                        pedido_conversa.estado_conversa = 'AGUARDANDO_ESCOLHA_CATEGORIA'
                elif incoming_msg_body == 'cat': # Ver categorias
                    response_message = get_categories_formatted()
                    pedido_conversa.estado_conversa = 'AGUARDANDO_ESCOLHA_CATEGORIA'
                elif incoming_msg_body == 'f': # Finalizar pedido
                    if pedido_conversa.carrinho_atual:
                        total_pedido = pedido_conversa.calcular_total_carrinho()
                        carrinho_formatado = pedido_conversa.formatar_carrinho_para_mensagem()
                        response_message = (
                            f"{carrinho_formatado}\n\n"
                            f"TOTAL DO PEDIDO: R${total_pedido:.2f}\n\n"
                            f"Para confirmar e pagar com PIX, digite 'PIX'.\n"
                            f"Para cancelar este pedido, digite 'X'."
                        )
                        pedido_conversa.estado_conversa = 'AGUARDANDO_CONFIRMACAO_PEDIDO'
                    else:
                        response_message = "Seu carrinho está vazio. Adicione itens antes de finalizar.\n" + get_categories_formatted()
                        pedido_conversa.estado_conversa = 'AGUARDANDO_ESCOLHA_CATEGORIA'
                elif incoming_msg_body == 'r': # Remover último item
                    if pedido_conversa.remover_ultimo_item_carrinho(): # uses .save()
                        total_carrinho = pedido_conversa.calcular_total_carrinho()
                        carrinho_len = len(pedido_conversa.carrinho_atual)
                        if carrinho_len > 0:
                            response_message = (
                                f"Último item removido. Seu carrinho tem {carrinho_len} item(ns), totalizando R${total_carrinho:.2f}.\n"
                                f"Digite 'C', 'CAT', 'F', ou 'R'."
                            )
                        else:
                             response_message = "Carrinho esvaziado. Adicione itens para continuar.\n" + get_categories_formatted()
                             pedido_conversa.estado_conversa = 'AGUARDANDO_ESCOLHA_CATEGORIA' # Go back to categories
                    else:
                        response_message = "Seu carrinho já está vazio.\nDigite 'C' ou 'CAT' para adicionar itens."
                else:
                    response_message = ("Opção inválida. Digite 'C' para continuar comprando, "
                                        "'CAT' para categorias, 'F' para finalizar, ou 'R' para remover.")

            elif current_state == 'AGUARDANDO_CONFIRMACAO_PEDIDO':
                if incoming_msg_body == 'pix':
                    # MVP: Static PIX key. Actual order saving will happen here.
                    # For now, just transition state and provide PIX info.
                    # In a real scenario, you'd create a `Pedido` object in your main orders app.
                    # pedido_conversa.pedido_confirmado_id = new_order.id (pseudo-code)
                    chave_pix_estatica = "CNPJ: XX.XXX.XXX/0001-XX (Banco XPTO)" # Placeholder
                    response_message = (
                        f"Ótimo! Seu pedido foi registrado e aguarda pagamento.\n"
                        f"Pague com a chave PIX: {chave_pix_estatica}\n"
                        f"Valor total: R${pedido_conversa.calcular_total_carrinho():.2f}\n\n"
                        f"IMPORTANTE: Após o pagamento, por favor, envie 'PAGO' ou o comprovante para este chat "
                        f"para que um atendente possa confirmar e processar seu pedido.\n\n"
                        f"Obrigado pela preferência!"
                    )
                    pedido_conversa.estado_conversa = 'AGUARDANDO_CONFIRMACAO_PAGAMENTO_PIX'
                elif incoming_msg_body == 'x':
                    pedido_conversa.reset_conversa() # Clears cart and state
                    response_message = "Pedido cancelado. Sua conversa foi reiniciada.\n" + \
                                       "Olá! Bem-vindo à Pizzaria [Nome da Pizzaria]! 😊\n" + \
                                       "Digite:\n1️⃣ Ver Cardápio e Fazer Pedido 🍕\n2️⃣ Falar com um Atendente 💬"
                    pedido_conversa.estado_conversa = 'AGUARDANDO_OPCAO_INICIAL'
                else:
                    response_message = "Opção inválida. Digite 'PIX' para confirmar ou 'X' para cancelar."

            elif current_state == 'AGUARDANDO_CONFIRMACAO_PAGAMENTO_PIX':
                # MVP: Manual confirmation by attendant. Bot just acknowledges.
                #      When attendant confirms, they would manually trigger next steps.
                #      For the bot, upon receiving 'PAGO', we now also set kitchen status.
                if 'pago' in incoming_msg_body or 'comprovante' in incoming_msg_body: # Simple check
                    # Set kitchen status and time
                    pedido_conversa.status_cozinha = PedidoWhatsApp.STATUS_COZINHA_AGUARDANDO
                    pedido_conversa.horario_entrada_cozinha = timezone.now()
                    # Note: The actual order creation in a main 'Pedidos' table is still a Pós-MVP or attendant task.
                    # This just flags the WhatsApp conversation/order for the kitchen.
                    
                    # Registrar o pagamento usando o serviço de pagamentos
                    try:
                        from pagamentos.services import registrar_pagamento_para_pedido
                        from pagamentos.models import Pagamento # Para acesso a choices
                        
                        # Assumindo que o valor total do carrinho é o valor pago para PIX no MVP
                        valor_total_pedido = pedido_conversa.calcular_total_carrinho()
                        
                        registrar_pagamento_para_pedido(
                            pedido_obj=pedido_conversa,
                            metodo_pagamento=Pagamento.METODO_PIX,
                            valor_pago=valor_total_pedido,
                            status_pagamento=Pagamento.STATUS_APROVADO, # Manualmente confirmado
                            # qr_code_pix pode ser a chave estática informada, se desejado registrar
                        )
                        logger.info(f"Pagamento PIX registrado para PedidoWhatsApp ID {pedido_conversa.id}")
                    except Exception as e:
                        logger.error(f"Erro ao registrar pagamento para PedidoWhatsApp ID {pedido_conversa.id}: {e}")
                        # Continuar mesmo se o registro do pagamento falhar, pois o fluxo do bot é prioritário aqui.
                        # Mas logar o erro é crucial.

                    response_message = ("Obrigado por informar o pagamento! Seu pedido foi enviado para a cozinha e em breve um de nossos atendentes "
                                        "irá verificar e confirmar os detalhes. Se precisar de algo mais, digite 'cancelar' para recomeçar.")
                else:
                    response_message = ("Aguardando sua confirmação de pagamento (envie 'PAGO') ou comprovante. "
                                        "Se preferir, digite 'cancelar' para reiniciar o atendimento.")
                # This state could eventually time out or be escalated to an attendant.
                # For MVP, it stays here until 'cancelar' or manual intervention.

            elif current_state == 'TRANSFERIDO_ATENDENTE':
                # Bot should ideally not respond further unless explicitly reset by 'cancelar'
                # or by an internal mechanism (e.g., attendant marks as resolved).
                if incoming_msg_body == 'cancelar': # Allow reset
                    pedido_conversa.reset_conversa()
                    response_message = "Sua conversa foi reiniciada. " + \
                                   "Olá! Bem-vindo à Pizzaria [Nome da Pizzaria]! 😊\n" + \
                                   "Digite:\n1️⃣ Ver Cardápio e Fazer Pedido 🍕\n2️⃣ Falar com um Atendente 💬"
                    pedido_conversa.estado_conversa = 'AGUARDANDO_OPCAO_INICIAL'
                else:
                    # No automatic response, or a very minimal one like:
                    response_message = "Você já foi direcionado a um atendente. Por favor, aguarde."
                    # To avoid loops, don't send message here or send it very rarely.
                    # For now, let's assume send_whatsapp_message might be skipped for this state after initial transfer.
                    # However, for testing, we'll allow it to respond.
                    pass


            pedido_conversa.save()
            send_whatsapp_message(from_number, response_message)

            # Twilio expects an empty response or TwiML. For now, empty HTTP 200 is fine.
            return HttpResponse(status=200)

        except Exception as e:
            logger.error(f"Error processing webhook: {e}", exc_info=True)
            # Avoid sending error details back to Twilio in production
            # but good for debugging initially.
            # Consider sending a generic error message to the user via WhatsApp if possible.
            send_whatsapp_message(from_number, "Ocorreu um erro interno. Por favor, tente novamente mais tarde ou contate o suporte.")
            return HttpResponse(f"Internal Server Error: {e}", status=500)
    else:
        logger.warning(f"Received {request.method} request to webhook, expected POST.")
        return HttpResponse("Method not allowed", status=405)
