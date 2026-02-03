# 🧩 Django Appwrite Admin Panel

A **full-stack Django application** that provides a **custom admin panel for Appwrite**, allowing you to **view, manage, and operate Appwrite databases, collections, documents, and storage** directly from a web UI.

This panel acts as a **lightweight, modular alternative** to Appwrite’s console — designed to be **plug-and-play** inside any Django project.

---

## ✨ Features

- Secure environment-based Appwrite connection
- List all **Appwrite databases**
- View databases → collections → documents hierarchy
- Dynamic document schema rendering
- Full **CRUD support** for documents
- Image & file upload via Appwrite Storage
- Automatic field validation based on Appwrite schema
- Live sync with Appwrite (no local DB required)
- Modular & reusable Django app
- Zero configuration beyond `.env`

---

## 🎯 Purpose

This project is built to:

- Replace repetitive Appwrite Console usage
- Provide a **project-specific admin panel**
- Simplify Appwrite management for non-technical users
- Integrate Appwrite seamlessly into Django workflows
- Enable rapid backend setup without writing admin logic

---

## 🧠 How It Works

### 🔗 Appwrite Integration
- Appwrite credentials are defined in environment variables
- The panel connects directly using Appwrite SDK
- No data is stored locally in Django

---

### 🗄️ Database & Collection Handling
- Automatically fetches:
  - Databases
  - Collections
  - Attributes (schema)
  - Documents
- UI adapts dynamically based on collection schema

---

## 🧩 Modular Architecture

This admin panel is designed as a **drop-in Django app**.

### ✅ Plug & Play
1. Install the app
2. Define Appwrite credentials in `.env`
3. Include URLs
4. Start managing Appwrite instantly

---

## 🛠️ Tech Stack
<p align="left"> 
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" width="32" /> 
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/django/django-plain.svg" width="32" /> 
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/appwrite/appwrite-original.svg" width="32" /> 
</p>

- Python
- Django
- Appwrite Database
- Appwrite Storage



