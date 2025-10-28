# Bot de Finanças WhatsApp

Sistema automatizado para controle financeiro pessoal via WhatsApp, com registro de despesas e receitas em planilha Excel e visualização de insights através de um dashboard interativo.

## 📋 Sobre o Projeto

Este bot permite que você gerencie suas finanças pessoais simplesmente enviando mensagens pelo WhatsApp no formato:
 - despesa 100 mercado
 - receita 3000 salário

Os dados são automaticamente registrados em uma planilha Excel e podem ser visualizados em tempo real através de um dashboard web construído com Streamlit.


## Arquitetura

```bash
WhatsApp → Evolution API → Webhook (FastAPI) → Excel → Dashboard (Streamlit)
                ↓
        Docker (Postgres + Redis)
                ↓
            Ngrok (URL Pública)

```

## Tecnologias Utilizadas

* **Python 3.x**
* **FastAPI** - API webhook para receber mensagens
* **Streamlit** - Dashboard de visualização
* **Pandas** - Manipulação de dados
* **Evolution API** - Integração com WhatsApp
* **Docker & Docker Compose** - Containerização
* **PostgreSQL** - Banco de dados da Evolution API
* **Redis** - Cache da Evolution API
* **Ngrok** - Túnel para expor webhook publicamente
* **openpyxl** - Leitura/escrita de arquivos Excel


## Estrutura do Projeto
```bash
projeto/
├── app.py                 # Dashboard Streamlit
├── main.py               # API FastAPI (webhook)
├── docker-compose.yml    # Configuração Docker
├── .env                  # Variáveis de ambiente
├── .gitignore           
├── requirements.txt      # Dependências Python
└── data/
    └── gastos.xlsx       # Planilha de dados (gerada automaticamente)
```

## Pré-requisitos

* Docker e Docker Compose instalados
* Python 3.8 ou superior
* Conta Ngrok (gratuita)
* Número de telefone para vincular ao WhatsApp


## 🔍 Funcionalidades

* ✅ Registro automático de despesas e receitas via WhatsApp
* ✅ Armazenamento em planilha Excel
* ✅ Dashboard interativo com métricas em tempo real
* ✅ Gráficos de gastos por categoria
* ✅ Histórico completo de lançamentos
* ✅ Cálculo automático de saldo
* ✅ Suporte a valores decimais (usando vírgula ou ponto)

## 📈 Próximas Melhorias

* Filtros por período (mês/ano)
* Exportação de relatórios em PDF
* Gráficos de evolução temporal
* Metas de gastos por categoria
* Notificações de limites excedidos
* Suporte a múltiplos usuários
* Backup automático dos dados


 ### 📄 Licença
Este projeto está sob a licença MIT.
 ### 🤝 Contribuindo
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.
 ### 📞 Contato
Para dúvidas ou sugestões, abra uma issue no repositório.