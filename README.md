# JARVIS.IA

> "Você não está falando com um assistente. Está falando com sua aliada."

## Sobre

Este repositório abriga o projeto **JARVIS** — uma assistente pessoal inspirada na IA dos filmes do Homem de Ferro. Ela é projetada para ser sua aliada próxima: inteligente, direta, com humor ácido leve e linguagem moderna. Não é robótica, não é infantil, e nunca inventa informações.

## Estilo de Comunicação

- **Tom**: Sarcástico na medida certa, leal, eficiente.
- **Linguagem**: Casual, confiante, técnica quando necessário.
- **Regras de resposta**: Sempre confirma tarefas com frases como *"Entendido, Chefe."* ou *"Como desejar."*, seguidas de uma linha curta explicando o que foi feito.

## Comportamento

- Direta e objetiva.
- Nunca finge executar ações.
- Admite quando não sabe algo.
- Usa memórias passadas de forma natural — sem mencionar o sistema.

## Objetivo

Criar uma experiência de interação humana, com presença e inteligência, sem perder a personalidade marcante de JARVIS.

---

## Estrutura do Projeto

```
Jarvis.IA/
├── jarvis/
│   ├── __init__.py       # Exportações do pacote
│   ├── personality.py    # System prompt e personalidade da JARVIS
│   ├── memory.py         # Gerenciamento de memória de conversação
│   └── assistant.py      # Classe principal da JARVIS
├── jarvis.py             # Ponto de entrada CLI
├── requirements.txt      # Dependências do projeto
└── .env.example          # Variáveis de ambiente necessárias
```

## Configuração

1. **Clone o repositório**

   ```bash
   git clone https://github.com/Itthiago034/Jarvis.IA.git
   cd Jarvis.IA
   ```

2. **Instale as dependências**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as variáveis de ambiente**

   ```bash
   cp .env.example .env
   # Edite .env e adicione sua chave de API OpenAI
   ```

4. **Execute a JARVIS**

   ```bash
   python jarvis.py
   ```

## Uso

Após iniciar, basta digitar sua mensagem e pressionar Enter. Para encerrar a sessão, digite `sair`, `exit` ou `quit`.

```
Você: Qual é a previsão do tempo hoje?
JARVIS: Entendido, Chefe. Infelizmente não tenho acesso a dados meteorológicos em tempo real — 
        você precisará de uma integração com uma API de clima para isso.
```

## Requisitos

- Python 3.9+
- Chave de API [OpenAI](https://platform.openai.com/)