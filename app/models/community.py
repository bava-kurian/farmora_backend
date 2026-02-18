from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.shared import PyObjectId
from bson import ObjectId

# --- Post Models ---

class CommunityPostBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=10)
    tags: List[str] = []

class CommunityPostCreate(CommunityPostBase):
    pass

class CommunityPostDB(CommunityPostBase):
    id: PyObjectId = Field(default_factory=lambda: PyObjectId(ObjectId()), alias="_id")
    author_id: PyObjectId
    author_name: str
    author_mobile: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    upvotes: int = 0
    downvotes: int = 0
    comment_count: int = 0
    
    class Config:
        populate_by_name = True
        json_encoders = {PyObjectId: str}

class CommunityPostResponse(CommunityPostBase):
    id: PyObjectId = Field(alias="_id")
    author_name: str
    author_mobile: Optional[str] = None
    created_at: datetime
    upvotes: int
    downvotes: int
    comment_count: int
    user_vote: Optional[int] = Field(0, description="1 for upvote, -1 for downvote, 0 for none")
    is_owner: bool = Field(False, description="True if current user is the author")

    class Config:
        populate_by_name = True

# --- Comment Models ---

class CommentBase(BaseModel):
    content: str = Field(..., min_length=1)

class CommentCreate(CommentBase):
    pass

class CommentDB(CommentBase):
    id: PyObjectId = Field(default_factory=lambda: PyObjectId(ObjectId()), alias="_id")
    post_id: PyObjectId
    author_id: PyObjectId
    author_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    upvotes: int = 0
    downvotes: int = 0
    
    class Config:
        populate_by_name = True
        json_encoders = {PyObjectId: str}

class CommentResponse(CommentBase):
    id: PyObjectId = Field(alias="_id")
    post_id: PyObjectId
    author_id: PyObjectId
    author_name: str
    created_at: datetime
    upvotes: int
    downvotes: int
    user_vote: Optional[int] = Field(0, description="1 for upvote, -1 for downvote, 0 for none")

    class Config:
        populate_by_name = True

# --- Vote Models ---

class VoteType(BaseModel):
    vote_type: int = Field(..., description="1 for upvote, -1 for downvote, 0 to remove vote")
