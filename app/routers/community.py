from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List
from app.auth import get_current_user
from app.models.user import UserDB
from app.models.community import (
    CommunityPostCreate, CommunityPostDB, CommunityPostResponse,
    CommentCreate, CommentDB, CommentResponse, VoteType
)
from database import get_db
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/community", tags=["Community"])

# --- Posts ---

@router.get("/posts", response_model=List[CommunityPostResponse])
async def get_posts(
    skip: int = 0,
    limit: int = 20,
    sort_by: str = Query("recent", enum=["recent", "popular"]),
    current_user: UserDB = Depends(get_current_user)
):
    db = get_db()
    
    sort_criteria = [("created_at", -1)]
    if sort_by == "popular":
        sort_criteria = [("upvotes", -1), ("created_at", -1)]
        
    cursor = db["community_posts"].find({"_id": {"$ne": ""}}).sort(sort_criteria).skip(skip).limit(limit)
    posts = await cursor.to_list(length=limit)
    
    # Calculate user_vote for each post
    # This might be slow for many posts. Ideally we'd do an aggregation or separate query.
    # For now, let's do a separate query to find user's votes for these posts.
    
    post_ids = [p["_id"] for p in posts]
    user_votes = await db["post_votes"].find({
        "user_id": current_user.id,
        "post_id": {"$in": post_ids}
    }).to_list(length=len(posts))
    
    vote_map = {v["post_id"]: v["vote_type"] for v in user_votes}
    
    result = []
    for p in posts:
        # Pydantic via alias will handle _id -> id conversion
        p["user_vote"] = vote_map.get(p["_id"], 0)
        p["is_owner"] = str(p["author_id"]) == str(current_user.id)
        result.append(p)
        
    return result

@router.get("/my-posts", response_model=List[CommunityPostResponse])
async def get_my_posts(
    skip: int = 0,
    limit: int = 20,
    current_user: UserDB = Depends(get_current_user)
):
    db = get_db()
    
    # Query by mobile number if available, otherwise fallback to author_id
    query = {"author_id": current_user.id}
    if current_user.mobile_number:
         query = {"$or": [{"author_id": current_user.id}, {"author_mobile": current_user.mobile_number}]}
         
    cursor = db["community_posts"].find(query).sort("created_at", -1).skip(skip).limit(limit)
    posts = await cursor.to_list(length=limit)
    
    post_ids = [p["_id"] for p in posts]
    user_votes = await db["post_votes"].find({
        "user_id": current_user.id,
        "post_id": {"$in": post_ids}
    }).to_list(length=len(posts))
    
    vote_map = {v["post_id"]: v["vote_type"] for v in user_votes}
    
    result = []
    for p in posts:
        p["user_vote"] = vote_map.get(p["_id"], 0)
        p["is_owner"] = True
        result.append(p)
        
    return result

@router.post("/posts", response_model=CommunityPostResponse)
async def create_post(
    post: CommunityPostCreate,
    current_user: UserDB = Depends(get_current_user)
):
    db = get_db()
    
    new_post = CommunityPostDB(
        **post.dict(),
        author_id=current_user.id,
        author_name=current_user.name or "Anonymous Farmer",
        author_mobile=current_user.mobile_number
    )
    
    result = await db["community_posts"].insert_one(new_post.dict(by_alias=True))
    created_post = await db["community_posts"].find_one({"_id": result.inserted_id})
    created_post["is_owner"] = True
    return created_post

@router.get("/posts/{post_id}", response_model=CommunityPostResponse)
async def get_post(
    post_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    db = get_db()
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=400, detail="Invalid post ID")
        
    post = await db["community_posts"].find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    # Get user vote
    vote = await db["post_votes"].find_one({
        "user_id": current_user.id,
        "post_id": ObjectId(post_id)
    })
    
    post["user_vote"] = vote["vote_type"] if vote else 0
    post["is_owner"] = str(post["author_id"]) == str(current_user.id)
    return post

