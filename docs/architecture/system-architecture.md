# System Architecture – Food Delivery System

## 1. Overview
Sistem Pengiriman Makanan dikembangkan menggunakan arsitektur microservices, di mana setiap layanan beroperasi secara independen dengan basis data dan API masing-masing. Sistem ini dikoordinasikan oleh sebuah API Gateway terpusat yang mengelola rute, otentikasi, pengalihan permintaan, dan isolasi tingkat layanan. Arsitektur ini memungkinkan skalabilitas, fleksibilitas dalam deployment, dan pemisahan yang jelas antara fungsi-fungsi yang berbeda.

## 2. High-Level Architecture Diagram

                  ┌────────────────────────┐
                  │        FRONTEND        │
                  │  HTML / JS / Fetch API │
                  └──────────┬─────────────┘
                             │
                             ▼
                  ┌────────────────────────┐
                  │      API GATEWAY       │
                  │ Flask + RESTX + JWT    │
                  └──────────┬─────────────┘
       ┌──────────────────────┼───────────────────────────────┐
       │                      │                               │
       ▼                      ▼                               ▼
┌───────────────┐     ┌───────────────┐               ┌──────────────┐
│ USER SERVICE   │     │ RESTAURANT     │               │ ORDER SERVICE │
│ port 5001      │     │ SERVICE 5002   │               │ port 5003     │
└───────────────┘     └───────────────┘               └──────────────┘
       │                      │                               │
       ▼                      ▼                               ▼
┌───────────────┐     ┌───────────────┐               ┌──────────────┐
│ user.db        │     │ restaurant.db │               │ order.db      │
└───────────────┘     └───────────────┘               └──────────────┘

       ┌───────────────────────────────┬─────────────────────────────┐
       │                               │                             │
       ▼                               ▼                             ▼
┌───────────────┐            ┌───────────────┐            ┌───────────────┐
│ DELIVERY       │            │ PAYMENT        │            │ FRONTEND       │
│ SERVICE 5004   │            │ SERVICE 5005   │            │ (static files) │
└───────────────┘            └───────────────┘            └───────────────┘
       ▼                               ▼
 delivery.db                    payment.db


## 3. API Gateway Responsibilities
- Centralized routing and forwarding requests  
- Authentication using JWT  
- Error normalization (401, 403, 404, 500)  
- Service discovery (manual mapping in config)  
- Ensures isolation between services  

## 4. Technology Stack
- Python (Flask, Flask-RESTX)
- SQLite (database per service)
- REST API Communication
- JWT Authentication
- CORS-enabled frontend communication

## 5. Communication Flow
All clients send requests to API Gateway → forwarded internally to microservices.

