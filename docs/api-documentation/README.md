API Documentation - Food Delivery System (API Gateway)
Base URL

Semua request ke backend dilakukan melalui API Gateway: http://localhost:5000

Authentication

Login terlebih dahulu:
Method: POST
URL: /auth/login
Headers: Content-Type: application/json
Body:

{
  "username": "admin",
  "password": "admin123"
}

Response Example:

{
  "success": true,
  "access_token": "eyJ0eXAiOiJKV1QiLCJh...etc",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@fooddelivery.com",
    "role": "admin"
  },
  "message": "Login successful"
}


Simpan nilai access_token dari response.

Tambahkan header berikut untuk endpoint yang membutuhkan auth:

Authorization: Bearer <access_token>
Content-Type: application/json

1. System Endpoints (Gateway)
Health Check

Method: GET

URL: /health

Description: Mengecek status API Gateway dan daftar service yang terdeteksi

Response Example:

{
  "status": "healthy",
  "service": "api-gateway",
  "timestamp": "2025-11-14T10:30:00Z",
  "services": [
    "user-service",
    "restaurant-service",
    "order-service",
    "delivery-service",
    "payment-service"
  ],
  "version": "1.0.0"
}

API Home

Method: GET

URL: /

Description: Informasi umum API Gateway dan daftar endpoint penting

Response Example:

{
  "service": "Food Delivery System API Gateway",
  "version": "1.0.0",
  "description": "API Gateway untuk Food Delivery System Microservices",
  "endpoints": {
    "health": "/health",
    "documentation": "/api-docs/",
    "auth": {
      "login": "/auth/login",
      "register": "/auth/register",
      "verify": "/auth/verify"
    },
    "services": {
      "user-service": "/api/user-service/",
      "restaurant-service": "/api/restaurant-service/",
      "order-service": "/api/order-service/",
      "delivery-service": "/api/delivery-service/",
      "payment-service": "/api/payment-service/"
    }
  },
  "authentication": "JWT Bearer Token required for service endpoints"
}

2. Authentication Endpoints
Login
Method: POST
URL: /auth/login
Headers: Content-Type: application/json

Body:

{
  "username": "admin",
  "password": "admin123"
}


Response Example: (lihat bagian Authentication di atas)

Verify Token

Method: GET

URL: /auth/verify

Headers: Authorization: Bearer <access_token>

Description: Mengecek apakah JWT token masih valid

Response Example:

{
  "success": true,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@fooddelivery.com",
    "role": "admin"
  }
}

3. User Service (via API Gateway)

Semua endpoint User Service diakses melalui prefix:

/api/user-service/...

Get All Users

Method: GET

URL: /api/user-service/api/users

Headers: Authorization: Bearer <access_token>

Description: Mengambil daftar seluruh user

Response Example:

{
  "success": true,
  "data": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@fooddelivery.com",
      "full_name": "Admin User",
      "user_type": "admin",
      "is_deleted": false
    }
  ]
}

Create User

Method: POST

URL: /api/user-service/api/users

Headers:

Content-Type: application/json

Authorization: Bearer <access_token>

Body:

{
  "username": "testuser123",
  "email": "testuser123@example.com",
  "password": "SecurePass123!",
  "full_name": "Test User",
  "phone": "08123456789",
  "address": "Jl. Contoh No. 123",
  "user_type": "customer"
}


Response Example:

{
  "success": true,
  "data": {
    "id": 2,
    "username": "testuser123",
    "email": "testuser123@example.com",
    "full_name": "Test User",
    "user_type": "customer",
    "created_at": "2025-11-14T10:30:00Z"
  }
}

Get User by ID

Method: GET

URL: /api/user-service/api/users/1

Headers: Authorization: Bearer <access_token>

Description: Mengambil detail user berdasarkan ID

Update User

Method: PUT

URL: /api/user-service/api/users/1

Headers:

Content-Type: application/json

Authorization: Bearer <access_token>

