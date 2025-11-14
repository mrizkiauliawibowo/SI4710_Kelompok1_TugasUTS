# 🍕 Food Delivery System - Kelompok 01 - SI4710

Sistem food delivery berbasis microservices menggunakan Flask dan Python dengan arsitektur modern yang memungkinkan setiap anggota tim mengembangkan service secara independen.

---

## 🎯 **TEAM ASSIGNMENTS**

| Nama | Port | Service | 
|------|------|---------|
| **Arthur Budi Maharesi** | 5001 | User Service |
| **M.Rizki Aulia Wibowo** | 5002 | Restaurant Service |
| **Nadia Miranda** | 5003 | Order Service |
| **Muhammad Aydin Yusuf** | 5004 | Delivery Service |
| **Akchmad Reza Zandri** | 5005 | Payment Service |

---

## 📁 **STRUKTUR PROJECT LENGKAP**

```
food_delivery_system/
├── docs/
│                       
├── frontend/                      # Frontend web application
│   ├── index.html                # Halaman utama
│   ├── restaurant.html           # Halaman restaurant
│   ├── cart.html                 # Halaman keranjang
│   ├── checkout.html             # Halaman checkout
│   ├── order-tracking.html       # Halaman tracking order
│   ├── admin.html                # Halaman admin
│   └── js/                       # JavaScript modules
│       ├── main.js               # Main JavaScript file
│       ├── home.js               # Home page logic
│       ├── restaurant.js         # Restaurant page logic
│       ├── cart.js               # Cart page logic
│       ├── checkout.js           # Checkout page logic
│       ├── order-tracking.js     # Order tracking logic
│       └── admin.js              # Admin page logic
│
├── instance/
│   ├── delivery_service.db
│   ├── order_service.db
│   ├── payment_service.db
│   ├── restaurant_service.db
│   ├── user_service.db
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
│
├── .gitignore                   # Git ignore file
└── README.md                    # 📖 This file
```

---

## 🚀 **QUICK START GUIDE**

### **Langkah 1: Setup Environment**
```bash
# Clone repository (jika belum)
git clone https://github.com/aturrr62/kelompok01_food_delivery_system
cd food-delivery-system

# Setup environment (jalanin di root directory)
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### **Langkah 2: Jalankan System**
```bash
# Mulai API Gateway dulu
./scripts/run-all.sh

# 🚨 IMPORTANT: Setiap anggota tim jalankan service mereka masing-masing:
```

---

## 👥 **PANDUAN UNTUK SETIAP ANGGOTA TIM**

### 🔵 **Arthur (5001) - User Service**
```bash
# Buka terminal baru, jalankan:
cd microservices/user-service
python app.py

# Service akan berjalan di: http://localhost:5001
# API akan tersedia di: http://localhost:5000/users/*
```

**Fungsi User Service:**
- User registration & login
- Profile management
- Authentication & authorization
- User preferences

---

### 🟢 **Rizki (5002) - Restaurant Service**
```bash
# Buka terminal baru, jalankan:
cd microservices/restaurant-service
python app.py

# Service akan berjalan di: http://localhost:5002
# API akan tersedia di: http://localhost:5000/restaurants/*
```

**Fungsi Restaurant Service:**
- Restaurant registration & management
- Menu management
- Restaurant categories
- Operating hours & location

---

### 🟡 **Nadia (5003) - Order Service**
```bash
# Buka terminal baru, jalankan:
cd microservices/order-service
python app.py

# Service akan berjalan di: http://localhost:5003
# API akan tersedia di: http://localhost:5000/orders/*
```

**Fungsi Order Service:**
- Order creation & management
- Order tracking
- Order history
- Order status updates

---

### 🟠 **Aydin (5004) - Delivery Service**
```bash
# Buka terminal baru, jalankan:
cd microservices/delivery-service
python app.py

# Service akan berjalan di: http://localhost:5004
# API akan tersedia di: http://localhost:5000/deliveries/*
```

**Fungsi Delivery Service:**
- Delivery assignment
- Driver tracking
- Real-time location updates
- Delivery status

---

### 🔴 **Reza (5005) - Payment Service**
```bash
# Buka terminal baru, jalankan:
cd microservices/payment-service
python app.py

# Service akan berjalan di: http://localhost:5005
# API akan tersedia di: http://localhost:5000/payments/*
```

**Fungsi Payment Service:**
- Payment processing
- Transaction management
- Payment history
- Refund handling

---

## 🌐 **ACCESS POINTS**

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5000 | Web Interface |
| **API Gateway** | http://localhost:5000/health | Health Check |
| **User Service** | http://localhost:5001 | Arthur |
| **Restaurant Service** | http://localhost:5002 | Rizki |
| **Order Service** | http://localhost:5003 | Nadia |
| **Delivery Service** | http://localhost:5004 | Aydin |
| **Payment Service** | http://localhost:5005 | Reza |

---

## 🔄 **API ROUTING**

API Gateway akan me-route request berdasarkan URL pattern:

- `GET/POST /users/*` → User Service (Arthur)
- `GET/POST /restaurants/*` → Restaurant Service (Rizki)  
- `GET/POST /orders/*` → Order Service (Nadia)
- `GET/POST /deliveries/*` → Delivery Service (Aydin)
- `GET/POST /payments/*` → Payment Service (Reza)

---

## 🛠️ **DEVELOPMENT GUIDE**

### **Membuat Service Baru:**
1. Copy `microservices/service-template/` folder
2. Rename sesuai nama service
3. Ubah port di `app.py` (line 73)
4. Modifikasi model di `app.py` (line 13-25)
5. Ubah endpoint dan nama service
6. Update `requirements.txt` jika perlu dependencies tambahan

### **Service Requirements:**
Setiap service WAJIB memiliki:
- ✅ Endpoint `/health` untuk health check
- ✅ Menggunakan port yang sudah ditentukan
- ✅ Database model dengan method `to_dict()`
- ✅ CRUD endpoints (GET, POST, PUT, DELETE)
- ✅ Error handling yang proper
- ✅ Logging yang informatif

---

## 🚨 **TROUBLESHOOTING**

### **Port sudah digunakan:**
```bash
# Cari process yang menggunakan port
lsof -i :5001  # Ganti dengan port yang bermasalah

# Hentikan process
kill -9 <PID>
```

### **Database error:**
```bash
# Hapus database lama dan buat ulang
rm -f microservices/*/database.db
python app.py  # di masing-masing service
```

### **Dependencies error:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

---

## ✅ **HEALTH CHECK**

Untuk mengecek semua service berfungsi:
```bash
# Cek API Gateway
curl http://localhost:5000/health

# Cek semua service
for port in 5001 5002 5003 5004 5005; do
  echo "Checking port $port:"
  curl http://localhost:$port/health
  echo ""
done
```

---

---

**🎉 Happy Coding! Semangat buat food delivery system terbaik! 🚀**
