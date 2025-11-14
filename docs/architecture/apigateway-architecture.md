# API Gateway Architecture

## 1. Overview
The API Gateway acts as the **central entry point** for all clients. All microservices are isolated and cannot be accessed directly except through the gateway.

## 2. Key Features
### Authentication
- JWT token generation and validation  
- `@jwt_required()` for protected routes  
- Admin-only authorization using decorators  

### Routing & Forwarding
The gateway forwards requests to microservices based on predefined routes:

```
/api/user-service/...        → localhost:5001/...
/api/restaurant-service/...  → localhost:5002/...
/api/order-service/...       → localhost:5003/...
/api/delivery-service/...    → localhost:5004/...
/api/payment-service/...     → localhost:5005/...
```

### Error Handling
- 401 Unauthorized  
- 403 Forbidden  
- 404 Not Found  
- 500 Internal Server Error  
- 503 Service Unavailable  

### Swagger Documentation
Gateway contains integrated OpenAPI/Swagger UI:
```
http://localhost:5000/api-docs/
```

## 3. Internal Communication
Each request is re-created and forwarded using:

```
requests.request(method, url, data, json, params)
```

Ensuring:
- Host header removed
- JSON forwarded safely
- Timeout controlled

## 4. Gateway Flow Summary
1. Client sends request  
2. Gateway validates request (JWT if needed)  
3. Gateway forwards to corresponding microservice  
4. Service returns response  
5. Gateway normalizes & returns to client  
