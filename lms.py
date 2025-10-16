import tkinter as tk
from ttkthemes import ThemedTk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector
from datetime import datetime

def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root", 
        password="",  
        database="library_db"
    )

def setup_database():
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS library_db")
    cursor.execute("USE library_db")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        book_id INT PRIMARY KEY,
        book_name VARCHAR(255),
        author_name VARCHAR(255),
        status VARCHAR(50),
        card_id VARCHAR(50)
    )
    """)
    cursor.execute("SHOW COLUMNS FROM books LIKE 'burrowed_date'")
    result = cursor.fetchone()
    if not result:
        cursor.execute("ALTER TABLE books ADD COLUMN burrowed_date DATETIME")
    cursor.close()
    connection.close()

def add_record():
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        book_name = bk_name.get().strip()
        author = author_name.get().strip()
        status = bk_status.get().strip()
        card = card_id.get().strip()

        try:
            book_id = int(bk_id.get())
        except ValueError:
            messagebox.showerror("Error", "Book ID must be an integer!")
            return

        # Basic field checks
        if not book_name or not author or not status:
            messagebox.showerror("Error", "All fields are required!")
            return

        # Handle burrowed_date with time
        if status == "Borrowed":
            if not card:
                messagebox.showerror("Error", "Missing Card ID!")
                return

            try:
                date_only = burrowed_date.get_date()  # gets datetime.date
                current_time = datetime.now().time()  # gets datetime.time
                burrowed_datetime = datetime.combine(date_only, current_time)
            except Exception:
                messagebox.showerror("Error", "Invalid date format for Borrowed Date!")
                return
        else:
            burrowed_datetime = None
            card = None  # Clear card ID if not borrowed

        # Check if book_id already exists
        cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Book ID already exists!")
            return

        # Insert record
        cursor.execute(
            "INSERT INTO books (book_id, book_name, author_name, status, card_id, burrowed_date) VALUES (%s, %s, %s, %s, %s, %s)",
            (book_id, book_name, author, status, card, burrowed_datetime)
        )
        connection.commit()
        cursor.close()
        connection.close()

        messagebox.showinfo("Success", "Record added successfully!")
        clear_fields()
        fetch_records()

    except Exception as e:
        messagebox.showerror("Error", str(e))

def update_record():
    try:
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "No record selected!")
            return

        selected_values = tree.item(selected_item, "values")
        if not selected_values:
            messagebox.showerror("Error", "No record selected!")
            return

        book_id = selected_values[1]
        new_status = bk_status.get().strip()
        new_card_id = card_id.get().strip()
        burrowed_date_input = burrowed_date.get().strip()

        if not new_status:
            messagebox.showerror("Error", "Status cannot be empty!")
            return

        # Validate borrowed status
        if new_status == "Available":
            new_card_id = None
            burrowed_datetime = None
        elif new_status == "Borrowed":
            if not new_card_id:
                messagebox.showerror("Error", "Missing Card ID!")
                return
            if not burrowed_date_input:
                messagebox.showerror("Error", "Missing Borrowed Date!")
                return
            try:
                # Try parsing if it's a string
                burrowed_date_obj = datetime.strptime(burrowed_date_input, "%Y-%m-%d").date()
                current_time = datetime.now().strftime("%I:%M %p")  # e.g., "03:45 PM"
                burrowed_datetime = f"{burrowed_date_input} {current_time}"  # e.g., "2025-05-14 03:45 PM"
            except ValueError:
                messagebox.showerror("Error", "Borrowed Date must be in YYYY-MM-DD format!")
                return
        else:
            burrowed_datetime = None

        # DB update
        connection = connect_to_db()
        cursor = connection.cursor()
        cursor.execute(
    "UPDATE books SET status = %s, card_id = %s, burrowed_date = %s WHERE book_id = %s",
    (new_status, new_card_id, burrowed_datetime, book_id)
)
        connection.commit()
        cursor.close()
        connection.close()

        messagebox.showinfo("Success", "Record updated successfully!")
        fetch_records()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
        
selected_books = {}

def fetch_records():
    try:
        connection = connect_to_db()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM books")
        rows = cursor.fetchall()
        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert("", tk.END, values=("", *row))
        cursor.close()
        connection.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def view_record():
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showerror("Error", "No record selected!")
        return
    
    # Get the current values of the selected item
    selected_values = tree.item(selected_item, "values")
    
    # Check if the checkbox is selected
    if selected_values[0] != "✔":
        messagebox.showerror("Error", "Select a book to view record.")
        return

    record_details = (
        f"Book ID: {selected_values[1]}\n"
        f"Book Name: {selected_values[2]}\n"
        f"Author Name: {selected_values[3]}\n"
        f"Status: {selected_values[4]}\n"
        f"Borrower Card ID: {selected_values[5]}\n"
        f"Borrowed Date: {selected_values[6]}"
    )

    # Create a custom messagebox-style window
    popup = tk.Toplevel(root)
    popup.title("Record Details")
    popup.geometry("360x240")  # About twice the original size
    popup.resizable(False, False)
    popup.transient(root)
    popup.grab_set()

    # Use a frame for nice padding
    frame = tk.Frame(popup, padx=15, pady=15)
    frame.pack(fill="both", expand=True)

    text_label = tk.Label(
        frame,
        text=record_details,
        justify="center",        # Center the lines
        font=("Segoe UI", 11),
        anchor="center"          # Center in the frame
    )
    text_label.pack(side="top", fill="both", expand=True)

    # OK button
    ok_button = tk.Button(popup, text="OK", width=10, command=popup.destroy, font=("Segoe UI", 10, "bold"), bg="SteelBlue")
    ok_button.pack(pady=(0, 10))

    # Center the popup over the main window
    popup.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (popup.winfo_width() // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (popup.winfo_height() // 2)
    popup.geometry(f"+{x}+{y}")

def delete_selected_records():
    try:
        selected_items = tree.get_children()
        to_delete = [tree.item(item, "values")[1] for item in selected_items if tree.item(item, "values")[0] == "✔"]
        if not to_delete:
            messagebox.showerror("Error", "No records selected for deletion!")
            return
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete selected record?")
        if not confirm:
            return
        connection = connect_to_db()
        cursor = connection.cursor()
        cursor.executemany("DELETE FROM books WHERE book_id = %s", [(book_id,) for book_id in to_delete])
        connection.commit()
        cursor.close()
        connection.close()
        messagebox.showinfo("Success", f"Deleted record successfully!")
        fetch_records()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def clear_fields():
    bk_id.set("")
    bk_name.set("")
    author_name.set("")
    bk_status.set("Available")
    card_id.set("")
    burrowed_date.set("")

def search_books():
    query = search_var.get().lower()
    selected_status = status_filter_var.get()  # Get selected status
    
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        # If a status is selected, add a condition to the query
        if selected_status != "All":
            cursor.execute("SELECT * FROM books WHERE status = %s", (selected_status,))
        else:
            cursor.execute("SELECT * FROM books")
        
        rows = cursor.fetchall()
        tree.delete(*tree.get_children())
        found = False
        for row in rows:
            book_id = str(row[0])  # Book ID is at index 0 in the row
            book_name = row[1].lower()  # Book name is at index 1 in the row

            # Check if the query matches either the book ID or book name
            if (selected_status == "All" or row[3].lower() == selected_status.lower()) and (
                query in book_id or query in book_name):
                tree.insert("", tk.END, values=("", *row))
                found = True

        cursor.close()
        connection.close()

        # Only show message when performing a search, not during filtering
        if query and found:
            messagebox.showinfo("Search Result", "Book found!")
        elif query and not found:
            messagebox.showinfo("Search Result", "No book found!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def reset_search():
    search_var.set("")
    fetch_records()

def show_login():
    login_window = tk.Toplevel()
    login_window.title("Login")
    login_window.resizable(False, False)

    # Keep it on top and make it modal
    login_window.grab_set()           # Make it modal
    login_window.transient(root)      # Tie to main window
    login_window.attributes("-topmost", True)  # Stay on top initially

    login_window.update_idletasks()
    width = 300
    height = 230  # Adjusted the height to make space for the button
    x = (login_window.winfo_screenwidth() // 2) - (width // 2)
    y = (login_window.winfo_screenheight() // 2) - (height // 2)
    login_window.geometry(f"{width}x{height}+{x}+{y}")

    tk.Label(login_window, text="Username:", font=("Arial", 11)).pack(pady=8)
    username_entry = tk.Entry(login_window, font=("Arial", 11), width=20)
    username_entry.pack(pady=5)

    tk.Label(login_window, text="Password:", font=("Arial", 11)).pack(pady=8)
    password_entry = tk.Entry(login_window, show='*', font=("Arial", 11), width=20)
    password_entry.pack(pady=5)

    def validate_login():
        username = username_entry.get()
        password = password_entry.get()
        if username == "admin" and password == "admin":
            login_window.destroy()
            root.deiconify()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password", parent=login_window)

    # Login button positioned after the entry fields
    login_button = tk.Button(login_window, text="Login", command=validate_login, font=("Arial", 11, "bold"), width=15, height=2, bg="SteelBlue", fg="white")
    login_button.pack(pady=30)

    # If login window is closed, terminate app
    login_window.protocol("WM_DELETE_WINDOW", root.destroy)

root = ThemedTk(theme="plastik")  # Try other themes like "radiance", "breeze", "equilux", etc.
root.title("Library Management System")
root.geometry("800x600")
root.withdraw()  # Hide main window initially
show_login()
root.title("Library Management System")
root.state('zoomed')

light_blue_bg = "#266CA9"
lf_bg = 'LightSkyBlue'
rtf_bg = 'DeepSkyBlue'
rbf_bg = 'DodgerBlue'
btn_hlb_bg = 'SteelBlue'

tk.Label(root, text="LIBRARY MANAGEMENT SYSTEM", font=("Noto Sans CJK TC", 15, 'bold'), bg=light_blue_bg, fg='White').pack(side=tk.TOP, fill=tk.X)

bk_status = tk.StringVar(value="Available")

def toggle_burrowed_date(*args):
    if bk_status.get() == "Available":
        date_entry.config(state="disabled")
    else:
        date_entry.config(state="normal")

bk_status.trace_add("write", toggle_burrowed_date)

bk_name = tk.StringVar()
bk_id = tk.StringVar()
author_name = tk.StringVar()
card_id = tk.StringVar()
burrowed_date = tk.StringVar()

left_frame = tk.Frame(root, bg=lf_bg)
left_frame.place(x=0, y=30, relwidth=0.3, relheight=0.96)

search_frame = tk.Frame(root, bg=rtf_bg)
search_frame.place(relx=0.3, y=30, relheight=0.1, relwidth=0.7)

search_var = tk.StringVar()

search_inner_frame = tk.Frame(search_frame, bg=rtf_bg)
search_inner_frame.pack(expand=True)

search_entry = tk.Entry(search_inner_frame, textvariable=search_var, font=("Arial", 12), width=50)
search_entry.grid(row=0, column=0, padx=10, pady=15)

search_button = tk.Button(search_inner_frame, text="Search", font=("Arial", 11, "bold"), bg=btn_hlb_bg, fg="White", command=search_books)
search_button.grid(row=0, column=1, padx=10, pady=15)

tk.Button(search_inner_frame, text="Reset", font=("Arial", 11, "bold"), bg=btn_hlb_bg, fg="White", command=reset_search).grid(row=0, column=2, padx=10)

status_filter_var = tk.StringVar(value="All")
status_filter_label = tk.Label(search_inner_frame, text="Status Filter", bg=rtf_bg, fg="White", font=("Arial", 11))
status_filter_label.grid(row=0, column=3, padx=10, pady=15)

status_filter_dropdown = tk.OptionMenu(search_inner_frame, status_filter_var, "All", "Available", "Borrowed")
status_filter_dropdown.grid(row=0, column=4, padx=10, pady=15)


RB_frame = tk.Frame(root, bg=rbf_bg)
RB_frame.place(relx=0.3, rely=0.14, relheight=0.86, relwidth=0.7)

tk.Label(RB_frame, text="BOOK RECORDS", bg=rbf_bg, fg="White", font=("Noto Sans CJK TC", 15, "bold")).pack(side=tk.TOP, fill=tk.X)

tk.Label(left_frame, text="Book ID", bg=lf_bg, font=("Arial", 10, 'bold'), fg="White").pack(pady=10, anchor="center")
tk.Entry(left_frame, textvariable=bk_id, font=("Arial", 10), width=25).pack(pady=5, anchor="center")

tk.Label(left_frame, text="Book Name", bg=lf_bg, font=("Arial", 10, 'bold'), fg="White").pack(pady=10, anchor="center")
tk.Entry(left_frame, textvariable=bk_name, font=("Arial", 10), width=25).pack(pady=5, anchor="center")

tk.Label(left_frame, text="Author Name", bg=lf_bg, font=("Arial", 10, 'bold'), fg="White").pack(pady=10, anchor="center")
tk.Entry(left_frame, textvariable=author_name, font=("Arial", 10), width=25).pack(pady=5, anchor="center")

tk.Label(left_frame, text="Status of the Book", bg=lf_bg, font=("Arial", 10, 'bold'), fg="White").pack(pady=10, anchor="center")
tk.OptionMenu(left_frame, bk_status, "Available", "Borrowed").pack(pady=5, anchor="center")

tk.Label(left_frame, text="Borrower's Card ID", bg=lf_bg, font=("Arial", 10, 'bold'), fg="White").pack(pady=10, anchor="center")
tk.Entry(left_frame, textvariable=card_id, font=("Arial", 10), width=25).pack(pady=5, anchor="center")

tk.Label(left_frame, text="Borrowed Date", bg=lf_bg, font=("Arial", 10, 'bold'), fg="White").pack(pady=10, anchor="center")
date_entry = DateEntry(left_frame, textvariable=burrowed_date, font=("Arial", 10), width=22, date_pattern='yyyy-mm-dd')
date_entry.pack(pady=5, anchor="center")

tk.Button(left_frame, text="Add New Record", font=("Arial", 10), bg=btn_hlb_bg, fg="White", width=25, height=2, command=add_record).pack(pady=10, anchor="center")
tk.Button(left_frame, text="Clear Fields", font=("Arial", 10), bg=btn_hlb_bg, fg="White", width=25, height=2, command=clear_fields).pack(pady=10, anchor="center")
tk.Button(left_frame, text="Update Record", font=("Arial", 10), bg=btn_hlb_bg, fg="White", width=25, height=2, command=update_record).pack(pady=10, anchor="center")
tk.Button(left_frame, text="Delete Book Record", font=("Arial", 10), bg=btn_hlb_bg, fg="White", width=25, height=2, command=delete_selected_records).pack(pady=10, anchor="center")
tk.Button(left_frame, text="View Record", font=("Arial", 10), bg=btn_hlb_bg, fg="White", width=25, height=2, command=view_record).pack(pady=10, anchor="center")

tree = ttk.Treeview(
    RB_frame,
    selectmode=tk.BROWSE,
    columns=("Select", "Book ID", "Book Name", "Author", "Status", "Borrower Card ID", "Borrowed Date"),
)

tree.column("#0", width=0, stretch=tk.NO)
tree.column("Select", width=70, anchor=tk.CENTER)
tree.column("Book ID", width=100, anchor=tk.CENTER)
tree.column("Book Name", width=250, anchor=tk.CENTER)
tree.column("Author", width=180, anchor=tk.CENTER)
tree.column("Status", width=120, anchor=tk.CENTER)
tree.column("Borrower Card ID", width=180, anchor=tk.CENTER)
tree.column("Borrowed Date", width=150, anchor=tk.CENTER)

tree.heading("Select", text="Select")
tree.heading("Book ID", text="Book ID")
tree.heading("Book Name", text="Book Name")
tree.heading("Author", text="Author")
tree.heading("Status", text="Status")
tree.heading("Borrower Card ID", text="Borrower Card ID")
tree.heading("Borrowed Date", text="Borrowed Date")

def toggle_checkbox(event):
    selected_item = tree.identify_row(event.y)
    if not selected_item:
        return
    
    # Get the current state of the selected checkbox
    current_values = tree.item(selected_item, "values")
    current_checkbox_state = current_values[0]
    
    for item in tree.get_children():
        tree.item(item, values=("", *tree.item(item, "values")[1:]))

    # If the checkbox is checked, uncheck it
    if current_checkbox_state == "✔":
        tree.item(selected_item, values=("", *current_values[1:]))
        tree.tag_configure(selected_item, background="")
    # If the checkbox is unchecked, check it
    else:
        tree.item(selected_item, values=("✔", *current_values[1:]))
        tree.tag_configure(selected_item, background="lightblue")  # Highlight color (can be adjusted)

# Bind the click event to the toggle_checkbox function
tree.bind("<Button-1>", toggle_checkbox)

XScrollbar = tk.Scrollbar(tree, orient=tk.HORIZONTAL, command=tree.xview)
YScrollbar = tk.Scrollbar(tree, orient=tk.VERTICAL, command=tree.yview)
tree.configure(xscrollcommand=XScrollbar.set, yscrollcommand=YScrollbar.set)
XScrollbar.pack(side=tk.BOTTOM, fill=tk.X)
YScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.pack(fill=tk.BOTH, expand=True)

setup_database()
fetch_records()

root.mainloop()