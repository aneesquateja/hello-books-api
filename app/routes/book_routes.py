from flask import Blueprint, abort, make_response, request, Response
from app.models.book import Book
from .route_utilities import validate_model
from ..db import db

bp = Blueprint("books_bp", __name__, url_prefix="/books")

@bp.post("")
def create_book():
    request_body = request.get_json()

    try:
        new_book = Book.from_dict(request_body)

    except KeyError as error:
        response = {"message": f"Invalid request: missing {error.args[0]}"}
        abort(make_response(response, 400))

    db.session.add(new_book)
    db.session.commit()

    return new_book.to_dict(), 201

@bp.get("")
def get_all_books():
    # create a basic select query without any filtering
    query = db.select(Book)

    # If we have a `title` query parameter, we can add on to the query object
    title_param = request.args.get("title")
    if title_param:
        # Match the title_param exactly, including capitalization
        # query = query.where(Book.title == title_param)

        # If we want to allow partial matches, we can use the % wildcard with `like()`
        # If `title_param` contains "Great", the code below will match 
        # both "The Great Gatsby" and "Great Expectations"
        # query = query.where(Book.title.like(f"%{title_param}%"))

        # If we want to allow searching case-insensitively, 
        # we can use ilike instead of like
        query = query.where(Book.title.ilike(f"%{title_param}%"))

    # If we have other query parameters, we can continue adding to the query. 
    # As we did above, we must reassign the `query`` variable to capture the new clause we are adding. 
    # If we don't reassign `query``, we are calling the `where` function but are not saving the resulting filter
    description_param = request.args.get("description")
    if description_param:
        # In case there are books with similar titles, we can also filter by description
        query = query.where(Book.description.ilike(f"%{description_param}%"))

    books = db.session.scalars(query.order_by(Book.id))
    # We could also write the line above as:
    # books = db.session.execute(query).scalars()

    books_response = []
    for book in books:
        books_response.append(book.to_dict())
    return books_response

@bp.get("/<book_id>")
def get_one_book(book_id):
    book = validate_model(Book, book_id)

    return book.to_dict()

@bp.put("/<book_id>")
def update_book(book_id):
    book = validate_model(Book, book_id)
    request_body = request.get_json()

    book.title = request_body["title"]
    book.description = request_body["description"]
    db.session.commit()

    return Response(status=204, mimetype="application/json") # 204 No Content

@bp.delete("/<book_id>")
def delete_book(book_id):
    book = validate_model(Book, book_id)
    db.session.delete(book)
    db.session.commit()

    return Response(status=204, mimetype="application/json")
