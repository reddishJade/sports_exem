import mysql.connector
from mysql.connector import Error

def create_database():
    try:
        # 连接MySQL（不指定数据库）
        connection = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="123456"  # 更新为正确的密码
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # 创建数据库
            cursor.execute("CREATE DATABASE IF NOT EXISTS fitness_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("数据库 'fitness_db' 创建成功！")
            
    except Error as e:
        print(f"连接MySQL时出错: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL连接已关闭")

if __name__ == "__main__":
    create_database()
