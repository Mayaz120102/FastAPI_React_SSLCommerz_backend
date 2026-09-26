# SSLCommerz Payment Integration — FastAPI Backend

A lightweight, asynchronous **FastAPI backend** designed to demonstrate payment processing integration with **SSLCommerz API v4** using `httpx` and `pydantic-settings`.

## Features

- **Asynchronous Execution:** Fast, non-blocking HTTP requests using `httpx`.
- **Environment Management:** Powered by `pydantic-settings` to parse configuration and `.env` files with type safety.
- **Server-Side Order Validation:** Verifies payment authenticity directly against SSLCommerz servers to prevent client-side request tampering.
- **In-Memory Order Tracking:** Ideal for rapid prototyping without needing database drivers configured.
- **CORS Configured:** Prepared for cross-origin requests from React/Vite local dev servers.

## Project Structure

```text
backend/
├── pyproject.toml
├── .env
└── src/
    └── backend/
        ├── __init__.py
        └── main.py
```

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) — Modern, fast Python package manager
- SSLCommerz Sandbox Credentials
  - Store ID
  - Store Password

## Quick Start

### 1. Installation

From the `backend/` directory, install all required dependencies:

```bash
uv add "fastapi[standard]" httpx pydantic-settings
```

### 2. Environment Configuration

Create a `.env` file in the root `backend/` folder, next to `pyproject.toml`:

```env
SSLCOMMERZ_STORE_ID=your_store_id_here
SSLCOMMERZ_STORE_PASSWORD=your_store_password_here
SSLCOMMERZ_IS_SANDBOX=true
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

> **Important:** Never commit your real SSLCommerz credentials or `.env` file to Git.

Add `.env` to your `.gitignore`:

```gitignore
.env
```

### 3. Run Development Server

Launch the FastAPI application with auto-reloading enabled:

```bash
uv run fastapi dev src/backend/main.py
```

The backend server will start at:

```text
http://localhost:8000
```

You can inspect the automatically generated Swagger documentation at:

```text
http://localhost:8000/docs
```

## API Documentation

| Method | Endpoint           | Description                                       | Expected Payload                         |
| ------ | ------------------ | ------------------------------------------------- | ---------------------------------------- |
| `POST` | `/api/pay`         | Initiates payment session with SSLCommerz         | Query parameter: `amount` (e.g. `500.0`) |
| `POST` | `/payment/success` | Callback endpoint for successful payments         | Form data: `val_id`, `tran_id`           |
| `POST` | `/payment/fail`    | Callback endpoint for failed payment attempts     | Form data: `tran_id`                     |
| `POST` | `/payment/cancel`  | Callback endpoint for user-cancelled transactions | Form data: `tran_id`                     |

## Payment Flow Mechanics

### 1. Payment Initiation

The frontend sends a request to:

```http
POST /api/pay?amount=500.0
```

The backend then:

1. Generates a unique UUID-based transaction ID (`tran_id`).
2. Stores the order in the in-memory order tracker.
3. Sends customer information and callback URLs to SSLCommerz.
4. Sends the payment request to the SSLCommerz API:

```text
gwprocess/v4/api.php
```

5. Returns the `GatewayPageURL` to the React client.

The frontend can then redirect the customer to the returned gateway URL.

### 2. Customer Payment

The customer completes the payment on the SSLCommerz-hosted payment gateway.

After the payment is completed, SSLCommerz sends the result to the appropriate callback endpoint configured by the backend.

### 3. Successful Payment Validation

For successful payments, SSLCommerz sends a POST request to:

```http
POST /payment/success
```

The callback contains information such as:

```text
val_id
tran_id
```

The backend does **not** blindly trust the callback.

Instead, it sends a server-to-server request to the SSLCommerz Validation API:

```text
validator/api/validationserverAPI.php
```

The backend confirms that the transaction status is:

```text
VALID
```

or:

```text
VALIDATED
```

This server-side validation helps prevent client-side request tampering.

### 4. Redirect to Frontend

After successful validation, the backend issues an HTTP `303` redirect back to the frontend:

```text
http://localhost:5173?status=success&tran_id=<transaction_id>
```

The frontend can use the `status` and `tran_id` query parameters to display the appropriate payment result.

## Callback Endpoints

### Successful Payment

```http
POST /payment/success
```

Expected form data:

```text
val_id
tran_id
```

The backend validates the transaction against SSLCommerz before marking the order as successful.

### Failed Payment

```http
POST /payment/fail
```

Expected form data:

```text
tran_id
```

The corresponding order is marked as failed before redirecting the customer to the frontend.

### Cancelled Payment

```http
POST /payment/cancel
```

Expected form data:

```text
tran_id
```

The corresponding order is marked as cancelled before redirecting the customer to the frontend.

## Configuration

The application uses environment variables for configuration.

| Variable                    | Description                   | Example                 |
| --------------------------- | ----------------------------- | ----------------------- |
| `SSLCOMMERZ_STORE_ID`       | SSLCommerz Store ID           | `your_store_id`         |
| `SSLCOMMERZ_STORE_PASSWORD` | SSLCommerz Store Password     | `your_store_password`   |
| `SSLCOMMERZ_IS_SANDBOX`     | Enables/disables sandbox mode | `true`                  |
| `BACKEND_URL`               | Backend callback URL          | `http://localhost:8000` |
| `FRONTEND_URL`              | Frontend redirect URL         | `http://localhost:5173` |

## Development Notes

### In-Memory Order Tracking

This project uses in-memory storage to keep track of orders.

This is useful for:

- Learning
- Local development
- Prototyping
- Testing the payment flow

However, in-memory storage is **not suitable for production** because data will be lost when the application restarts.

For production, replace it with a persistent database such as PostgreSQL or MySQL.

### CORS

The backend is configured to support cross-origin requests from the React/Vite development server:

```text
http://localhost:5173
```

If your frontend runs on a different origin, update the CORS configuration accordingly.

### HTTPS

For production payment integration, callback URLs should use HTTPS and be publicly reachable by SSLCommerz.

For local development, you can use a tunneling service when SSLCommerz needs to reach your local backend.

## Security Considerations

Before using this project in production:

- Never expose SSLCommerz Store Passwords to the frontend.
- Keep credentials in environment variables or a secure secrets manager.
- Never trust payment status received directly from the client.
- Always validate successful transactions server-side.
- Store orders and payment states in a persistent database.
- Use HTTPS for production callback endpoints.
- Verify the transaction ID against your own order records.
- Verify the payment amount and currency against the original order.
- Implement idempotency handling for repeated callbacks.
- Never commit `.env` files or credentials to Git.

## Testing

A typical local development flow:

```text
1. Start the FastAPI backend
2. Start the React/Vite frontend
3. Create a payment from the frontend
4. Redirect to SSLCommerz Sandbox
5. Complete the sandbox payment
6. SSLCommerz calls the backend callback
7. Backend validates the transaction
8. Backend redirects to the frontend
9. Frontend displays the payment result
```

## API Documentation

Once the server is running:

### Swagger UI

```text
http://localhost:8000/docs
```

### ReDoc

```text
http://localhost:8000/redoc
```

## License

This project is open-source and intended for **educational and testing purposes**.

Before deploying to production, review the current SSLCommerz API documentation, security requirements, callback behavior, and production integration requirements.
