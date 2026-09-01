from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client


# Weka API Keys zako halisi hapa ndani ya alama za nukuu
SUPABASE_URL =" https://gsizvosbufsyccybfbjp.supabase.co"
SUPABASE_KEY = "sb_publishable_Vp-sRKSA-v9JlvZdY4PXcg__-zSVl6_.." 

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Products API")

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0

@app.get("/products")
def get_products():
    response = supabase.table("products").select("*").execute()
    return response.data

@app.post("/products")
def create_product(product: ProductCreate):
    response = supabase.table("products").insert(product.model_dump()).execute()
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to create product")
    return response.data[0]


supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Products API")

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0

@app.get("/products")
def get_products():
    response = supabase.table("products").select("*").execute()
    return response.data

@app.post("/products")
def create_product(product: ProductCreate):
    response = supabase.table("products").insert(product.model_dump()).execute()
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to create product")
    return response.data[0]