Body:

{
  "full_name": "Updated User Name"
}

Soft Delete User

Method: DELETE

URL: /api/user-service/api/users/2/soft-delete (atau sesuai implementasi)

Headers: Authorization: Bearer <access_token>

4. Restaurant Service (via API Gateway)

Prefix:

/api/restaurant-service/...

Get All Restaurants

Method: GET

URL: /api/restaurant-service/api/restaurants

Description: Mengambil semua restoran yang terdaftar

Response Example:

{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Test Restaurant",
      "description": "A great test restaurant",
      "address": "Jl. Makan No. 1",
      "phone": "08123456789",
      "email": "restaurant@example.com"
    }
  ]
}

Create Restaurant

Method: POST

URL: /api/restaurant-service/api/restaurants

Headers:

Content-Type: application/json

Authorization: Bearer <access_token>

Body:

{
  "name": "Test Restaurant",
  "description": "A great test restaurant",
  "address": "123 Restaurant St",
  "phone": "0812-3456789",
  "email": "restaurant@example.com"
}

Get All Menu Items

Method: GET

URL: /api/restaurant-service/api/menu-items

Description: Mengambil seluruh menu item

Create Menu Item

Method: POST

URL: /api/restaurant-service/api/menu-items

Headers: Content-Type: application/json

Body:

{
  "restaurant_id": 1,
  "name": "Test Dish",
  "description": "A delicious test dish",
  "price": 50000,
  "category": "main",
  "is_vegetarian": false
}

5. Order Service (via API Gateway)

Prefix:

/api/order-service/...

Get All Orders

Method: GET

URL: /api/order-service/api/orders

Description: Mengambil semua order

Create Order

Method: POST

URL: /api/order-service/api/orders

Headers: Content-Type: application/json

Body:

{
  "user_id": 1,
  "restaurant_id": 1,
  "delivery_address": "Alamat pengiriman contoh",
  "total_amount": 150000,
  "delivery_fee": 10000,
  "items": [
    {
      "menu_item_id": 1,
      "quantity": 2,
      "price": 50000
    }
  ]
}


Response Example:

{
  "success": true,
  "data": {
    "id": 1,
    "user_id": 1,
    "restaurant_id": 1,
    "total_amount": 150000,
    "delivery_fee": 10000,
    "status": "pending",
    "items": [
      {
        "menu_item_id": 1,
        "quantity": 2,
        "price": 50000
      }
    ]
  }
}

6. Delivery Service (via API Gateway)

Prefix:

/api/delivery-service/...

Get All Deliveries

Method: GET

URL: /api/delivery-service/api/deliveries

Description: Mengambil seluruh data delivery

Create Delivery

Method: POST

URL: /api/delivery-service/api/deliveries

Headers: Content-Type: application/json

Body:

{
  "order_id": 1,
  "driver_name": "Test Driver",
  "driver_phone": "08123456789",
  "delivery_address": "Alamat pengiriman contoh",
  "estimated_time": 30
}

Track Delivery by Order

Method: GET

URL: /api/delivery-service/api/tracking/1

Description: Tracking pengiriman berdasarkan order_id

7. Payment Service (via API Gateway)

Prefix:

/api/payment-service/...

Get All Payments

Method: GET

URL: /api/payment-service/api/payments

Description: Mengambil seluruh data pembayaran

Create Payment

Method: POST

URL: /api/payment-service/api/payments

Headers: Content-Type: application/json

Body:

{
  "order_id": 1,
  "amount": 160000,
  "payment_method": "credit_card",
  "status": "pending"
}

Process Payment

Method: POST

URL: /api/payment-service/api/payments/1/process

Headers: Content-Type: application/json

Body:

{
  "status": "completed"
}


Response Example:

{
  "success": true,
  "data": {
    "id": 1,
    "order_id": 1,
    "amount": 160000,
    "payment_method": "credit_card",
    "status": "completed"
  }
}