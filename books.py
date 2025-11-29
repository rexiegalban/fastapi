from fastapi import FastAPI

app = FastAPI()

books = [
    {"id": 1, "title": "The Great Gatsby", "category": "Fiction"},
    {"id": 2, "title": "1984", "category": "Dystopian"},
    {"id": 3, "title": "To Kill a Mockingbird", "category": "Classic"},
    {"id": 4, "title": "The Catcher in the Rye", "category": "Classic"}
]

@app.get("/books")
async def read_books():
    return books

@app.get("/books/{book_id}")
async def read_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    return {"error": "Book not found"}

@app.get("/books/")
async def find_book(category: str):
    books_return = []
    for book in books:
        if book["category"].lower() == category.lower():
            books_return.append(book)
    if books_return:
        return books_return
    return {"error": "Book not found"}

@app.post("/books/")
async def create_book(book: dict):
    books.append(book)
    return book

@app.put("/books/{book_id}")
async def update_book(book_id: int, updated_book: dict):
    for index, book in enumerate(books):
        if book["id"] == book_id:
            books[index] = updated_book
            return updated_book
    return {"error": "Book not found"}

@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
    for index, book in enumerate(books):
        if book["id"] == book_id:
            deleted_book = books.pop(index)
            return deleted_book
    return {"error": "Book not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)