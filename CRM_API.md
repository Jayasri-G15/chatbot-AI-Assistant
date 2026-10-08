# AI CRM ASSISTANT API SPECIFICATION

This document details the RESTful API endpoints for authentication, customer management, deals, activities, and leads.

---

## 1. Authentication APIs

### `POST /api/v1/auth/login`
Authenticates a user and returns a Bearer JWT access token.

- **Authentication:** Public
- **Request Body:**
  ```json
  {
    "email": "admin@crm.com",
    "password": "password123"
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": "usr-admin-01",
      "name": "Admin User",
      "email": "admin@crm.com",
      "role": "admin"
    }
  }
  ```
- **Errors:**
  - `401 Unauthorized`: Invalid email or password.

---

### `GET /api/v1/auth/me`
Fetches current authenticated user details.

- **Authentication:** Bearer Token
- **Headers:** `Authorization: Bearer <token>`
- **Response `200 OK`:**
  ```json
  {
    "id": "usr-admin-01",
    "name": "Admin User",
    "email": "admin@crm.com",
    "role": "admin"
  }
  ```

---

## 2. Customer APIs

### `GET /api/v1/customers`
Retrieves a paginated list of customers with optional search filtering.

- **Authentication:** Bearer Token
- **Query Parameters:**
  - `search` (string, optional): Term to filter by customer name, email, or company.
  - `page` (int, default=1): Page index.
  - `limit` (int, default=20): Max items per page (1 to 100).
- **Response `200 OK`:**
  ```json
  {
    "success": true,
    "data": {
      "items": [
        {
          "id": "cust-abc",
          "name": "ABC Ltd",
          "email": "contact@abcltd.com",
          "phone": "+91 98765 43210",
          "company": "ABC Ltd",
          "owner_id": "usr-rep-01",
          "deals_count": 3,
          "open_deal_value": 2050000.0,
          "created_at": "2026-10-07T18:51:50Z"
        }
      ],
      "page": 1,
      "limit": 20,
      "total": 22
    }
  }
  ```

---

### `GET /api/v1/customers/:id`
Retrieves detailed profile for a specific customer, including associated contacts, deals, and recent activities.

- **Authentication:** Bearer Token
- **Response `200 OK`:**
  ```json
  {
    "success": true,
    "data": {
      "customer": {
        "id": "cust-abc",
        "name": "ABC Ltd",
        "email": "contact@abcltd.com",
        "company": "ABC Ltd"
      },
      "contacts": [
        { "id": "cnt-1", "name": "John Doe", "email": "john@abcltd.com", "role": "CEO" }
      ],
      "deals": [
        { "id": "deal-1", "title": "Enterprise Cloud Contract", "value": 1200000.0, "status": "open" }
      ],
      "activities": [
        { "id": "act-1", "type": "call", "subject": "Intro Call", "notes": "Discussed requirement" }
      ]
    }
  }
  ```
- **Errors:**
  - `404 Not Found`: Customer not found.

---

## 3. Deal APIs

### `GET /api/v1/deals`
Search and filter deals by status, minimum/maximum value, owner, or customer ID.

- **Authentication:** Bearer Token
- **Query Parameters:**
  - `status` (string, optional): `open` | `won` | `lost`
  - `min_value` (float, optional): Minimum deal value
  - `max_value` (float, optional): Maximum deal value
  - `owner_id` (string, optional): Owner user ID
  - `customer_id` (string, optional): Customer ID
- **Response `200 OK`:**
  ```json
  {
    "success": true,
    "data": {
      "items": [
        {
          "id": "deal-1",
          "title": "Enterprise Cloud Contract",
          "customer_id": "cust-abc",
          "customer_name": "ABC Ltd",
          "value": 1200000.0,
          "status": "open",
          "close_date": "2026-10-22T00:00:00Z"
        }
      ],
      "page": 1,
      "limit": 20,
      "total": 34
    }
  }
  ```

---

### `GET /api/v1/deals/summary`
Retrieves aggregated pipeline summary stats.

- **Authentication:** Bearer Token
- **Response `200 OK`:**
  ```json
  {
    "success": true,
    "data": {
      "total_customers": 22,
      "total_leads": 22,
      "total_open_deals": 24,
      "total_open_pipeline_value": 18550000.0,
      "total_won_value": 4200000.0,
      "top_5_customers": []
    }
  }
  ```

---

## 4. Activity & Lead APIs

### `GET /api/v1/activities`
Retrieves recent activity log entries.

- **Query Parameters:** `customer_id`, `type`, `limit` (default=20)

### `GET /api/v1/leads`
Retrieves sales leads.

- **Query Parameters:** `status`, `source`, `page`, `limit`
