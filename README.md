# SSLCommerz Payment Integration — FastAPI Backend

A lightweight, asynchronous FastAPI backend designed to demonstrate payment processing integration with **SSLCommerz API v4** using `httpx` and `pydantic-settings`.

---

## Features

- **Asynchronous Execution:** Fast, non-blocking HTTP requests using `httpx`.
- **Environment Management:** Powered by `pydantic-settings` to parse configuration and `.env` files with type safety.
- **Server-Side Order Validation:** Verifies payment authenticity directly against SSLCommerz servers to prevent client-side request tampering.
- **In-Memory Order Tracking:** Ideal for rapid prototyping without needing database drivers configured.
- **CORS Configured:** Prepared for cross-origin requests from React/Vite local dev servers.

---

## Project Structure

```text
backend/
├── pyproject.toml
├── .env
└── src/
    └── backend/
        ├── __init__.py
        └── main.py
PrerequisitesPython 3.10+uv (Modern, fast Python package manager)SSLCommerz Sandbox Credentials (Store ID & Password)Quick Start1. InstallationFrom the backend/ directory, install all required dependencies:Bashuv add "fastapi[standard]" httpx pydantic-settings
2. Environment ConfigurationCreate a .env file in the root backend/ folder (next to pyproject.toml):Code snippetSSLCOMMERZ_STORE_ID=your_store_id_here
SSLCOMMERZ_STORE_PASSWORD=your_store_passwd_here
SSLCOMMERZ_IS_SANDBOX=true
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
3. Run Development ServerLaunch the FastAPI application with auto-reloading enabled:Bashuv run fastapi dev src/backend/main.py
The backend server will start at http://localhost:8000. You can inspect the automatically generated Swagger documentation at http://localhost:8000/docs.API DocumentationMethodEndpointDescriptionExpected PayloadPOST/api/payInitiates payment session with SSLCommerz.Query param: amount (e.g., 500.0)POST/payment/successCallback endpoint for successful payments.Form data: val_id, tran_idPOST/payment/failCallback endpoint for failed payment attempts.Form data: tran_idPOST/payment/cancelCallback endpoint for user-cancelled transactions.Form data: tran_idPayment Flow MechanicsInitiation (/api/pay):Backend generates a unique UUID-based transaction ID (tran_id).Sends customer info and callback URLs to SSLCommerz (gwprocess/v4/api.php).Returns a GatewayPageURL to the React client.Redirect & User Payment:Customer completes payment on SSLCommerz's hosted payment gateway.Validation & Redirect (/payment/success):SSLCommerz POSTs callback data (val_id, tran_id) back to FastAPI.FastAPI issues a GET request to SSLCommerz's Validation API (validator/api/validationserverAPI.php) to confirm status is VALID or VALIDATED.FastAPI issues an HTTP 303 Redirect back to the frontend (FRONTEND_URL?status=success&tran_id=...).LicenseThis project is open-source and intended for educational/testing purposes.