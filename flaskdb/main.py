import sqlite3
from flask import Flask, render_template

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

def get_database_connection():
    database_path = r"C:\Users\abhis\Desktop\AttandenceProject\attendence.db"
    return sqlite3.connect(database_path)

@app.route("/")
def display_attendance():
    try:
        con = get_database_connection()
        cursor = con.cursor()
        cursor.execute('''SELECT * FROM attendence''')
        attendance_data = cursor.fetchall()
        return render_template("attendance.html", attendance_data=attendance_data)
    except Exception as e:
        return str(e)
    finally:
        con.close()

if __name__ == "__main__":
    app.run(debug=True)