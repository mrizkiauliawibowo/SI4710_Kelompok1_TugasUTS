# 🎯 CRUD Operations & Features Documentation

## 📊 **CURRENT STATUS - SEBELUM PERBAIKAN**

### ✅ **Yang Sudah Ada:**
- **CREATE** - Semua service bisa create data baru
- **READ** - Semua service bisa read data (all + by ID)  
- **UPDATE** - 4 dari 5 service ada update operations
- **Business Logic** - Status updates, payment processing, dll

### ❌ **Yang BELUM Ada:**
- **DELETE operations** di semua service
- **Full CRUD untuk menu items** di Restaurant Service
- **Soft delete** untuk data integrity

---

## 🆕 **FITUR BARU YANG SUDAH DITAMBAHKAN**

### 1. **🗑️ DELETE OPERATIONS - Semua Service**

#### **Soft Delete** (Recommended)
```
DELETE /api/<resource>/<id>/soft-delete
```
- Menandai data sebagai deleted tanpa menghapus dari database
- Set `deleted_at` timestamp dan `is_active = false`
- Data tetap ada tapi tidak terlihat di query normal
- Dapat direstore kembali

#### **Hard Delete** (Permanent)
```
DELETE /api/<resource>/<id>
```
- Menghapus data permanen dari database
- Tidak dapat dikembalikan

#### **Restore Operations**
```
POST /api/<resource>/<id>/restore
```
- Mengembalikan data yang di-soft delete
- Set `deleted_at = null` dan `is_active = true`

### 2. **🍽️ FULL CRUD - Restaurant Menu Items**

#### **Menu Item Model** yang lengkap:
```python
class MenuItem(db.Model):
    id, restaurant_id, name, description, price
    category, image_url, is_available
    is_vegetarian, is_spicy, preparation_time
    calories, allergens (JSON), is_active
    created_at, updated_at, deleted_at
```

#### **CRUD Operations untuk Menu Items:**
- **CREATE** - Tambah menu item baru
- **READ** - Get all menu items, by ID, by restaurant
- **UPDATE** - Full update dan partial update
- **DELETE** - Soft delete, hard delete, restore
- **FILTER** - Filter by restaurant, category, price, dietary info

### 3. **🧹 SOFT DELETE - Data Integrity**

#### **Implementasi di Model:**
```python
is_active = db.Column(db.Boolean, default=True)
created_at = db.Column(db.DateTime, default=datetime.utcnow)
updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete
```

#### **Query Behavior:**
- Default: Hanya menampilkan data `deleted_at=None`
- Parameter `?include_deleted=true`: Menampilkan semua data termasuk yang di-soft delete
- Soft delete data tidak terlihat di list normal tapi tetap ada di database

### 4. **⚡ BULK OPERATIONS**

#### **Bulk Soft Delete:**
```
DELETE /api/<resource>/bulk-delete
Content-Type: application/json
{"ids": [1, 2, 3, 4, 5]}
```

#### **Bulk Restore:**
```
POST /api/<resource>/bulk-restore
Content-Type: application/json
{"ids": [1, 2, 3]}
```

### 5. **🔍 ADVANCED FILTERING**

#### **Filter Menu Items:**
```
POST /api/menu-items/filter
Content-Type: application/json
{
    "restaurant_ids": [1, 2, 3],
    "categories": ["main", "dessert"],
    "price_min": 10000,
    "price_max": 50000,
    "is_vegetarian": true,
    "is_spicy": false,
    "include_deleted": false,
    "page": 1,
    "per_page": 20
}
```

### 6. **📱 ENHANCED API RESPONSES**

#### **Response Format dengan Metadata:**
```json
{
    "success": true,
    "data": [...],
    "count": 10,
    "message": "Operation successful",
    "pagination": {
        "page": 1,
        "per_page": 20,
        "total": 100,
        "pages": 5,
        "has_next": true,
        "has_prev": false
    }
}
```

---

## 🚀 **CONTOH PENGGUNAAN**

### **1. Menu Item Management**

#### **Tambah Menu Item:**
```bash
curl -X POST http://localhost:5002/api/menu-items \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_id": 1,
    "name": "Pizza Margherita",
    "description": "Pizza dengan keju mozzarella",
    "price": 85000,
    "category": "main",
    "is_vegetarian": true,
    "allergens": ["gluten", "dairy"]
  }'
```

