import sqlite3
from flask import Flask

app = Flask(__name__)

@app.route('/update-user/<email>')
def update_user(email):
    # Connect to your SQLite database
    conn = sqlite3.connect('site.db')  # Ensure the path is correct based on your app structure
    cursor = conn.cursor()

    # Update the user record
    cursor.execute("UPDATE user SET is_verified = 1 WHERE email = ?", (email,))
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    return f"User {email} updated successfully."

if __name__ == '__main__':
    app.run()
