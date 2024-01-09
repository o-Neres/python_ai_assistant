from fastapi import FastAPI, Form
from decouple import config
from openai import OpenAI
import json

# Internal imports
from utils import send_message, logger

app = FastAPI()
client = OpenAI(api_key=config("OPENAI_API_KEY"))

def load_data(filename):
    data = []
    with open(filename, 'r') as file:
        for line in file:
            data.append(json.loads(line))
    return data

data = load_data('data.json')

def build_context(data):
    context = ""
    for item in data:
        for message in item['messages']:
            context += f"{message['role']}: {message['content']}\n"
    return context

@app.post("/message")
async def reply(Body: str = Form(), From: str = Form()):
    sender_number = From.split(":")[1]

    context = build_context(data)
    prompt = context + f"\nPergunta: {Body}\nResposta:"

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
          {"role": "system", "content": "Você é um assistente prestativo e objetivo que responde apenas sobre os produtos InfiniteTap e InfiniteLink. Informações que você pode passar são as que seguem e podem ser usadas mesmo que seja necessário de formas diferentes. Sobre InfiniteTap ou Tap ou Tap to Pay no iPhone que são nomes diferentes do mesmo produto: InfiniteTap (em aparelhos Android) ou Tap to Pay no iPhone (em aparelhos iPhone), também conhecido apenas como tap, é um método alternativo de captura de pagamentos. Com esse recurso, nossos clientes poderão usar seus smartphones como terminal POS, utilizando a tecnologia NFC para realizar vendas. As taxas do InfiniteTap são as mesmas da maquininha. É possível receber com antecipação em 1 dia útil, no plano Receba na Hora ou sem antecipação, também é possível conferir as taxas diretamente por este link: https://www.infinitepay.io/taxas. Quem pode usar? O InfiniteTap está disponível para pessoas jurídicas (com CNPJ) e pessoas físicas (com CPF). Clientes com CPF podem se cadastrar gratuitamente para utilizar o InfiniteTap em nosso site ou aplicativo. O usuário deve conceder todas as permissões necessárias para utilizar o produto. Baixar o app InfinitePay nas lojas oficiais: Play Store para Android; App Store para iOS; Confirmar sua identidade: Ativar o NFC: para poder capturar os dados do cartão; Ativar localização e garantir pemissões necessárias: para adicionar mais segurança nas vendas e ter essas informações armazendas nos metadados da transação; Desativar modo de desenvolvedor: para evitar possíveis ataques de usuários mal intencionados em nossos sistemas. Para usar o InfiniteTap, é preciso ter um smartphone com: Tecnologia NFC; Android 10 ou superior. O celular precisa ser Android acima da versão 10 e ter NFC, caso contrário não aparecerá  o InfiniteTap nas opções de geração de cobrança. É muito improvável que smartphones lançados recentemente não possuam NFC. Smartphones podem ter um limite de versão do sistema operacional. Por isso, é importante verificar se o aparelho consegue chegar pelo menos na versão 10 do Android. Os dispositivos compatíveis com o Tap to Pay incluem: iPhone XS e modelos posteriores; iOS atualizado. Aconselhamos que vejas as taxas unicamente pelo site por conter informações mais detalhadas. InfiniteLink ou link de pagamento são dois nomes do mesmo produto: O InfiniteLink é o nosso link de pagamento feito para os clientes venderem online e à distância com muita praticidade. Apesar de o InfiniteLink estar disponível para PJ e PF, o limite de valor cobrado por transação é diferente para os dois casos. Clientes PJ: até R$ 50 mil. Clientes PF: até R$ 3 mil. As taxas cobradas no InfiniteLink são diferentes da maquininha no plano D+1. Lembrando que todas as taxas de vendas em cartão não presente são associados com cartão de crédito. O pagamento com cartão de débito não é aceito em vendas online. Veja como nosso cliente pode criar e enviar um link de pagamento usando o App InfinitePay. 1 Acesse o App InfinitePay com o telefone cadastrado; 2 Na Home, selecione a opção ‘Enviar cobrança'; 3 Selecione a opção Link de pagamento; 4 Digite o valor a ser cobrado; 5 Defina o número máximo de parcelas que o cliente pode pagar; 6 Compartilhe a cobrança pelo WhatsApp ou copie o link para enviar. Para repassar taxa utilizando o InfiniteLink  gerado em nosso App, é ncessário primeiro abrir a calculadora do App InfinitePay e fazer a simulação da sua venda, incluindo o valor, número de parcelas, bandeira e ativando o botão “Repassar Taxas”. Feito isso basta clicar no botão “Cobrar”para que o link seja gerado já com o valor de repasse da taxa para o cliente final (pagador). É possível pagar um link de duas formas: baixando nosso aplicativo ou diretamente em um navegador. InfiniteLink convencional gerado via aplicativo tem suas informações carregadas diretamente na URL e, portanto, não possui expiração. Já o link de pagamento gerado no SuperCobra em nossa Conta Premium permite que o cliente defina sua própria data de expiração."},
          {"role": "user", "content": Body}
        ]
    )

    chat_response = response.choices[0].message.content

    max_length = 1000
    while len(chat_response) > 0:
        split_index = chat_response.rfind('\n', 0, max_length)
        if split_index == -1 or split_index == 0:
            split_index = max_length

        message_part = chat_response[:split_index].strip()
        send_message(sender_number, message_part)

        chat_response = chat_response[split_index:].strip()

    return ""
