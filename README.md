<div align="center">

# Kios AI

AI-powered customer service and inventory management for retail kiosk networks via WhatsApp.

[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)]()
[![WhatsApp](https://img.shields.io/badge/WhatsApp-API-25D366?style=flat-square&logo=whatsapp&logoColor=white)]()

</div>

---

## Overview

Built for a network of 30+ retail kiosks in Indonesia. Replaces manual customer service with intelligent agents that understand Bahasa Indonesia (including regional dialects and informal language).

## Architecture

```
Customer (WhatsApp)
    |
    v
+------------------+
| WhatsApp Bridge  |  <-- message routing
+--------+---------+
         |
    +----+----+----+
    |         |    |
    v         v    v
+------+ +------+ +------+
| CS   | | Order| | Stock|  <-- AI agents
| Agent| | Proc.| | Mgmt |
+--+---+ +--+---+ +--+---+
   |        |        |
   +--------+--------+
            |
            v
    +---------------+
    | Inventory DB  |  <-- multi-location
    | + Analytics   |     stock tracking
    +---------------+
```

## Features

- **Natural Language Orders** — "masukin 3 indomie sama 2 aqua" → structured order
- **Multi-location Stock** — real-time inventory across 30+ kiosks
- **Daily Reports** — automated sales and stock summaries
- **Customer History** — purchase patterns and preferences

## Quick Start

```bash
pip install -r requirements.txt
docker-compose up -d  # starts WhatsApp bridge + DB
python -m src.server
```

## License

MIT
