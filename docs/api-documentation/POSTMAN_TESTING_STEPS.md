# 📋 Step-by-Step Guide: Testing API di Postman

## 🎯 Overview
Panduan lengkap untuk testing Food Delivery System API menggunakan Postman Collection yang telah disediakan.

## 📝 Prerequisites
1. **Postman** terinstall (Download dari https://www.postman.com/downloads/)
2. **API Gateway** running di http://localhost:5000
3. **Collection file**: `docs/POSTMAN_COLLECTION.json`

## ⚠️ **CATATAN PENTING - Response Format Updates**
Setelah perbaikan error serialisasi, **User Service** sekarang menggunakan **Flask-RESTX** dengan format response yang berbeda:
- **Sebelum**: `{"success": true, "data": [...], "count": 5}`
- **Sesudah**: Array langsung `[user1, user2, ...]`

**Service lainnya** (Restaurant, Order, Delivery, Payment) tetap menggunakan format lama.

---

## 🚀 **LANGKAH 1: Setup Postman Collection**

### Step 1.1: Import Collection
```
1. Buka aplikasi Postman
2. Klik "Import" button (di sidebar kiri atas)
3. Pilih tab "File" atau drag-and-drop file
4. Browse ke folder project: `docs/POSTMAN_COLLECTION.json`
5. Klik "Import" untuk confirm
```

### Step 1.2: Verify Collection Imported
```
1. Check sidebar kiri - seharusnya ada folder:
   "Food Delivery System - UTS IAE"
2. Expand folder untuk melihat 8 sub-folder:
   - 1. API Gateway Authentication
   - 2. System Health & Info
   - 3. User Service (ARTHUR - Port 5001)
   - 4. Restaurant Service (rizki - Port 5002)
   - 5. Order Service (Nadia - Port 5003)
   - 6. Delivery Service (aydin - Port 5004)
   - 7. Payment Service (reza - Port 5005)
   - 8. Error Handling Tests
```

---

## 🔐 **LANGKAH 2: Setup Environment (Optional)**

### Step 2.1: Create Environment
```
1. Di sidebar kiri, klik "Environments"
2. Klik "Create Environment"  
3. Nama: "Food Delivery Development"
4. Klik "Create" untuk create environment
```

### Step 2.2: Set Environment Variables
```
Tambahkan variables berikut:

Variable Name | Initial Value | Current Value
base_url      | http://localhost:5000 | http://localhost:5000
admin_token   | (kosong) | (kosong)
user_token    | (kosong) | (kosong)
user_id       | (kosong) | (kosong)
restaurant_id | (kosong) | (kosong)
menu_item_id  | (kosong) | (kosong)
order_id      | (kosong) | (kosong)
delivery_id   | (kosong) | (kosong)
payment_id    | (kosong) | (kosong)

Catatan: Variables user_id, restaurant_id, dll akan otomatis ter-set oleh test scripts
```

### Step 2.3: Select Environment
```
1. Di top-right Postman, click dropdown "No Environment"
2. Pilih "Food Delivery Development"
3. Pastikan environment active dengan melihat checkbox
```

---

## 🧪 **LANGKAH 3: Run Tests - Basic Flow**

### Step 3.1: Test Health Check
```
Folder: "2. System Health & Info"
Test: "GET - Health Check"
1. Double-click test "GET - Health Check"
2. Klik "Send" button
3. Expected Response: 200 OK dengan JSON health status
4. Check response body:
   {
     "status": "healthy",
     "service": "api-gateway",
     "version": "1.0.0"
   }
```

### Step 3.1.1: Test Swagger Documentation (Optional)
```
Setelah perbaikan, Swagger UI sekarang tersedia:
- User Service: http://localhost:5001/ (baru ditambahkan)
- API Gateway: http://localhost:5000/api-docs/ (sudah ada)

1. Buka URL di browser untuk melihat dokumentasi API interaktif
2. Test endpoints langsung dari Swagger UI
3. Explore models dan schemas yang tersedia
```

### Step 3.2: Test Authentication - Login Admin
```
Folder: "1. API Gateway Authentication"
Test: "POST - Login Admin"
1. Double-click test "POST - Login Admin"
2. Klik "Send" button
3. Expected Response: 200 OK
4. Check response body:
   - success: true
   - access_token: (JWT token string)
   - user: {id: 1, username: "admin", role: "admin"}
5. Token sudah tersimpan di environment variable admin_token

NOTE: Login accepts either username OR email:
- Username: "admin" or Email: "admin@fooddelivery.com"
- Password: "admin123"
```

### Step 3.3: Verify Token
```
Test: "GET - Verify Token"
1. Double-click test "GET - Verify Token"
2. Klik "Send" button
3. Expected Response: 200 OK dengan user info
4. Verify token working dengan user data
```

---

## 🏥 **LANGKAH 4: Test User Service (ARTHUR)**

### Step 4.1: Get All Users
```
Folder: "3. User Service (ARTHUR - Port 5001)"
Test: "GET - Get All Users"
1. Double-click test
2. Pastikan sudah login (token auto-added by pre-request)
3. Klik "Send"
4. Expected: 200 OK dengan array users
5. Check response structure (Flask-RESTX format):
   [
     {
       "id": 1,
       "username": "admin",
       "email": "admin@fooddelivery.com",
       "full_name": "Administrator",
       "phone": null,
       "address": null,
       "user_type": "admin",
       "is_active": true,
       "created_at": "2025-01-01T00:00:00",
       "updated_at": null,
       "is_deleted": false
     }
   ]
```

### Step 4.2: Create New User
```
Test: "POST - Create User"
1. Double-click test
2. Klik "Send" 
3. Expected: 201 Created
4. Check new user created dengan unique ID
5. User ID tersimpan di environment variable user_id
```

### Step 4.3: Get User by ID
```
Test: "GET - Get User by ID"
1. Double-click test
2. Klik "Send"
3. Expected: 200 OK dengan user details
4. Verify data sesuai dengan input sebelumnya
```

### Step 4.4: Update User
```
Test: "PUT - Update User"
1. Double-click test
2. Klik "Send"
3. Expected: 200 OK dengan updated data
4. Check name/email berhasil di-update
```

### Step 4.5: Soft Delete User
```
Test: "DELETE - Soft Delete User"
1. Double-click test
2. Klik "Send"
3. Expected: 200 OK dengan is_deleted: true
4. Verify soft delete implementation
```

---

## 🍽️ **LANGKAH 5: Test Restaurant Service (rizki)**

### Step 5.1: Get All Restaurants
```
Folder: "4. Restaurant Service (rizki - Port 5002)"
Test: "GET - Get All Restaurants"
1. Double-click test
2. Klik "Send"
3. Expected: 200 OK dengan array restaurants
```

### Step 5.2: Create Restaurant
```
Test: "POST - Create Restaurant"
1. Double-click test
2. Klik "Send"
3. Expected: 201 Created
4. Restaurant ID tersimpan di environment variable restaurant_id
```

### Step 5.3: Get Menu Items
```
Test: "GET - Get All Menu Items"
1. Double-click test
2. Klik "Send"
3. Expected: 200 OK dengan array menu items
```

### Step 5.4: Create Menu Item
```
Test: "POST - Create Menu Item"
1. Double-click test
2. Klik "Send"
3. Expected: 201 Created
4. Menu item ID tersimpan di environment variable menu_item_id
```

---

## 📦 **LANGKAH 6: Test Order Service (Nadia)**

### Step 6.1: Get All Orders
```
Folder: "5. Order Service (Nadia - Port 5003)"
Test: "GET - Get All Orders"
1. Double-click test
2. Klik "Send"
3. Expected: 200 OK dengan array orders
```

### Step 6.2: Create Order
```
Test: "POST - Create Order"
1. Double-click test
2. Klik "Send"
3. Expected: 201 Created
4. Order ID tersimpan di environment variable order_id
5. Check total_amount dihitung dengan benar
```

---

## 🚚 **LANGKAH 7: Test Delivery Service (aydin)**

### Step 7.1: Get All Deliveries
```
Folder: "6. Delivery Service (aydin - Port 5004)"
Test: "GET - Get All Deliveries"
1. Double-click test
2. Klik "Send"
3. Expected: 200 OK dengan array deliveries
```

### Step 7.2: Create Delivery
```
Test: "POST - Create Delivery"
1. Double-click test
2. Klik "Send"
3. Expected: 201 Created
4. Delivery ID tersimpan di environment variable delivery_id
5. Check delivery_status: "assigned"
```

---

## 💳 **LANGKAH 8: Test Payment Service (reza)**

### Step 8.1: Get All Payments
```
Folder: "7. Payment Service (reza - Port 5005)"
Test: "GET - Get All Payments"
1. Double-click test
2. Klik "Send"
3. Expected: 200 OK dengan array payments
```

### Step 8.2: Create Payment
```
Test: "POST - Create Payment"
1. Double-click test
2. Klik "Send"
3. Expected: 201 Created
4. Payment ID tersimpan di environment variable payment_id
5. Check payment_status: "pending"
```

### Step 8.3: Process Payment
```
Test: "POST - Process Payment"
1. Double-click test
2. Klik "Send"
3. Expected: 200 OK dengan processed payment
4. Check payment_status: "completed"
```

---

## ⚠️ **LANGKAH 9: Test Error Handling**

### Step 9.1: Test Invalid Login
```
Folder: "8. Error Handling Tests"
Test: "POST - Login with Invalid Credentials"
1. Double-click test
2. Klik "Send"
3. Expected: 401 Unauthorized
4. Check error message: "Invalid credentials"
```

### Step 9.2: Test Unauthorized Access
```
Test: "GET - Access Protected Endpoint Without Token"
1. Double-click test
2. Klik "Send"
3. Expected: 401 Unauthorized
4. Check error message: "Authorization required"
```

### Step 9.3: Test Non-existent Service
```
Test: "GET - Non-existent Service"
1. Double-click test
2. Klik "Send"
3. Expected: 404 Not Found
4. Check error message: "Service not found"
```

---

## 🔄 **LANGKAH 10: Run Collection Tests (Bulk)**

### Step 10.1: Run Single Folder
```
1. Right-click folder (e.g., "1. API Gateway Authentication")
2. Pilih "Run folder"
3. Configure Runner:
   - Environment: "Food Delivery Development"
   - Iterations: 1
   - Delay: 0
4. Klik "Run [folder-name]"
```

### Step 10.2: Run Entire Collection
```
1. Right-click "Food Delivery System - UTS IAE"
2. Pilih "Run collection"
3. Configure Runner:
   - Environment: "Food Delivery Development"
   - Iterations: 1
   - Delay: 0
   - Log responses: All
4. Klik "Run Food Delivery System - UTS IAE"
```

### Step 10.3: Review Test Results
```
1. Check test results di Runner window
2. Green = ✅ Passed tests
3. Red = ❌ Failed tests
4. Klik pada failed test untuk melihat detail error
5. Screenshot untuk dokumentasi jika perlu
```

---

## 📊 **LANGKAH 11: Advanced Testing**

### Step 11.1: Test Data Persistence
```
1. Run all tests dengan "Run collection"
2. Run collection lagi untuk test idempotency
3. Verify data consistency between runs
```

### Step 11.2: Performance Testing
```
1. Di Collection Runner, set Iterations: 10
2. Run untuk test performance
3. Monitor response times dan success rate
```

### Step 11.3: Manual Testing
```
Untuk testing manual spesifik:
1. Double-click specific test
2. Modify request data jika perlu
3. Send dan analyze response
4. Repeat untuk different scenarios
```

---

## 📝 **LANGKAH 12: Generate Test Report**

### Step 12.1: Export Test Results
```
1. Setelah run collection, di Runner window
2. Klik "Export Results"
3. Choose location dan filename
4. Save sebagai JSON atau CSV
```

### Step 12.2: Documentation
```
Buat test report dengan:
1. Total tests run
2. Pass/Fail rate
3. Performance metrics
4. Issues found
5. Screenshots of successful tests
```

---

## 🐛 **Troubleshooting Common Issues**

### Issue 1: "Unauthorized" untuk semua tests
```
Solution:
1. Pastikan sudah login admin terlebih dahulu
2. Check admin_token tersimpan di environment
3. Re-run login test jika token expired
```

### Issue 2: "Connection refused" error
```
Solution:
1. Pastikan API Gateway running di localhost:5000
2. Check port tidak digunakan aplikasi lain
3. Restart API Gateway
```

### Issue 3: Tests fail dengan 4xx errors
```
Solution:
1. Check request headers (Authorization: Bearer {{admin_token}})
2. Verify request body JSON format
3. Check expected data structure
```

### Issue 4: Environment variables kosong
```
Solution:
1. Pastikan environment "Food Delivery Development" selected
2. Re-run login test untuk populate variables
3. Check pre-request scripts running correctly
```

### Issue 5: User Service response format berbeda (Flask-RESTX)
```
Problem: Response sekarang array langsung, bukan nested object
Solution:
Update test scripts untuk handle format baru:
- Sebelum: pm.expect(jsonData.data).to.be.an('array')
- Sesudah: pm.expect(jsonData).to.be.an('array')

Atau gunakan direct access:
- GET /api/user-service/api/users → expect array
- POST /api/user-service/api/users → expect single object
```

### Issue 6: Login accepts username OR email
```
Problem: API Gateway login accepts both username and email
Solution:
Use either:
- Username: "admin" or "user"
- Email: "admin@fooddelivery.com" or "user@fooddelivery.com"
Password: "admin123" or "user123"
```

### Issue 7: Clearer error messages for user creation
```
Problem: User creation fails with specific field errors
Solution:
Ensure request body includes all required fields:
- username (string)
- email (string)
- password (string)
- full_name (string)
Optional: phone, address, user_type
```

---

## ✅ **Expected Test Results**

Setelah menjalankan semua tests, Anda seharusnya melihat:

```
📊 Test Summary:
✅ Total Tests: 45
✅ Passed: 42-45 (93-100%)
❌ Failed: 0-3 (0-7%)
📈 Success Rate: 93-100%
```

### Critical Tests yang WAJIB PASS:
- [x] Health Check (200)
- [x] Login Admin (200 + token)
- [x] Get Users (200) - Response: Array langsung (Flask-RESTX)
- [x] Create User (201) - Response: Single object
- [x] Get Restaurants (200) - Response: Nested object
- [x] Create Restaurant (201) - Response: Nested object
- [x] Create Order (201) - Response: Nested object
- [x] Create Delivery (201) - Response: Nested object
- [x] Create Payment (201) - Response: Nested object
- [x] Process Payment (200) - Response: Nested object
- [x] Invalid Login (401)
- [x] Unauthorized Access (401)

---

## 🎯 **Success Criteria**

Testing berhasil jika:
1. ✅ **95%+ tests pass**
2. ✅ **JWT authentication working**
3. ✅ **CRUD operations complete**
4. ✅ **Error handling proper**
5. ✅ **Service integration working**
6. ✅ **Data persistence working**

---

## 🚀 **Next Steps**

Setelah testing berhasil:
1. 📊 **Document results** untuk submission
2. 🔄 **Test end-to-end flow** (login → create order → payment)
3. 📸 **Screenshot important results** untuk portfolio
4. 📝 **Note any improvements** untuk future development

**Happy Testing! 🎉**