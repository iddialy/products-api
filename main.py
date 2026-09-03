import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import Client, create_client

# 1. Taarifa za Supabase
SUPABASE_URL = "https://gsizvosbufsyccybfbjp.supabase.co"
SUPABASE_KEY = "sb_publishable_Vp-sRKSA-v9J1vZdY4PXcg__-zSV16"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. Taarifa za Malipopay (API Credentials)
MALIPOPAY_KEY_ID = "zCuKwFrmB-1n"
MALIPOPAY_PUBLIC_KEY = (
    "mp_pk_prod_U2FsdGVkX1+93j0i8/1vLvhjP+I9Gv6NH74O"  # Key yako ya Malipopay
)
MALIPOPAY_URL = "https://api.malipopay.co.tz/v1/payments/charge"

app = FastAPI()

# Kuruhusu Front-End (Website yako ya GitHub Pages) iweze kuwasiliana na Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Muundo wa taarifa za ombi la malipo kutoka kwenye Web Form
class PaymentRequest(BaseModel):
    phone_number: str  # Mfano: 2557XXXXXXXX
    amount: float  # Kiasi cha kulipia huduma
    reference_id: str = None


@app.get("/")
def read_root():
    return {"status": "Backend na Malipopay ziko tayari kazi!"}


# Endpoint ya kuanzisha muamala na kutuma USSD Push kwenye simu ya mteja
@app.post("/pay")
async def process_payment(payment: PaymentRequest):
    headers = {
        "X-Key-Id": MALIPOPAY_KEY_ID,
        "Authorization": f"Bearer {MALIPOPAY_PUBLIC_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "phone_number": payment.phone_number,
        "amount": payment.amount,
        "currency": "TZS",
        "description": "Malipo ya AI Sales Assistant Access",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                MALIPOPAY_URL, json=payload, headers=headers, timeout=30.0
            )

            if response.status_code in [200, 201]:
                res_data = response.json()
                # Hifadhi kumbukumbu ya muamala Supabase
                supabase.table("transactions").insert(
                    {
                        "phone_number": payment.phone_number,
                        "amount": payment.amount,
                        "status": "pending",
                        "malipopay_ref": res_data.get("transaction_id", ""),
                    }
                ).execute()

                return {
                    "success": True,
                    "message": "Ujumbe wa kuweka PIN unatumwa kwenye simu ya mteja!",
                    "data": res_data,
                }
            else:
                raise HTTPException(
                    status_code=response.status_code, detail=response.text
                )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Malipopay API Error: {str(e)}"
            )
