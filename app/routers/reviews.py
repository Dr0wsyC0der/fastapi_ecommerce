from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update


from app.auth import get_current_buyer, get_current_admin
from app.db_depends import get_async_db
from app.models import Product as ProductModel
from app.models.reviews import Review as ReviewModel
from app.schemas import Review as ReviewSchema, ReviewCreate

router = APIRouter(prefix="/reviews", tags=["reviews"])


async def update_product_rating(db: AsyncSession, product_id: int):
    result = await db.execute(
        select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active == True
        )
    )
    avg_rating = result.scalar() or 0.0
    product = await db.get(ProductModel, product_id)
    product.rating = avg_rating

@router.get("/", response_model=list[ReviewSchema])
async def get_all_reviews(db: AsyncSession = Depends(get_async_db)):
    stmt = await db.scalars(select(ReviewModel).where(ReviewModel.is_active == True))
    reviews = stmt.all()
    return reviews

@router.post("/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(review: ReviewCreate, current_user = Depends(get_current_buyer) ,db: AsyncSession = Depends(get_async_db)):
    product = await db.scalars(select(ProductModel).where(ProductModel.id == review.product_id).where(ProductModel.is_active == True))
    if not product.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    new_review = ReviewModel(**review.model_dump(), user_id=current_user.id)
    db.add(new_review)
    await db.flush()
    await update_product_rating(db, review.product_id)
    await db.commit()
    await db.refresh(new_review)

    return new_review

@router.delete("/{review_id}")
async def delete_review_by_id(review_id: int, current_user = Depends(get_current_admin), db: AsyncSession = Depends(get_async_db)):
    result = await db.scalars(
        select(ReviewModel).where(ReviewModel.id == review_id).where(ReviewModel.is_active == True)
    )
    review = result.first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    await db.execute(
        update(ReviewModel).where(ReviewModel.id == review_id).values(is_active=False)
    )
    await db.flush()
    await update_product_rating(db, review.product_id)
    await db.commit()
    await db.refresh(review)
    return {"message": "Review deleted"}