#### **Update Menu Item:**
```bash
curl -X PATCH http://localhost:5002/api/menu-items/1 \
  -H "Content-Type: application/json" \
  -d '{"price": 90000, "is_available": false}'
```

#### **Soft Delete Menu Item:**
```bash
curl -X DELETE http://localhost:5002/api/menu-items/1/soft-delete
```

#### **Restore Menu Item:**
```bash
curl -X POST http://localhost:5002/api/menu-items/1/restore
```

### **2. Bulk Operations**

#### **Delete Multiple Items:**
```bash
curl -X DELETE http://localhost:5002/api/menu-items/bulk-delete \
  -H "Content-Type: application/json" \
  -d '{"ids": [1, 2, 3, 4, 5]}'
```

### **3. Filtering & Search**

#### **Filter Menu Items by Category:**
```bash
curl "http://localhost:5002/api/menu-items?category=main&restaurant_id=1"
```

#### **Advanced Filter:**
```bash
curl -X POST http://localhost:5002/api/menu-items/filter \
  -H "Content-Type: application/json" \
  -d '{
    "categories": ["main", "appetizer"],
    "price_max": 50000,
    "is_vegetarian": true,
    "page": 1,
    "per_page": 10
  }'
```

---

## 📋 **ENDPOINTS LENGKAP - SERVICE TEMPLATE**

### **Base CRUD:**
```
GET    /api/<resource>                    - Read all
GET    /api/<resource>/<id>               - Read by ID
POST   /api/<resource>                    - Create
PUT    /api/<resource>/<id>               - Full update
PATCH  /api/<resource>/<id>               - Partial update
```

### **Delete Operations:**
```
DELETE /api/<resource>/<id>/soft-delete   - Soft delete
DELETE /api/<resource>/<id>               - Hard delete
POST   /api/<resource>/<id>/restore       - Restore
```

### **Bulk Operations:**
```
DELETE /api/<resource>/bulk-delete        - Bulk soft delete
POST   /api/<resource>/bulk-restore       - Bulk restore
```

### **Parameters:**
- `?include_deleted=true` - Include soft deleted records
- `?category=main` - Filter by category
- `?restaurant_id=1` - Filter by restaurant

---

## 🏆 **MANFAAT & KEUNGGULAN**

### **1. Data Integrity**
- **Soft delete** melindungi data dari kehilangan permanen
- **Audit trail** dengan `created_at`, `updated_at`, `deleted_at`
- **Can restore** data yang terhapus

### **2. Performance**
- **Bulk operations** untuk efisiensi
- **Pagination** untuk performa dengan data besar
- **Advanced filtering** untuk query yang kompleks

### **3. Flexibility**
- **Partial updates** tanpa harus kirim semua field
- **Include deleted** untuk administrative purposes
- **Multiple filters** untuk pencarian yang spesifik

### **4. RESTful Design**
- **HTTP methods** yang tepat (GET, POST, PUT, PATCH, DELETE)
- **Status codes** yang sesuai (200, 201, 400, 404, 500)
- **JSON responses** yang konsisten

---

## ✅ **CHECKLIST - STATUS TERKINI**

### **CRUD Operations:**
- [x] **CREATE** - ✓ Semua service
- [x] **READ** - ✓ All + by ID
- [x] **UPDATE** - ✓ 4 dari 5 service + full CRUD
- [x] **DELETE** - ✓ Soft delete + hard delete + restore

### **Advanced Features:**
- [x] **Soft Delete** - ✓ Implementasi lengkap
- [x] **Bulk Operations** - ✓ Delete & restore multiple
- [x] **Filtering** - ✓ Advanced filtering dengan pagination
- [x] **Data Integrity** - ✓ Audit trail & timestamps

### **Restaurant Menu Items:**
- [x] **Full CRUD** - ✓ Create, Read, Update, Delete
- [x] **Menu Management** - ✓ Category, dietary, pricing
- [x] **Restaurant Integration** - ✓ Relationship dengan restaurant
- [x] **Bulk Operations** - ✓ Mass operations

**🎉 PROJECT SUDAH LENGKAP DENGAN SEMUA FITUR CRUD YANG DIPERLUKAN!**