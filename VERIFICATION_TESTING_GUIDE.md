# 🧪 Shopkeeper Verification System - Live Testing Guide

## ✅ Current Status
- ✅ Test shopkeeper created in database
- ✅ Status: **⏳ PENDING VERIFICATION** (not verified yet)
- ✅ All 3 systems running (ports 5000, 5001, 5002)

---

## 🔄 Complete Workflow Test (Step-by-Step)

### **STEP 1: Shopkeeper Login with Test Account** ← YOU ARE HERE
**URL:** http://localhost:5001/auth/login

1. Go to Shopkeeper System login page
2. Enter credentials:
   - **Email:** `testshop123@pharmacy.com`
   - **Password:** `testpass123`
3. Click Login

**What should happen:**
- ✅ Login successful
- ✅ Redirected to "Pending Verification" page
- ❌ **Cannot** access dashboard
- ❌ **Cannot** add medicines
- ❌ **Cannot** view orders

---

### **STEP 2: See Pending Verification Page**
**What you'll see:**
```
⏳ Your Shop is Pending Verification

Status Timeline:
✓ Application Submitted (Today)
⏳ Under Review (Waiting...)
⏸️  Approval Notification (Pending)

"Your shop application is being reviewed by our admin team.
Once approved, you'll be able to list medicines and accept orders."
```

**Only button available:** Logout

---

### **STEP 3: Admin Reviews in Admin Panel**
**URL:** http://localhost:5002/dashboard/shopkeepers

1. Go to Admin Portal
2. Login as Admin:
   - **Username:** `admin`
   - **Password:** `admin123`
3. Click **"Shopkeepers"** in menu
4. Look for **PENDING VERIFICATION** section

**What admin should see:**
```
PENDING VERIFICATION (⏳ Yellow Section)
───────────────────────────
1. Test New Medical Store
   Owner: Test Shop Owner
   Email: testshop123@pharmacy.com
   License: LIC-TEST-2024
   Contact: 03001234567
   Applied: Today
   
   [✅ VERIFY] [❌ REJECT]
```

---

### **STEP 4: Admin Verifies Shopkeeper**
1. In the admin panel, find "Test New Medical Store"
2. Click **"✅ VERIFY"** button
3. See confirmation: `✅ Shopkeeper verified successfully!`

**What happens in database:**
- `verified` changes from `0` to `1`
- `verified_at` gets current timestamp

---

### **STEP 5: Shopkeeper Gets Access (After Verification)**
1. Shopkeeper logs out and logs back in
2. Now sees **Full Dashboard** ✅
3. Can now:
   - ✅ See dashboard stats
   - ✅ Add medicines
   - ✅ View orders
   - ✅ Manage inventory

---

## 📊 Database State (Right Now)

```
Total Shopkeepers: 4
  ✅ Verified: 3 (can fully access system)
  ⏳ Pending: 1 (TEST: Test New Medical Store)
```

---

## 🎯 Testing Checklist

- [ ] Shopkeeper can login with test account
- [ ] Sees "Pending Verification" page after login
- [ ] Cannot click any dashboard links
- [ ] Logout button works
- [ ] Admin can see pending shopkeeper in admin panel
- [ ] Admin can click "Verify" button
- [ ] Admin sees success message
- [ ] Shopkeeper logs back in → sees full dashboard
- [ ] Shopkeeper can now add medicines
- [ ] Shopkeeper can view orders

---

## 🔧 Quick Reference

| Action | URL | Credentials |
|--------|-----|-------------|
| **Shopkeeper Login** | http://localhost:5001/auth/login | `testshop123@pharmacy.com` / `testpass123` |
| **Admin Dashboard** | http://localhost:5002/dashboard | `admin` / `admin123` |
| **Admin Shopkeepers** | http://localhost:5002/dashboard/shopkeepers | (same admin creds) |
| **Customer App** | http://localhost:5000 | (can register new customer) |

---

## 🆘 If Something Breaks

### Shopkeeper Still Sees Pending After Verification
- Clear cookies: `Ctrl+Shift+Delete` → Delete cookies for localhost
- Logout and login again

### Admin Can't See Pending Shopkeeper
- Verify database has unverified shopkeeper:
  ```bash
  cd "d:\CODING\AI PHARMACY"
  python -c "import sqlite3; conn = sqlite3.connect('admin_system/database/pharmacy.db'); cursor = conn.cursor(); cursor.execute('SELECT shop_name, verified FROM shopkeepers WHERE verified = 0'); print(cursor.fetchall()); conn.close()"
  ```

### Verify System Not Working
- Check route `@shopkeeper_required` decorator is properly applied
- Check database has `verified`, `verified_at`, `verification_notes` columns
- Run migration: `python migrate_db.py`

---

## 📝 System Design

```
New Shopkeeper Registration
        ↓
    verified=0
        ↓
  Redirect to Pending Page
        ↓
  Admin Reviews (Dashboard)
        ↓
  Admin Clicks "Verify"
        ↓
  verified=1, verified_at=NOW
        ↓
  Shopkeeper Gets Full Access
```

---

## ✨ Features

✅ New shopkeepers must be approved by admin  
✅ Cannot use any features until verified  
✅ Admin sees pending list in dashboard  
✅ One-click verification process  
✅ Automatic status updates  
✅ Timeline view for shopkeeper  
✅ CLI tool also available for verification  

---

**Ready to test? Go to:** http://localhost:5001/auth/login

Test Account:
- Email: `testshop123@pharmacy.com`
- Password: `testpass123`
