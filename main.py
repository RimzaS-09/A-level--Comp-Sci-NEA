import sqlite3

if __name__ == "__main__":
    print("Hello world!\n")
    
    
    connection = sqlite3.connect("OS_Open_Zoomstack.mbtiles")
    cursor = connection.cursor()
    output = cursor.execute("SELECT * FROM metadata WHERE 1 = 2;")
    
    print(output.fetchall())