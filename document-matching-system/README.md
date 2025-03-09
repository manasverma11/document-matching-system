# 📄 Document Scanning & Matching System

## **🚀 Project Overview**
This is a **self-contained document scanning and matching system** with:
- **User authentication** (Register, Login)
- **Credit System** (20 free scans daily, request additional credits)
- **Document Upload & Matching** (Basic similarity check)
- **Admin Dashboard** (Approve credit requests, track usage)

---

## **🛠 Tech Stack**
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Flask (Python)
- **Database:** SQLite (Lightweight storage)
- **File Storage:** Local server

---

## **📌 Features**
### ✅ User Management & Authentication
- Register/Login
- User Roles: **Regular Users** & **Admins**

### ✅ Credit System
- 20 free scans per day (auto-reset at midnight)
- Users **request additional credits** if needed
- **Admins approve/deny credit requests**
- **Each document scan costs 1 credit**

### ✅ Document Upload & Matching
- Users upload a **plain text file**
- System compares it with stored documents
- Returns **similar documents** based on word-matching

### ✅ Smart Analytics Dashboard
- Tracks **scans per user per day**
- Identifies **most common document topics**
- Displays **top users** by scans & credits

---

## **🔧 Setup Instructions**
### **1️⃣ Install Dependencies**
Make sure you have **Python 3+** installed. Then run:
```sh


Run Flask App:
python app.py
Access at: http://127.0.0.1:5000/

API Endpoints

Method	Endpoint	Description
POST	/auth/register	User registration
POST	/auth/login	User login
GET	/user/profile	Get user details & credits
POST	/scan	Upload document for scanning (uses 1 credit)
GET	/matches/:docId	Get similar documents
POST	/credits/request	Request admin to add credits
GET	/admin/analytics	View analytics (Admin)
GET	/admin/credit-requests	View pending credit requests
POST	/admin/credit-approve	Approve credit request
POST	/admin/credit-deny	Deny credit request
