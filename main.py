import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import Client, create_client

# 1. Supabase Credentials
SUPABASE_URL = "https://gsizvosbufsyccybfbjp.supabase.co"
SUPABASE_KEY = "sb_publishable_Vp-sRKSA-v9J1vZdY4PXcg__-zSV16"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. Malipopay Live Credentials
MALIPOPAY_KEY_ID = "5NZ1iEzacdi5"
MALIPOPAY_SECRET_KEY = "mp_sk_prod_U2FsdGVkX1/wJtS7hbttBICxjwuOyxtMrGJJQhqEQQ84xkOEYKiLVD3w2prI/NiR6CYUZZzk1Hli7hbRYg39TpIWj9HiLzWzKknQV+fZky/VnDq6yvvSFVHKYwpPb3ib2niqb5Mtk9ZwY+PP3Gmw5fjnPH0KBcACKXEkeQqdA5uj9jl/8mzA0vHF2X48Krom"
MALIPOPAY_URL = "https://core-prod.malipopay.co.tz/api/v1/payment/collection"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PaymentRequest(BaseModel):
    phone_number: str
    amount: float


@app.get("/")
def read_root():
    return {"status": "Backend ipo tayari!"}


@app.post("/pay")
async def process_payment(payment: PaymentRequest):
    # Malipopay inatumia Secret Key kwenye Authorization Header
    headers = {
        "Authorization": f"Bearer {MALIPOPAY_SECRET_KEY}",
        "X-Key-Id": MALIPOPAY_KEY_ID,
        "apiToken": MALIPOPAY_SECRET_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "reference": "ACC-SUB-PLAN",
        "description": "Malipo ya Kifurushi cha AI Sales Assistant",
        "amount": payment.amount,
        "phoneNumber": payment.phone_number,
        "amountType": "FULL",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                MALIPOPAY_URL, json=payload, headers=headers, timeout=30.0
            )

            res_data = response.json()

            if response.status_code in [200, 201] and (
                res_data.get("success") or res_data.get("status") == "success"
            ):
                supabase.table("transactions").insert(
                    {
                        "phone_number": payment.phone_number,
                        "amount": payment.amount,
                        "status": "pending",
                        "malipopay_ref": res_data.get("reference", ""),
                    }
                ).execute()

                return {
                    "success": True,
                    "message": "Ujumbe wa kuweka PIN unatumwa kwenye simu!",
                    "data": res_data,
                }
            else:
                return {
                    "success": False,
                    "detail": res_data.get("message")
                    or res_data.get("error")
                    or response.text,
                }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Malipopay Connection Error: {str(e)}"
            )
