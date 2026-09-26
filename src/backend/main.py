import uuid
from typing import Dict
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    sslcommerz_store_id: str
    sslcommerz_store_password: str
    sslcommerz_is_sandbox: bool = True
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()


app = FastAPI(title="SSLCommerz FastAPI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 3. SSLCommerz Endpoints
INIT_URL = (
    "https://sandbox.sslcommerz.com/gwprocess/v4/api.php"
    if settings.sslcommerz_is_sandbox
    else "https://securepay.sslcommerz.com/gwprocess/v4/api.php"
)
VALIDATION_URL = (
    "https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php"
    if settings.sslcommerz_is_sandbox
    else "https://securepay.sslcommerz.com/validator/api/validationserverAPI.php"
)

# Temporary memory to track orders (No DB needed)
orders_db: Dict[str, dict] = {}


# 4. Route to initialize the payment session
@app.post("/api/pay")
async def init_payment(amount: float = 100.0):
    tran_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"

    payload = {
        "store_id": settings.sslcommerz_store_id,
        "store_passwd": settings.sslcommerz_store_password,
        "total_amount": str(amount),
        "currency": "BDT",
        "tran_id": tran_id,
        "success_url": f"{settings.backend_url}/payment/success",
        "fail_url": f"{settings.backend_url}/payment/fail",
        "cancel_url": f"{settings.backend_url}/payment/cancel",
        "cus_name": "Test Customer",
        "cus_email": "test@example.com",
        "cus_add1": "Dhaka",
        "cus_city": "Dhaka",
        "cus_postcode": "1200",
        "cus_country": "Bangladesh",
        "cus_phone": "01700000000",
        "shipping_method": "NO",
        "product_name": "Test Product",
        "product_category": "General",
        "product_profile": "general",
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(INIT_URL, data=payload)
        data = res.json()

    if data.get("status") == "SUCCESS":
        orders_db[tran_id] = {"amount": amount, "status": "PENDING"}
        return {"payment_url": data["GatewayPageURL"], "tran_id": tran_id}

    raise HTTPException(
        status_code=400,
        detail=data.get("failedreason", "Failed to start SSLCommerz payment"),
    )


# 5. Success Callback from SSLCommerz
@app.post("/payment/success")
async def payment_success(val_id: str = Form(...), tran_id: str = Form(...)):
    # Validate transaction with SSLCommerz Server
    params = {
        "val_id": val_id,
        "store_id": settings.sslcommerz_store_id,
        "store_passwd": settings.sslcommerz_store_password,
        "format": "json",
    }
    async with httpx.AsyncClient() as client:
        res = await client.get(VALIDATION_URL, params=params)
        val_data = res.json()

    if val_data.get("status") in ["VALID", "VALIDATED"]:
        if tran_id in orders_db:
            orders_db[tran_id]["status"] = "PAID"
        return RedirectResponse(
            url=f"{settings.frontend_url}?status=success&tran_id={tran_id}",
            status_code=303,
        )

    return RedirectResponse(
        url=f"{settings.frontend_url}?status=failed&tran_id={tran_id}",
        status_code=303,
    )



# 6. Fail Callback
@app.post("/payment/fail")
async def payment_fail(tran_id: str = Form(...)):
    if tran_id in orders_db:
        orders_db[tran_id]["status"] = "FAILED"
    return RedirectResponse(
        url=f"{settings.frontend_url}?status=failed&tran_id={tran_id}",
        status_code=303,
    )


# 7. Cancel Callback
@app.post("/payment/cancel")
async def payment_cancel(tran_id: str = Form(...)):
    if tran_id in orders_db:
        orders_db[tran_id]["status"] = "CANCELLED"
    return RedirectResponse(
        url=f"{settings.frontend_url}?status=cancelled&tran_id={tran_id}",
        status_code=303,
    )