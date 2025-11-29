from typing import Optional
from fastapi import FastAPI, Path, Query, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: float
    published_date: int
    
    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date

class BookRequest(BaseModel):
    id: Optional[int] = Field(description="The unique identifier of the book", default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=10)
    rating: float = Field(gt=0, lt=5)
    published_date: int = Field(gt=1899, lt=2031)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "description": "A novel set in the Roaring Twenties.",
                "rating": 4.5,
                "published_date": 2020
            }
        }
    }


BOOKS = [
    Book(1, "The Great Gatsby", "F. Scott Fitzgerald", "A novel set in the Roaring Twenties.", 4.5, 1925),
    Book(2, "1984", "George Orwell", "A dystopian novel about totalitarianism.", 4.7, 1949),
    Book(3, "To Kill a Mockingbird", "Harper Lee", "A novel about racial injustice in the Deep South.", 4.8, 1960),
    Book(4, "The Catcher in the Rye", "J.D. Salinger", "A story about teenage rebellion and angst.", 4.0, 1951),
    Book(5, "Pride and Prejudice", "Jane Austen", "A classic romance novel.", 4.6, 1813)
]
         
@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS

@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(..., description="The ID of the book to retrieve", gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")

@app.get("/books/", status_code=status.HTTP_200_OK)
async def find_books_by_rating(rating: float = Query(..., description="The minimum rating of the books to retrieve", gt=0, lt=5)):
    books_return = []
    for book in BOOKS:
        if book.rating >= rating:
            books_return.append(book)
    if books_return:
        return books_return
    raise HTTPException(status_code=404, detail="Book not found")

@app.get("/books/published/", status_code=status.HTTP_200_OK)
async def find_books_by_published_date(published_date: int = Query(..., description="The minimum published date of the books to retrieve", gt=1899, lt=2031)):
    books_return = []
    for book in BOOKS:
        if book.published_date >= published_date:
            books_return.append(book)
    if books_return:
        return books_return
    raise HTTPException(status_code=404, detail="Book not found")

@app.post("/create_book/", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.dict())
    fin_book_id(new_book)
    BOOKS.append(new_book)
    return new_book

def fin_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book

@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            book_changed = True
            BOOKS[i].title = book.title
        if not book_changed:
            raise HTTPException(status_code=404, detail="Book not found")
    return BOOKS[i]

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(..., description="The ID of the book to delete", gt=0)):
    for index, book in enumerate(BOOKS):
        if book.id == book_id:
            deleted_book = BOOKS.pop(index)
            return deleted_book
    raise HTTPException(status_code=404, detail="Book not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)