@router.put("/posts/{post_id}", response_model=CommunityPostResponse)
async def update_post(
    post_id: str,
    post_update: CommunityPostCreate,
    current_user: UserDB = Depends(get_current_user)
):
    db = get_db()
    
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=400, detail="Invalid post ID")
        
    post = await db["community_posts"].find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    if str(post["author_id"]) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to edit this post")
        
    update_data = {
        "title": post_update.title,
        "content": post_update.content,
        "tags": post_update.tags
    }
    
    await db["community_posts"].update_one(
        {"_id": ObjectId(post_id)},
        {"$set": update_data}
    )
    
    updated_post = await db["community_posts"].find_one({"_id": ObjectId(post_id)})
    
    # Get user vote (optional for edit response but good for consistency)
    vote = await db["post_votes"].find_one({
        "user_id": current_user.id,
        "post_id": ObjectId(post_id)
    })
    updated_post["user_vote"] = vote["vote_type"] if vote else 0
    updated_post["is_owner"] = True
    
    return updated_post

@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    db = get_db()
    
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=400, detail="Invalid post ID")
        
    post = await db["community_posts"].find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    if str(post["author_id"]) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
        
    # Delete post
    await db["community_posts"].delete_one({"_id": ObjectId(post_id)})
    
    # Delete associated comments
    await db["community_comments"].delete_many({"post_id": ObjectId(post_id)})
    
    # Delete associated votes (optional, but cleaner)
    await db["post_votes"].delete_many({"post_id": ObjectId(post_id)})
    
    return {"message": "Post deleted successfully"}

# --- Comments ---

@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
async def get_comments(
    post_id: str,
    skip: int = 0,
    limit: int = 50,
    current_user: UserDB = Depends(get_current_user)
):
    db = get_db()
    if not ObjectId.is_valid(post_id):
         raise HTTPException(status_code=400, detail="Invalid post ID")

    cursor = db["community_comments"].find({"post_id": ObjectId(post_id)}).sort("created_at", 1).skip(skip).limit(limit)
    comments = await cursor.to_list(length=limit)
    
    comment_ids = [c["_id"] for c in comments]
    user_votes = await db["comment_votes"].find({
        "user_id": current_user.id,
        "comment_id": {"$in": comment_ids}
    }).to_list(length=len(comments))
    
    vote_map = {v["comment_id"]: v["vote_type"] for v in user_votes}
    
    result = []
    for c in comments:
        c["user_vote"] = vote_map.get(c["_id"], 0)
        result.append(c)
        
    return result

@router.post("/posts/{post_id}/comments", response_model=CommentResponse)
async def create_comment(
    post_id: str,
    comment: CommentCreate,
    current_user: UserDB = Depends(get_current_user)
):
    db = get_db()
    if not ObjectId.is_valid(post_id):
         raise HTTPException(status_code=400, detail="Invalid post ID")
         
    # Check if post exists
    post = await db["community_posts"].find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    new_comment = CommentDB(
        **comment.dict(),
        post_id=ObjectId(post_id),
        author_id=current_user.id,
        author_name=current_user.name or "Anonymous Farmer"
    )
    
    result = await db["community_comments"].insert_one(new_comment.dict(by_alias=True))
    
    # Increment comment count on post
    await db["community_posts"].update_one(
        {"_id": ObjectId(post_id)},
        {"$inc": {"comment_count": 1}}
    )
    
    created_comment = await db["community_comments"].find_one({"_id": result.inserted_id})
    return created_comment

# --- Voting ---

