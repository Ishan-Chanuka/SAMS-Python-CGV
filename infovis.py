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

def visualize(data, student_id):
    statuses = [x[0] for x in data]
    counts = [x[1] for x in data]
    plt.bar(statuses, counts)
    plt.title(f'Attendance Summary for {student_id}')
    plt.xlabel('Status')
    plt.ylabel('Count')
    plt.show()

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python infovis.py <student_id>")
        sys.exit(1)

    student_id = sys.argv[1]
    data = fetch_attendance(student_id)
    visualize(data, student_id)