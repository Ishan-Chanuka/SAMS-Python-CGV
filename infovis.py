def fetch_attendance(student_id):
    conn = pyodbc.connect(
        r'Driver={ODBC Driver 17 for SQL Server};'
        r'Server=ISHAN\SQLEXPRESS;'
        r'Database=AttendanceDb;'
        r'UID=ick;'
        r'PWD=Ishan,1998'
    )

    c = conn.cursor()
    c.execute("SELECT Status, COUNT(*) FROM attendance WHERE ID = ? GROUP BY Status", (student_id,))
    data = c.fetchall()
    conn.close()
    return data