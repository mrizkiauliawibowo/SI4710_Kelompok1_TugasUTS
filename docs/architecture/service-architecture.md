# Microservices Architecture

## 1. User Service (Port 5001)
Handles user authentication, registration, profile, CRUD operations, and soft/hard delete logic.

### Responsibilities
- Register user  
- Login user  
- Manage user data  
- Manage user profiles  

### Database
`user_service.db`

---

## 2. Restaurant Service (Port 5002)
Provides restaurant CRUD operations and menu item management.

### Responsibilities
- Manage restaurants  
- Full CRUD for menu items  
- Soft delete / restore for menu items  
- Filtering menu items by restaurant  

### Database
`restaurant.db`

---

## 3. Order Service (Port 5003)
Manages order creation, updating statuses, soft deletes, items, and order history.

### Responsibilities
- Create order  
- Manage order items  
- Manage status update  
- Maintain order history table  
- Soft delete / bulk delete  

### Database
`order_service.db`

---

## 4. Delivery Service (Port 5004)
Handles courier assignment, delivery status, tracking, and location updates.

### Responsibilities
- Assign courier  
- Update courier location  
- Track delivery related to order  
- Soft delete delivery records  

### Database
`delivery_service.db`

---

## 5. Payment Service (Port 5005)
Manages payment creation, processing, refund, and payment methods.

### Responsibilities
- Create payment  
- Process payment  
- Manage refunds  
- Manage payment methods  

### Database
`payment_service.db`
