# Data Flow Diagram (DFD)

## 1. Login Flow
```
Client → API Gateway → User Service → validate user
User Service → Gateway → return JWT
Gateway → Client
```

---

## 2. Ordering Food
```
Client → Gateway → Restaurant Service → get menu
Client → Gateway → Order Service → create order
Order Service → Delivery Service → assign courier
Order Service → Payment Service → create pending payment
Gateway → Client → order created
```

---

## 3. Payment Processing
```
Client → Gateway → Payment Service → process
Payment Service → Gateway → success
```

---

## 4. Delivery Tracking
```
Delivery Courier → Delivery Service → update location
Client → Gateway → Delivery Service → get tracking → Client
```

---

## 5. DFD Level 0 (Text Representation)
```
[User] 
   ↓
[API Gateway]
   ↓
[User Service] → Login Response

[User] → Menu Request → [Gateway] → [Restaurant Service]

[User] → Create Order → [Gateway] → [Order Service]
[Order Service] → [Delivery Service]
[Order Service] → [Payment Service]

[Delivery Service] → Tracking Info → [Gateway] → [User]
```
