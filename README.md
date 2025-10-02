# E-Commerce Backend API

A production-ready backend system for an e-commerce platform, built with **FastAPI**. The application demonstrates secure authentication, order lifecycle management, inventory control, and admin functionality, following best practices in backend development.

---

## Features

* **User Authentication & Authorization** using JWT and Role-Based Access Control (RBAC)
* **Product Management** with search and filtering
* **Order Lifecycle Management**: pending → confirmed → shipped → delivered → cancelled
* **Shopping Cart** with stock validation and checkout flow
* **Inventory Management** with concurrency-safe updates preventing overselling
* **Email Notifications** for order confirmations and status updates
* **Admin Dashboard** for system-level operations

---

## Tech Stack

* **Framework**: FastAPI
* **Database**: SQLite with SQLAlchemy ORM
* **Authentication**: JWT tokens, Argon2 password hashing
* **Security**: Role-based access control, rate limiting, Pydantic validation
* **Email**: SMTP integration for notifications

---

## Project Structure

```
ecommerce-backend/
├── app/
│   ├── routes/
│   │   ├── auth.py
│   │   ├── products.py
│   │   ├── orders.py
│   │   ├── cart.py
│   │   └── admin.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── database.py
│   ├── dependencies.py
│   ├── email_service.py
│   └── main.py
├── requirements.txt
├── README.md
└── .gitignore
```
---

## API Documentation

When the server is running, interactive documentation is available:

* Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
* ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Quick Start

1. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```
2. Run the server

   ```bash
   uvicorn app.main:app --reload
   ```
3. Access the API at `http://localhost:8000/docs`

---

## Default Admin User

To bootstrap the system, create an admin user via:

```bash
POST /auth/register-admin
{
  "username": "admin",
  "email": "admin@example.com",
  "password": "admin123",
  "secret_key": "admin123"
}
```

---

## API Endpoints

### Authentication

* `POST /auth/register` – Register new user
* `POST /auth/register-admin` – Register admin user
* `POST /auth/login` – Login

### Products

* `GET /products/` – List products with search/filters
* `POST /products/` – Create product (Admin only)
* `GET /products/{id}` – Product details
* `PUT /products/{id}` – Update product (Admin only)
* `DELETE /products/{id}` – Delete product (Admin only)

### Orders

* `POST /orders/` – Create order
* `GET /orders/my-orders` – Retrieve orders for logged-in user
* `GET /orders/{id}` – Order details
* `PUT /orders/{id}/status` – Update order status (Admin only)

### Cart

* `POST /cart/` – Add item to cart
* `GET /cart/{user_id}` – View cart contents
* `DELETE /cart/{user_id}/{product_id}` – Remove item from cart
* `POST /cart/{user_id}/checkout` – Checkout cart

### Admin

* `GET /admin/dashboard` – Admin dashboard
* `GET /admin/reports` – System reports

---

## Security Implementation

* **Argon2 password hashing** (migrated from bcrypt for stronger protection)
* **JWT-based authentication** with expiration control
* **Role-Based Access Control (RBAC)** to restrict endpoints
* **Rate limiting** on sensitive endpoints
* **Pydantic input validation** to enforce schema integrity
* **SQL injection prevention** via SQLAlchemy ORM

---

## Key Technical Achievements

* Concurrency-safe inventory management to prevent overselling
* Automated background email notifications
* Search and filtering powered by TF-IDF for products
* Database transactions ensuring consistency and rollback safety
* REST-compliant API structure with descriptive error handling

---

## Database Schema

The relational schema consists of:

* **users** – authentication and profile data
* **products** – product catalog with stock levels
* **orders** – order headers and statuses
* **order_items** – product items within orders
* **cart_items** – temporary cart state

---

## Testing the API

1. Start the server and open `/docs`
2. Register both a regular user and an admin
3. Add products as admin
4. Place an order as a user
5. Manage order status as admin

---

## Example Usage

```json
POST /orders/
{
  "user_id": 1,
  "items": [
    {"product_id": 1, "quantity": 2},
    {"product_id": 3, "quantity": 1}
  ]
}
```

The system will automatically:

* Validate product availability
* Calculate order total
* Deduct inventory
* Send confirmation email

---

## Order Lifecycle

1. **Pending** – Order created, awaiting confirmation
2. **Confirmed** – Order accepted and verified
3. **Shipped** – Dispatched to customer
4. **Delivered** – Completed successfully
5. **Cancelled** – Order cancelled, inventory restored