@router.post("/posts/{post_id}/vote")
async def vote_post(
    post_id: str,
    vote: VoteType,
    current_user: UserDB = Depends(get_current_user)
):
    db = get_db()
    print(f"Vote request for post_id: '{post_id}'")
    if not ObjectId.is_valid(post_id):
         print(f"Invalid post ID: {post_id}")
         raise HTTPException(status_code=400, detail="Invalid post ID")

    pid = ObjectId(post_id)
    uid = current_user.id
    
    # Check existing vote
    existing_vote = await db["post_votes"].find_one({"user_id": uid, "post_id": pid})
    
    if existing_vote:
        previous_vote = existing_vote["vote_type"]
        if previous_vote == vote.vote_type:
             return {"message": "Already voted"}
        
        # Changing vote (e.g. 1 to -1, or 1 to 0)
        # Update counts
        inc_update = {}
        if previous_vote == 1:
            inc_update["upvotes"] = -1
        elif previous_vote == -1:
            inc_update["downvotes"] = -1
            
        if vote.vote_type == 1:
            inc_update["upvotes"] = inc_update.get("upvotes", 0) + 1
        elif vote.vote_type == -1:
             inc_update["downvotes"] = inc_update.get("downvotes", 0) + 1
             
        if vote.vote_type == 0:
            await db["post_votes"].delete_one({"_id": existing_vote["_id"]})
        else:
            await db["post_votes"].update_one(
                {"_id": existing_vote["_id"]},
                {"$set": {"vote_type": vote.vote_type}}
            )
            
        if inc_update:
            await db["community_posts"].update_one(
                {"_id": pid},
                {"$inc": inc_update}
            )
            
    else:
        # New vote
        if vote.vote_type == 0:
            return {"message": "No vote to remove"}
            
        await db["post_votes"].insert_one({
            "user_id": uid,
            "post_id": pid,
            "vote_type": vote.vote_type
        })
        
        inc_update = {}
        if vote.vote_type == 1:
            inc_update["upvotes"] = 1
        elif vote.vote_type == -1:
            inc_update["downvotes"] = 1
            
        await db["community_posts"].update_one(
            {"_id": pid},
            {"$inc": inc_update}
        )
        
    return {"message": "Vote recorded"}

@router.post("/comments/{comment_id}/vote")
async def vote_comment(
    comment_id: str,
    vote: VoteType,
    current_user: UserDB = Depends(get_current_user)
):
    db = get_db()
    if not ObjectId.is_valid(comment_id):
         raise HTTPException(status_code=400, detail="Invalid comment ID")

    cid = ObjectId(comment_id)
    uid = current_user.id
    
    # Check existing vote
    existing_vote = await db["comment_votes"].find_one({"user_id": uid, "comment_id": cid})
    
    if existing_vote:
        previous_vote = existing_vote["vote_type"]
        if previous_vote == vote.vote_type:
             return {"message": "Already voted"}
        
        # Changing vote
        inc_update = {}
        if previous_vote == 1:
            inc_update["upvotes"] = -1
        elif previous_vote == -1:
            inc_update["downvotes"] = -1
            
        if vote.vote_type == 1:
            inc_update["upvotes"] = inc_update.get("upvotes", 0) + 1
        elif vote.vote_type == -1:
             inc_update["downvotes"] = inc_update.get("downvotes", 0) + 1
             
        if vote.vote_type == 0:
            await db["comment_votes"].delete_one({"_id": existing_vote["_id"]})
        else:
            await db["comment_votes"].update_one(
                {"_id": existing_vote["_id"]},
                {"$set": {"vote_type": vote.vote_type}}
            )
            
        if inc_update:
            await db["community_comments"].update_one(
                {"_id": cid},
                {"$inc": inc_update}
            )
            
    else:
        # New vote
        if vote.vote_type == 0:
            return {"message": "No vote to remove"}
            
        await db["comment_votes"].insert_one({
            "user_id": uid,
            "comment_id": cid,
            "vote_type": vote.vote_type
        })
        
        inc_update = {}
        if vote.vote_type == 1:
            inc_update["upvotes"] = 1
        elif vote.vote_type == -1:
            inc_update["downvotes"] = 1
            
        await db["community_comments"].update_one(
            {"_id": cid},
            {"$inc": inc_update}
        )
        
    return {"message": "Vote recorded"}
