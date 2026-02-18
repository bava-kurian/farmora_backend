from fastapi import APIRouter, Depends, HTTPException, Body
from app.auth import get_current_user
from app.models.user import UserDB
from app.models.store import Product, Cart, CartItem, CartResponse
from database import get_db
from typing import List, Optional
from bson import ObjectId

router = APIRouter(prefix="/store", tags=["Store"])

@router.get("/products", response_model=List[Product])
async def get_products(category: Optional[str] = None):
    db = get_db()
    query = {}
    if category:
        query["category"] = category
    
    products = await db["products"].find(query).to_list(length=100)
    return [Product(**p) for p in products]

@router.get("/cart", response_model=CartResponse)
async def get_cart(current_user: UserDB = Depends(get_current_user)):
    db = get_db()
    cart = await db["carts"].find_one({"user_id": current_user.mobile_number})
    
    if not cart:
        return CartResponse(items=[], total_price=0.0, total_items=0)
    
    cart_items = cart.get("items", [])
    detailed_items = []
    total_price = 0.0
    total_items = 0
    
    product_ids = [ObjectId(item["product_id"]) for item in cart_items]
    products = await db["products"].find({"_id": {"$in": product_ids}}).to_list(length=len(product_ids))
    product_map = {str(p["_id"]): p for p in products}
    
    for item in cart_items:
        pid = item["product_id"]
        qty = item["quantity"]
        if pid in product_map:
            product = product_map[pid]
            # Ensure product has 'our_price', defaulting to 0 if missing for safety
            price = product.get("our_price", 0.0)
            item_total = price * qty
            total_price += item_total
            total_items += qty
            
            detailed_items.append({
                "product": Product(**product),
                "quantity": qty,
                "item_total": item_total
            })
            
    return CartResponse(items=detailed_items, total_price=total_price, total_items=total_items)

@router.post("/cart/add")
async def add_to_cart(
    item: CartItem,
    current_user: UserDB = Depends(get_current_user)
):
    db = get_db()
    
    # Verify product exists
    try:
        product = await db["products"].find_one({"_id": ObjectId(item.product_id)})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
    except Exception:
         raise HTTPException(status_code=400, detail="Invalid product ID")

    cart = await db["carts"].find_one({"user_id": current_user.mobile_number})
    
    if not cart:
        # Create new cart
        new_cart = {
            "user_id": current_user.mobile_number,
            "items": [{"product_id": item.product_id, "quantity": item.quantity}]
        }
        await db["carts"].insert_one(new_cart)
    else:
        # Update existing cart
        items = cart.get("items", [])
        found = False
        for i in items:
            if i["product_id"] == item.product_id:
                i["quantity"] += item.quantity
                found = True
                break
        
        if not found:
            items.append({"product_id": item.product_id, "quantity": item.quantity})
            
        await db["carts"].update_one(
            {"user_id": current_user.mobile_number},
            {"$set": {"items": items}}
        )
        
    return {"message": "Item added to cart"}

@router.post("/cart/remove")
async def remove_from_cart(
    item: CartItem, # Reusing CartItem for input, ignoring quantity for full removal or handling decrement logic if needed. 
                    # For simplicity, let's say this removes the item entirely or decrements.
                    # As per user request "proper cart", let's support removing specific product.
    current_user: UserDB = Depends(get_current_user)
):
    db = get_db()
    cart = await db["carts"].find_one({"user_id": current_user.mobile_number})
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
        
    items = cart.get("items", [])
    # Remove item completely
    new_items = [i for i in items if i["product_id"] != item.product_id]
    
    await db["carts"].update_one(
        {"user_id": current_user.mobile_number},
        {"$set": {"items": new_items}}
    )
    return {"message": "Item removed from cart"}

@router.post("/checkout")
async def checkout(current_user: UserDB = Depends(get_current_user)):
    db = get_db()
    # Clear cart
    await db["carts"].delete_one({"user_id": current_user.mobile_number})
    return {"message": "Order placed successfully (Mock)"}
