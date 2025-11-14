# Deployment Architecture

## 1. Local Deployment (Current Setup)
Each microservice is started manually:

```
python user-service/app.py
python restaurant-service/app.py
python order-service/app.py
python delivery-service/app.py
python payment-service/app.py
python api-gateway/app.py
```

Or using helper scripts:

- `START_ALL_SERVICE.ps1`
- `start_all.py`
- `setup.sh`

Frontend is static and served via local browser.

---

## 2. Possible Dockerized Deployment (Future)
Although not implemented yet, the system is compatible with a container-based approach.

### Example Deployment Plan:
- 1 container per microservice  
- 1 container for API Gateway  
- SQLite files mounted via Docker volumes  
- Reverse proxy (Nginx) optional  

---

## 3. Networking
All services currently run on:

```
127.0.0.1 (localhost)
Ports: 5000–5005
```

No inter-service direct calls — all requests go through API Gateway.

---

## 4. Scalability Notes
Microservices can be scaled independently:
- More delivery workers → scale delivery-service  
- High load on restaurants → scale restaurant-service  
