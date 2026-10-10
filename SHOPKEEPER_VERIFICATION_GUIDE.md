# 🏪 Shopkeeper Verification System - Complete Guide

## 🎯 Overview
The shopkeeper verification system allows administrators to review and approve new shop owner registrations. Once approved, shopkeepers can list their medicines on the platform and accept customer orders.

**KEY UPDATE**: Shopkeeper system and admin system now share the **same pharmacy.db database** for unified verification workflow.

---

## 🗄️ Database Architecture

**UNIFIED DATABASE**: Both `shopkeeper_system` and `admin_system` use `admin_system/database/pharmacy.db`
- Ensures shopkeeper registrations are visible to admin panel
- Verification status synchronized across both systems
- No data duplication

---

## 🔐 Admin Access

### Credentials:
- **Username:** `admin`
- **Password:** `admin123`

### Admin Panel URL:
```
http://localhost:5000/dashboard
```

### Shopkeeper System URL:
```
http://localhost:5001
```

---

## 📋 Managing Shopkeepers

### Step 1: Access Shopkeeper Management
1. Go to Admin Dashboard: `http://localhost:5000/admin/dashboard`
2. Click **"Manage Shopkeepers"** button in Quick Actions
3. Or navigate directly: `http://localhost:5000/admin/shopkeepers`

### Step 2: Review Pending Registrations
The dashboard shows two sections:

#### **Pending Verification** (⏳ Yellow Section)
Shows all shopkeepers awaiting admin approval. Each entry shows:
- 🏪 **Shop Name** - Name of the medical store
- 👤 **Owner Name** - Full name of the shop owner
- 📋 **License Number** - Medical shop license
- 📍 **City** - Location of the shop
- 📞 **Contact** - Phone number
- 📧 **Email** - Email address
- 📅 **Registered** - Registration date

#### **Approved Shops** (✅ Green Section)
Shows all verified and active shopkeepers with their medicine count.

---

## ✅ Approving a Shopkeeper

### To Approve:
1. Find the shopkeeper in the **"Pending Verification"** table
2. Click the **"✅ Approve"** button
3. Confirm the action when prompted
4. The shopkeeper will receive a success notification

### What Happens After Approval:
- ✅ Shopkeeper's verification status changes to `verified`
- ✅ Shopkeeper can now add medicines to the platform
- ✅ Their medicines become visible to customers
- ✅ They can receive and manage customer orders
- ✅ Entry moves from "Pending" to "Approved" section

---

## ❌ Rejecting a Shopkeeper

### To Reject:
1. Find the shopkeeper in the **"Pending Verification"** table
2. Click the **"❌ Reject"** button
3. Confirm deletion when prompted
4. The registration will be permanently deleted

### What Happens After Rejection:
- ❌ Shopkeeper account is deleted
- ❌ Associated user account is removed
- ❌ Registration cannot be recovered
- ❌ Entry is removed from the pending list

---

## 🧪 Testing the System

### Test Shopkeeper Account:
- **Username:** `testshop`
- **Password:** `shopkeeper123`
- **Email:** testshop@acumeds.com
- **Shop Name:** Test Medical Store
- **Status:** Pending Verification

### Test Workflow:
1. **Login as Admin** → Admin Dashboard
2. **Manage Shopkeepers** → View pending "Test Medical Store"
3. **Approve Shopkeeper** → Changes to verified
4. **Login as Shopkeeper** at http://localhost:5001
5. **Add Medicines** → Dashboard → Add Medicine
6. **Verify in Phone App** → Medicines visible to customers

---

## 👥 User Flow

### For New Shopkeepers:
```
1. Register at http://localhost:5001/auth/register
   ↓
2. Fill Shop Details (License, Contact, etc.)
   ↓
3. Registration Created (Status: Pending)
   ↓
4. Admin Reviews in Shopkeeper Management
   ↓
5. Admin Approves ✅
   ↓
6. Shopkeeper Receives Confirmation
   ↓
7. Can Login and Add Medicines
```

### For Customers:
```
1. Visit http://localhost:5000
   ↓
2. Browse Medicines from Approved Shopkeepers
   ↓
3. Add to Cart and Order
   ↓
4. Shopkeeper Fulfills Order
```

---

## 📊 Statistics

The Shopkeeper Management dashboard shows:
- **Pending Verification Count** - How many shops await approval
- **Approved Shops Count** - How many shops are active
- **Per-Shop Metrics** - Number of medicines per shop

---

## 🔒 Important Notes

1. **Verification is Required** - Unverified shopkeepers cannot:
   - Add medicines
   - Accept orders
   - Their medicines won't be visible to customers

2. **License Validation** - Admins should verify:
   - License number format
   - Business legitimacy
   - Contact information accuracy

3. **Audit Trail** - All approvals/rejections are recorded:
   - Admin who approved
   - Approval date
   - Shop status

---

## 🛠️ Command-Line Verification (Advanced)

For advanced users, you can also manage verification via terminal:

### Installation
```bash
cd shopkeeper_system
```

### List Pending Shopkeepers
```bash
python verify_shopkeeper.py list
```

Output shows:
```
================================================================================
                   PENDING SHOPKEEPERS FOR VERIFICATION
================================================================================

1. Park's Medical Shop
   Owner: John Park (john@example.com)
   License: LIC-12345
   Contact: +94-70-123-4567
   Applied: 2024-01-20 10:30 AM
```

### Verify a Shopkeeper
```bash
python verify_shopkeeper.py verify 1
```

Output: `✓ Shopkeeper ID 1 verified successfully!`

### Reject a Shopkeeper
```bash
python verify_shopkeeper.py reject 1 "License document is invalid"
```

This CLI tool connects to the **same pharmacy.db** as the admin panel.

---

## 🔄 Complete Verification Workflow

### For New Shopkeepers:
```
1. Go to: http://localhost:5001/register
2. Fill registration form (Shop Name, License, Contact, etc.)
3. Submit → Registration created with verified=false
4. Sees "Pending Verification" page with:
   ✓ Application Submitted (today's date)
   ⏳ Under Review (waiting)
   ⏸️ Approval Notification (pending)
```

### In Admin Panel:
```
1. Go to: http://localhost:5000/dashboard
2. Click: Shopkeepers → Pending Verification
3. See new shopkeeper in yellow pending section
4. Click: "Verify" button
5. Confirmation: "✓ Shopkeeper verified successfully"
```

### Shopkeeper Gets Access:
```
1. Shopkeeper logs back in
2. Dashboard is now fully accessible
3. Can add medicines, view orders, manage shop
```

---

## 🆘 Troubleshooting

### Shopkeeper Not Showing in Admin Panel?
**Solution**: Ensure both systems use **shared pharmacy.db**
- Check: `shopkeeper_system/app/__init__.py` 
- Should point to: `admin_system/database/pharmacy.db` ✓

### "no such column: shopkeepers.verified_at" Error?
**Solution**: Run database migration
```bash
cd d:\CODING\AI PHARMACY
python migrate_db.py
```

### Shopkeeper Can Still Access Dashboard Without Verification?
**Solution**: Check route verification in `shopkeeper_system/app/routes.py`
- Dashboard route should have:
```python
if not shopkeeper.verified:
    return redirect(url_for('auth.pending_verification'))
```

---

## 📞 Support

For issues with the shopkeeper verification system:
1. Check admin logs in terminal
2. Verify database entries: `sqlite3 admin_system/database/pharmacy.db`
3. Contact development team

---

**Last Updated:** 2024
**System Version:** AcuMeds Pharmacy + Shopkeeper Portal
**Database**: Unified pharmacy.db ✓
