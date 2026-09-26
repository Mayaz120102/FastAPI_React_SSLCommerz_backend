SSLCommerz Payment Integration — FastAPI Backend

A lightweight, asynchronous FastAPI backend demonstrating payment processing integration with the SSLCommerz API v4 using httpx and pydantic-settings.

Features

Asynchronous Execution: Fast, non-blocking HTTP requests using httpx.

Environment Management: Uses pydantic-settings to parse configuration from environment variables and .env files with type safety.

Server-Side Order Validation: Verifies payment authenticity directly against SSLCommerz servers to prevent client-side request tampering.

In-Memory Order Tracking: Suitable for rapid prototyping without requiring database drivers.

CORS Configured: Prepared for cross-origin requests from React/Vite local development servers.

Project Structure
backend/
├── pyproject.toml
├── .env
└── src/
    └── backend/
        ├── __init__.py
        └── main.py

Prerequisites

Before getting started, make sure you have:

Python 3.10+

uv
 — Modern, fast Python package manager

SSLCommerz Sandbox credentials

Store ID

Store Password

Quick Start
1. Installation

From the backend/ directory, install the required dependencies:

uv add "fastapi[standard]" httpx pydantic-settings

2. Environment Configuration

Create a .env file in the root backend/ directory, next to pyproject.toml:

SSLCOMMERZ_STORE_ID=your_store_id_here
SSLCOMMERZ_STORE_PASSWORD=your_store_password_here
SSLCOMMERZ_IS_SANDBOX=true
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173


Important: Never commit your real SSLCommerz credentials or .env file to version control.

You can add .env to your .gitignore:

.env

3. Run the Development Server

Launch the FastAPI application with auto-reloading enabled:

uv run fastapi dev src/backend/main.py


The backend will start at:

http://localhost:8000

4. Open API Documentation

FastAPI automatically provides interactive Swagger documentation at:

http://localhost:8000/docs

API Documentation
Method	Endpoint	Description	Expected Payload
POST	/api/pay	Initiates a payment session with SSLCommerz	Query parameter: amount (e.g. 500.0)
POST	/payment/success	Callback endpoint for successful payments	Form data: val_id, tran_id
POST	/payment/fail	Callback endpoint for failed payment attempts	Form data: tran_id
POST	/payment/cancel	Callback endpoint for cancelled transactions	Form data: tran_id
Payment Flow

The payment integration follows this general flow:

React/Vite Frontend
        │
        │ POST /api/pay?amount=500
        ▼
FastAPI Backend
        │
        │ Create transaction
        │ Send payment request
        ▼
SSLCommerz Gateway
        │
        │ Customer completes payment
        ▼
SSLCommerz Callback
        │
        │ POST /payment/success
        ▼
FastAPI Backend
        │
        │ Validate transaction
        ▼
SSLCommerz Validation API
        │
        │ VALID / VALIDATED
        ▼
FastAPI
        │
        │ HTTP 303 Redirect
        ▼
React/Vite Frontend

Payment Flow Mechanics
1. Payment Initiation

The frontend sends a request to:

POST /api/pay?amount=500.0


The backend then:

Generates a unique UUID-based transaction ID (tran_id).

Stores the order in the in-memory order tracker.

Sends the customer and transaction information to SSLCommerz.

Uses the SSLCommerz gateway endpoint:

gwprocess/v4/api.php


Returns the SSLCommerz GatewayPageURL to the frontend.

The frontend can then redirect the customer to the returned gateway URL.

2. Customer Payment

The customer completes the payment on the SSLCommerz-hosted payment gateway.

SSLCommerz then sends the payment result to the appropriate callback endpoint configured by the backend.

3. Successful Payment Validation

For successful payments, SSLCommerz sends a request to:

POST /payment/success


The callback includes information such as:

val_id
tran_id


The backend does not blindly trust the callback.

Instead, it sends a server-to-server request to the SSLCommerz Validation API:

validator/api/validationserverAPI.php


The transaction is considered valid only when the validation response indicates an appropriate valid status such as:

VALID


or

VALIDATED


This server-side validation helps prevent clients from manipulating payment status information.

4. Redirect to Frontend

After successful validation, the backend redirects the customer back to the configured frontend URL using HTTP 303 See Other:

http://localhost:5173?status=success&tran_id=<transaction_id>


The frontend can use the status and tran_id query parameters to display the appropriate payment result.

Callback Endpoints
Successful Payment
POST /payment/success


Expected form fields:

val_id
tran_id


The backend validates the transaction against SSLCommerz before marking the order as successful.

Failed Payment
POST /payment/fail


Expected form field:

tran_id


The corresponding order is marked as failed before redirecting the customer to the frontend.

Cancelled Payment
POST /payment/cancel


Expected form field:

tran_id


The corresponding order is marked as cancelled before redirecting the customer to the frontend.

Configuration

The application uses environment variables for configuration.

Variable	Description	Example
SSLCOMMERZ_STORE_ID	SSLCommerz Store ID	your_store_id
SSLCOMMERZ_STORE_PASSWORD	SSLCommerz Store Password	your_store_password
SSLCOMMERZ_IS_SANDBOX	Enables/disables sandbox mode	true
BACKEND_URL	Public/backend callback URL	http://localhost:8000
FRONTEND_URL	Frontend redirect URL	http://localhost:5173
Development Notes
In-Memory Order Tracking

This example uses an in-memory data structure to keep track of orders.

This is useful for:

Learning

Local development

Prototyping

Testing the payment flow

However, in-memory storage is not suitable for production because data will be lost whenever the application restarts, and it does not work reliably across multiple backend instances.

For production, replace it with a persistent database such as PostgreSQL, MySQL, or another suitable database.

CORS

The backend is configured to support cross-origin requests from the React/Vite development server:

http://localhost:5173


If your frontend runs on a different origin, update the CORS configuration accordingly.

HTTPS

For real-world payment integration, callback URLs should use HTTPS and be publicly reachable by SSLCommerz.

For local development, a tunneling service can be used to expose your local backend when required.

Security Considerations

Before using this project in production:

Never expose SSLCommerz Store Passwords to the frontend.

Keep credentials in environment variables or a secure secrets manager.

Never trust payment status received directly from the client.

Always validate successful transactions server-side.

Store orders and payment states in a persistent database.

Use HTTPS for production callback endpoints.

Validate transaction IDs against your own order records.

Verify the payment amount and currency against the original order.

Implement appropriate idempotency handling for repeated callbacks.

Do not commit .env files or credentials to Git.

Add authentication/authorization to internal order-management endpoints as needed.

Testing

A typical local development flow is:

1. Start the FastAPI backend
2. Start the React/Vite frontend
3. Create a payment from the frontend
4. Redirect to SSLCommerz Sandbox
5. Complete the sandbox payment
6. SSLCommerz calls the backend callback
7. Backend validates the transaction
8. Backend redirects to the frontend
9. Frontend displays the payment result

API Documentation

Once the server is running, you can access the automatically generated API documentation:

Swagger UI:
http://localhost:8000/docs

ReDoc:
http://localhost:8000/redoc

License

This project is open-source and intended for educational and testing purposes.

Before deploying to production, review SSLCommerz's current API documentation, security requirements, callback behavior, and production integration requirements.