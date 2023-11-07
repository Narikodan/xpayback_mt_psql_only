# User Registration with PostgreSQL and FastAPI

This is a sample FastAPI application that allows users to register with the system. User information is stored in a PostgreSQL database, with separate tables for user details and profile pictures.

## Features

- User registration with Full Name, Email, Password, Phone, and Profile Picture.
- Validation for duplicate Email and Phone during registration.
- GET method to retrieve registered user details.

## Database Setup

1. Install PostgreSQL: If you haven't already, you need to install PostgreSQL on your system. You can download it from the official website: [PostgreSQL Downloads](https://www.postgresql.org/download/).

2. Create a PostgreSQL Database:
   - Create a new PostgreSQL database using your preferred method, for example, you can use the command line or a GUI tool like pgAdmin.

3. Set up the Database URL:
   - Update the `DATABASE_URL` in the FastAPI application (`main.py`) with your PostgreSQL database URL. It should be in the format:
     ```
     postgresql://<username>:<password>@<host>/<database>
     ```

4. Create Tables:
   - Run the FastAPI application to create the required tables in your PostgreSQL database. Use the following command:
     ```
     uvicorn main:app --reload
     ```

## Usage

1. Register a User:
   - To register a new user, make a POST request to `/register/` with the following details:
     - Full Name
     - Email
     - Password
     - Phone
     - Profile Picture (Upload a file)
   - Example:
     ```
     curl -X POST "http://localhost:8000/register/" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "full_name=John Doe" -F "email=johndoe@example.com" -F "password=securepassword" -F "phone=1234567890" -F "profile_picture=@path/to/profile.jpg"
     ```

2. Retrieve User Details:
   - To retrieve user details, make a GET request to `/user/{user_id}` where `user_id` is the unique ID of the registered user.
   - Example:
     ```
     curl -X GET "http://localhost:8000/user/{user_id}" -H "accept: application/json"
     ```


