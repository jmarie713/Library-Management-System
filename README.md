📚 Library Management System

A simple Library Management System built using Python, Tkinter, and XAMPP MySQL.
This project provides a graphical interface to manage books, students, and borrowing records.

🛠️ Tech Stack
Python
Tkinter (GUI)
MySQL (XAMPP)
VS Code

📦 Installation & Setup Guide
1️⃣ Install Requirements
#Install Python
Download Python from: https://www.python.org/downloads/
Be sure to check "Add Python to PATH" during installation.

#Install XAMPP (for MySQL Database)
Download XAMPP: https://www.apachefriends.org/index.html

#Install Required Python Libraries
Open a terminal in your project folder and run:
pip install mysql-connector-python

🗃️ 2️⃣ Setting Up XAMPP MySQL
#Step 1: Start XAMPP Services
Open the XAMPP Control Panel
Start:
Apache
MySQL

#Step 2: Open phpMyAdmin
Navigate to:
http://localhost/phpmyadmin

#Step 3: Create Database
Click New
Enter database name (example):
library_db
Click Create

#Step 4: Create Required Tables
Example minimal tables (you can adjust based on your project):

books table
CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    author VARCHAR(255),
    year INT,
    isbn VARCHAR(100)
);

students table
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    course VARCHAR(100),
    year_level VARCHAR(50)
);

issued_books table
CREATE TABLE issued_books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    book_id INT,
    issue_date DATE,
    return_date DATE,
    FOREIGN KEY(student_id) REFERENCES students(id),
    FOREIGN KEY(book_id) REFERENCES books(id)
);

🖥️ 3️⃣ Setting Up Python in VS Code
#Step 1: Install VS Code
Download: https://code.visualstudio.com/

#Step 2: Install Python Extension
Open VS Code
Go to Extensions (Ctrl+Shift+X)
Search: Python
Install the official Microsoft Python extension

Step 3: Select Python Interpreter
Press:
Ctrl + Shift + P → "Python: Select Interpreter"
Choose the one installed on your system (e.g., Python 3.x).

#Step 4: Run Your Program
From VS Code terminal:
python main.py

⚙️ 4️⃣ Configure Database Connection in Python
Your Python script should include something like:

import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",     # default XAMPP MySQL has no password
    database="library_db"
)

cursor = db.cursor()

▶️ Running the Program
Ensure XAMPP MySQL is running
Open VS Code
Run
python main.py

The Tkinter window should open.
