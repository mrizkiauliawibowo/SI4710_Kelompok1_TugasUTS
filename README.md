# Food Delivery System - Kelompok 01

Sistem food delivery berbasis microservices menggunakan Flask dan Python.

## Struktur Project

```
food_delivery_system/
├── microservices/
│   ├── api-gateway/          # API Gateway untuk routing request
│   └── service-template/     # Template untuk membuat service baru
├── scripts/
│   ├── setup.sh             # Script untuk setup environment
│   └── run-all.sh           # Script untuk menjalankan semua service
└── README.md
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