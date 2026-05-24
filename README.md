# Kios AI

AI-powered customer service and inventory management for retail kiosk networks. Handles WhatsApp customer interactions, processes natural language orders, manages multi-location stock, and generates daily business intelligence.

## Overview

Built for a network of 30+ retail kiosks in Indonesia. Replaces manual customer service with intelligent agents that understand Bahasa Indonesia (including regional dialects and informal language).

```
Customer (WhatsApp)
        │
        ▼
┌─────────────────────────────────────────┐
│            Kios AI Platform              │
│                                          │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │   NLU    │  │ Handler  │  │Response││
│  │  Agent   │─▶│  Agent   │─▶│ Agent  ││
│  │          │  │          │  │        ││
│  │ Classify │  │ Process  │  │Generate││
│  │ intent   │  │ action   │  │ reply  ││
│  └──────────┘  └──────────┘  └────────┘│
│        │              │                  │
│        ▼              ▼                  │
│  ┌──────────┐  ┌──────────────────┐    │
│  │ Inventory │  │ Payment/Logistics│    │
│  │   API     │  │     Gateway      │    │
│  └──────────┘  └──────────────────┘    │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────┐
│ Nightly Analytics│
│ - Sales patterns │
│ - Restock alerts │
│ - P&L reports    │
└─────────────────┘
```

## Features

- **WhatsApp Integration** — Direct customer interaction via WhatsApp Business API
- **Bahasa Indonesia NLU** — Understands formal, informal, and regional dialect variations
- **Intent Classification** — Product inquiry, order placement, complaint, delivery tracking, promo inquiry
- **Multi-location Inventory** — Real-time stock across 30+ kiosks with auto-restock alerts
- **Payment Processing** — QRIS, bank transfer, e-wallet (GoPay, OVO, Dana, ShopeePay)
- **Predictive Restocking** — ML-based demand forecasting per location per SKU
- **Daily Reports** — Auto-generated P&L, top sellers, stock alerts via WhatsApp to owners
- **Human Escalation** — Automatic handoff for edge cases with full context

## Quick Start

```bash
pip install -r requirements.txt
cp config/config.example.yaml config/config.yaml
# Configure WhatsApp Business API, LLM keys, and database
python src/main.py
```

## Architecture

### Agents

1. **NLU Agent** — Classifies customer intent and extracts entities (product name, quantity, location)
2. **Handler Agent** — Executes business logic (check stock, create order, track delivery)
3. **Response Agent** — Generates contextually appropriate reply in customer's language style
4. **Analytics Agent** — Nightly batch processing for business intelligence

### Integrations

- WhatsApp Business API (via Fonnte/Wablas)
- Payment: Midtrans (QRIS, VA, e-wallet)
- Logistics: JNE, J&T, SiCepat API
- Inventory: Custom PostgreSQL + Redis cache
- Accounting: Jurnal.id sync

## Configuration

```yaml
# config/config.yaml
llm:
  provider: mimo
  model: mimo-v2.5-reasoning
  base_url: https://api.xiaomimimo.com/v1
  api_key: ${MIMO_API_KEY}

whatsapp:
  provider: fonnte
  api_key: ${FONNTE_API_KEY}
  webhook_url: https://your-domain.com/webhook/wa

inventory:
  database_url: ${DATABASE_URL}
  redis_url: ${REDIS_URL}
  low_stock_threshold: 5

analytics:
  schedule: "0 22 * * *"  # Run at 10 PM daily
  report_recipients:
    - "+6281234567890"  # Owner 1
    - "+6281234567891"  # Owner 2
```

## Example Interactions

```
Customer: "Kak ada stok case iPhone 15 warna hitam ga?"
Bot: "Hai kak! Case iPhone 15 hitam ready stock ya di kios Cimahi 3 pcs, 
      kios Bandung 1 pcs. Harga 85rb. Mau order kak?"

Customer: "Iya 2 pcs dong kirim ke rumah"
Bot: "Siap kak! 2x Case iPhone 15 Hitam = 170rb.
      Ongkir ke alamat kakak berapa ya? Boleh share alamat lengkapnya?"

Customer: "Jl Merdeka 45 Bandung 40115"  
Bot: "Ongkir JNE REG ke Bandung: 9rb. Total 179rb.
      Bayar via QRIS/transfer/e-wallet? Aku generate link bayarnya ya kak"
```

## Token Usage

| Component | Tokens/interaction | Daily (200 interactions) |
|-----------|-------------------|--------------------------|
| NLU Classification | ~200 | 40K |
| Handler Reasoning | ~500 | 100K |
| Response Generation | ~300 | 60K |
| **Subtotal (CS)** | **~1,000** | **~2M** |
| Nightly Analytics | - | ~1M |
| **Total Daily** | - | **~3M** |

## Deployment

```bash
# Docker
docker-compose up -d

# Or systemd
sudo cp kios-ai.service /etc/systemd/system/
sudo systemctl enable --now kios-ai
```

## License

MIT
