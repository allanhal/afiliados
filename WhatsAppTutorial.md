# Tutorial: Como Automatizar o Envio de Mensagens em Grupos do WhatsApp

Para enviar mensagens via WhatsApp por automação, especialmente em grupos para os quais você deseja mandar links de afiliados, existem **duas principais abordagens**. A oficial pela Meta, e as não oficiais (que espelham o WhatsApp Web).

Para grupos de ofertas e afiliados, a **Abordagem Não Oficial** é a mais recomendada, porque:
1. A API oficial da Meta tem muitas regras de "opt-in" e cobra por algumas conversas iniciadas. Além disso, gerenciar grupos é mais rígido.
2. As APIs não oficiais simulam você abrindo o "WhatsApp Web" no navegador, escaneando o QR Code com o seu celular, permitindo enviar mensagens livremente para qualquer grupo em que você já está.

Abaixo, detalho como configurar a **melhor opção gratuita e não-oficial** para testes com Node.js usando a biblioteca `whatsapp-web.js` ou utilizando o serviço `Evolution API`.

---

## 1. Abordagem Recomendada: Criando um Robô em Node.js (whatsapp-web.js)

A biblioteca `whatsapp-web.js` abre um navegador oculto e conecta-se via WhatsApp Web. Essa é uma opção bem popular para criar chatbots gratuitos usando seu próprio número.

### Passo 1: Pré-requisitos
- Ter o **Node.js** instalado (versão 18+ de preferência).
- Ter o **Google Chrome** instalado na sua máquina (onde o robô vai rodar).

### Passo 2: Inicializando o projeto

Crie uma pasta, abra o terminal e inicialize o Node:

```bash
mkdir bot-whatsapp
cd bot-whatsapp
npm init -y
npm install whatsapp-web.js qrcode-terminal
```

### Passo 3: O Código do Bot

Crie um arquivo chamado `index.js` e adicione o código abaixo:

```javascript
const qrcode = require('qrcode-terminal');
const { Client, LocalAuth } = require('whatsapp-web.js');

// O LocalAuth salva sua sessão para não precisar escanear o QR Code toda vez.
const client = new Client({
    authStrategy: new LocalAuth()
});

// Quando o sistema solicitar, gere e mostre o QR Code no terminal
client.on('qr', (qr) => {
    console.log('Escaneie este QR Code com o seu WhatsApp:');
    qrcode.generate(qr, { small: true });
});

// Quando conectar com sucesso
client.on('ready', () => {
    console.log('✅ Conectado com sucesso ao WhatsApp!');
    
    // Agora o bot já está pronto para mandar mensagem
    // Se você tiver o ID de um grupo (ex: 120363041...xyz@g.us), pode mandar ali.
    const numeroOuGrupoId = "120363XXXXXXXXXXXX@g.us"; 
    const textoMensagem = "🛒 *Oferta Especial!*\nCompre aqui: https://amzn.to/exemplo";

    client.sendMessage(numeroOuGrupoId, textoMensagem)
        .then(response => {
            console.log("Mensagem enviada no grupo!");
        })
        .catch(err => {
            console.error("Erro ao enviar mensagem", err);
        });
});

// Evento para ler as mensagens recebidas
client.on('message', message => {
    console.log(`Mensagem de ${message.from}: ${message.body}`);
});

// Inicializando o cliente
client.initialize();
```

### Passo 4: Rodando e Encontrando o ID do seu Grupo

1. Rode `node index.js`.
2. Um QR Code vai aparecer no seu terminal. Acesse WhatsApp no celular > Aparelhos conectados > Conectar aparelho e escaneie o código.
3. Para **descobrir o ID de um grupo** específico, no evento `client.on('message', message => {...})` coloque um `console.log(message.from)` e mande uma mensagem no grupo teste pelo celular. O terminal irá mostrar o ID desse grupo (sempre termina com `@g.us`).
4. Troque a variável `numeroOuGrupoId` no código para o ID que apareceu no terminal e você já pode disparar suas mensagens de dentro do seu scraper.

---

## 2. Abordagem Profissional em Nuvem: Evolution API / Z-API

Se o seu projeto crescer e você não quiser deixar o terminal aberto o tempo todo, você pode usar uma API rodando na nuvem.
Existem duas formas:

1. **Evolution API (Gratuito / Open Source)**: Um projeto brasileiro incrível. Você sobe ele no seu próprio servidor (Railway, Render, VPS) ou no Docker, e ele cria "instâncias" que você acessa via API REST padrão. Você manda um POST (`/message/sendText`) para enviar a mensagem, podendo chamar essa API até do seu script Python (que criamos para a Amazon).
2. **Serviços Pagos (Z-API, ChatPro, MegaAPI)**: Custam em média de R$ 90 a R$ 150/mês. Eles já dão tudo pronto, só te passam o link HTTP que você vai chamar e o QR Code aparece num painel prático deles para escaneamento.

### Como isso se integra com nosso Scraper Python?
Se você for por este caminho de API (seja instalando a Evolution API ou pagando serviço), no lugar da chamada `requests.post()` do Telegram que fizemos antes, basta trocar a URL pela URL do provedor do WhatsApp. 

Exemplo prático de como seria o envio em Python usando uma API padrão como Evolution ou Z-API:

```python
import requests

def send_whatsapp(message):
    url = "https://URL_DA_API/message/sendText"
    headers = {
        "apikey": "sua-chave-secreta"
    }
    payload = {
        "number": "120363...ID-DO-GRUPO@g.us",
        "text": message
    }
    requests.post(url, json=payload, headers=headers)
```
