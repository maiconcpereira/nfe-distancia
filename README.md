# 📦 Calculadora de Distância NF-e

Calcula a distância entre o endereço do **emitente** e do **destinatário**
de uma nota fiscal eletrônica (NF-e) usando a Google Maps Distance Matrix API.

---

## ✅ Pré-requisitos

- Python 3.8+
- Uma **Google Maps API Key** com as APIs habilitadas:
  - Distance Matrix API
  - Geocoding API (recomendado)

---

## 🔑 Como obter a Google Maps API Key

1. Acesse https://console.cloud.google.com/
2. Crie um projeto (ou use um existente)
3. Vá em **APIs & Services → Enable APIs**
4. Ative: **Distance Matrix API** e **Geocoding API**
5. Vá em **Credentials → Create Credentials → API Key**
6. Copie a chave gerada

---

## 🚀 Instalação

```bash
pip install -r requirements.txt
```

---

## 💻 Opção 1 — Linha de Comando

```bash
python app.py nota_fiscal.xml SUA_API_KEY_AQUI
```

**Exemplo de saída:**
```
============================================================
  CALCULADORA DE DISTÂNCIA - NF-e
============================================================

📄 Lendo XML: nota.xml

🏭 EMITENTE: EMPRESA ABC LTDA (CNPJ: 00.000.000/0001-00)
   Endereço: Rua das Flores, 100, Centro, São Paulo, SP, 01310-100, Brasil

📦 DESTINATÁRIO: EMPRESA XYZ SA (CNPJ: 11.111.111/0001-11)
   Endereço: Av. Atlântica, 500, Copacabana, Rio de Janeiro, RJ, 22070-000, Brasil

🗺️  Consultando Google Maps...

============================================================
  RESULTADO
============================================================
  📍 Origem  : Rua das Flores, 100 - Centro, São Paulo - SP
  📍 Destino : Av. Atlântica, 500 - Copacabana, Rio de Janeiro - RJ
  📏 Distância: 430 km (430.000 m)
  ⏱️  Duração : 5 horas 20 min
============================================================
```

---

## 🌐 Opção 2 — Interface Web

```bash
python web_app.py
```

Depois abra: **http://localhost:5000**

Na interface você pode:
- Fazer upload do XML da NF-e
- Inserir a API Key
- Ver a distância e tempo estimado de viagem

---

## 📋 Estrutura dos Arquivos

```
├── app.py           # Script de linha de comando
├── web_app.py       # Interface web (Flask)
├── requirements.txt # Dependências
└── README.md        # Este arquivo
```

---

## ⚠️ Observações

- O XML deve ser um arquivo NF-e válido (padrão SEFAZ)
- Funciona com arquivos XML simples ou dentro de `nfeProc` (retorno da SEFAZ)
- A precisão da distância depende da qualidade do endereço na nota fiscal
- A API do Google Maps tem uma cota gratuita de 200 USD/mês (~40.000 chamadas)
