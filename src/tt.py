import cx_Oracle

# Oracle DB 연결 정보
username = "nxkis"
password = "nxkis"
dsn = cx_Oracle.makedsn("host", 1521, service_name="nxkis")  # Replace "host" and "your_service_name"

try:
    # 데이터베이스에 연결
    connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
    print("Successfully connected to Oracle Database")

    # 커서 생성
    cursor = connection.cursor()

    # SQL 쿼리 실행
    cursor.execute("SELECT * FROM your_table_name WHERE ROWNUM <= 10")
    rows = cursor.fetchall()

    # 결과 출력
    for row in rows:
        print(row)

except cx_Oracle.DatabaseError as e:
    print(f"Database error: {e}")

finally:
    # 연결 종료
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()
