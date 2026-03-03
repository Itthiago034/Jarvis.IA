# 🤖 JARVIS - Assistente Pessoal de Voz

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![LiveKit](https://img.shields.io/badge/LiveKit-Realtime-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

*"Você não está falando com um assistente. Está falando com sua aliada."*

</div>

---

## 📋 Sobre

JARVIS é uma assistente pessoal de voz inspirada na IA dos filmes do Homem de Ferro. Ela é projetada para ser sua aliada próxima: inteligente, direta, com humor ácido leve e linguagem moderna.

### ✨ Características
- 🎙️ **Comunicação por voz** em tempo real com LiveKit
- 🧠 **Memória persistente** - lembra de conversas anteriores
- 🔌 **Sistema de plugins** - funcionalidades expansíveis
- 🎯 **Personalidade única** - sarcástica na medida certa

---

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.11+
- Conta no [LiveKit](https://livekit.io)
- Conta no [Google AI Studio](https://aistudio.google.com)
- Conta no [Mem0](https://mem0.ai)

### Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/Jarvis.IA.git
cd Jarvis.IA

# Crie o ambiente virtual
python -m venv venv

# Ative o ambiente (Windows)
.\venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas chaves
```

### Executando

```bash
# Método 1: Script bat (Windows)
.\Jarvis.bat

# Método 2: Direto com Python
python run.py dev
```

---

## 🔌 Plugins Disponíveis

| Plugin | Descrição | Exemplos de Comando |
|--------|-----------|---------------------|
| 🌤️ **Clima** | Previsão do tempo | "Como está o tempo?", "Vai chover?" |
| 🎵 **Spotify** | Controle de música | "Toca música", "Próxima", "Pausa" |
| 💻 **Sistema** | Info do PC | "Quanta bateria?", "Uso de CPU" |
| 🕐 **Data/Hora** | Informações temporais | "Que horas são?", "Que dia é hoje?" |
| 📱 **Apps** | Abrir aplicativos | "Abre o Chrome", "Abrir YouTube" |

### Configurando Plugins

Edite `config/plugins.yaml` para habilitar/desabilitar plugins ou configurar APIs.

---

## 📁 Estrutura do Projeto

```
Jarvis.IA/
├── src/
│   └── jarvis/
│       ├── agent.py          # Core do agente de voz
│       ├── prompts.py        # Instruções de personalidade
│       └── plugins/          # Sistema de plugins
│           ├── base.py       # Classe base
│           ├── manager.py    # Gerenciador
│           ├── weather.py    # Plugin de clima
│           ├── spotify.py    # Plugin do Spotify
│           ├── system.py     # Plugin de sistema
│           └── apps.py       # Plugin de aplicativos
├── config/
│   └── plugins.yaml          # Configuração de plugins
├── assets/
│   └── images/               # Recursos visuais
├── docs/                     # Documentação
├── tests/                    # Testes
├── .github/
│   ├── workflows/ci.yml      # CI/CD
│   └── dependabot.yml        # Updates automáticos
├── run.py                    # Ponto de entrada
├── requirements.txt          # Dependências
└── .env                      # Variáveis (não commitado)
```

---

## 🎭 Personalidade

### Tom de Comunicação
- **Sarcástica** na medida certa
- **Leal** e prestativa
- **Inteligente** e rápida
- Nunca infantil ou agressiva

### Frases de Confirmação
- *"Entendido, Chefe."*
- *"Farei isso, Senhor."*
- *"Como desejar."*
- *"Ok, parceiro."*

---

## 🛠️ Desenvolvimento

### Criando um Novo Plugin

```python
from jarvis.plugins.base import JarvisPlugin, PluginContext, PluginResponse

class MeuPlugin(JarvisPlugin):
    name = "Meu Plugin"
    description = "Faz algo incrível"
    trigger_phrases = ["fazer algo", "execute algo"]
    
    async def execute(self, context: PluginContext) -> PluginResponse:
        # Sua lógica aqui
        return PluginResponse(message="Feito, chefe!")
```

### Executando Testes

```bash
pip install pytest pytest-asyncio
pytest tests/ -v
```

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🤝 Contribuindo

1. Faça um Fork do projeto
2. Crie sua Feature Branch (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona NovaFeature'`)
4. Push para a Branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

---

<div align="center">

Feito com ❤️ por Thiago

</div>
