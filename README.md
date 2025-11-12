# Food Delivery System - Kelompok 01

Sistem food delivery berbasis microservices menggunakan Flask dan Python.

## Struktur Project

```
food_delivery_system/
├── frontend/                      # Frontend web application
│   ├── index.html                # Halaman utama
│   └── js/                       # JavaScript modules
│       ├── main.js               # Main JavaScript file
│       └── home.js               # Home page logic
│
├── microservices/                # Backend microservices
│   ├── api-gateway/              # 🚀 API Gateway (Port 5000)
│   │   ├── app.py                # Flask app untuk routing
│   │   ├── requirements.txt      # Dependencies
│   │   └── run.sh               # Run script
│   │
│   ├── service-template/         # 📋 Template untuk service baru
│   │   ├── app.py                # Template Flask app
│   │   ├── requirements.txt      # Dependencies
│   │   ├── run.sh               # Run script
│   │   └── README.md            # Template documentation
│   │
│   ├── user-service/             # 👤 ARTHUR (5001)
│   │   ├── app.py                # User management & auth
│   │   ├── requirements.txt      # Dependencies
│   │   └── run.sh               # Run script
│   │
│   ├── restaurant-service/       # 🍽️ rizki (5002)
│   │   ├── app.py                # Restaurant & menu management
│   │   ├── requirements.txt      # Dependencies
│   │   └── run.sh               # Run script
│   │
│   ├── order-service/            # 📦 Nadia (5003)
│   │   ├── app.py                # Order management
│   │   ├── requirements.txt      # Dependencies
│   │   └── run.sh               # Run script
│   │
│   ├── delivery-service/         # 🚚 aydin (5004)
│   │   ├── app.py                # Delivery tracking
│   │   ├── requirements.txt      # Dependencies
│   │   └── run.sh               # Run script
│   │
│   └── payment-service/          # 💳 reza (5005)
│       ├── app.py                # Payment processing
│       ├── requirements.txt      # Dependencies
│       └── run.sh               # Run script
│
├── scripts/                      # Utility scripts
│   ├── setup.sh                 # 🛠️ Setup environment
│   └── run-all.sh               # 🚀 Start all services
│
├── logs/                        # Log files (auto-generated)
│   ├── gateway.log             # API Gateway logs
│   └── service-*.log           # Individual service logs
│
├── .gitignore                   # Git ignore file
└── README.md                    # 📖 This file
```
```

## Services

- **API Gateway** (Port 5000) - Router utama untuk semua request
- **User Service** (Port 5001) - Manajemen user dan autentikasi
- **Restaurant Service** (Port 5002) - Manajemen restaurant dan menu
- **Order Service** (Port 5003) - Manajemen order dan transaksi
- **Delivery Service** (Port 5004) - Manajemen pengiriman
- **Payment Service** (Port 5005) - Manajemen pembayaran

## Setup

1. Clone repository ini
2. Jalankan setup script:
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

3. Jalankan semua services:
   ```bash
   ./scripts/run-all.sh
   ```

4. Akses aplikasi di: http://localhost:5000

## API Gateway

API Gateway berfungsi sebagai entry point tunggal untuk semua request. Request akan di-route ke service yang sesuai berdasarkan URL pattern:

- `/users/*` → User Service
- `/restaurants/*` → Restaurant Service  
- `/orders/*` → Order Service
- `/deliveries/*` → Delivery Service
- `/payments/*` → Payment Service

## Health Check

Untuk mengecek status semua services:
```
GET /health
```

## Pengembangan

Gunakan `service-template` sebagai template untuk membuat service baru. Setiap service harus:

1. Mengimplementasikan endpoint `/health`
2. Menggunakan port yang sudah ditentukan
3. Mengikuti struktur yang sama dengan template

## Tim Pengembang

- **Arthur** - User Service (Port 5001)
- **Rizki** - Restaurant Service (Port 5002)  
- **Nadia** - Order Service (Port 5003)
- **Aydin** - Delivery Service (Port 5004)
- **Reza** - Payment Service (Port 5005)
