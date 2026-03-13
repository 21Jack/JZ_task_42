import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取数据库配置
MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME') or 'root'
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
MYSQL_PORT = os.environ.get('MYSQL_PORT') or '3306'
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'todolist'

try:
    # 连接到MySQL服务器（不指定数据库）
    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USERNAME,
        password=MYSQL_PASSWORD
    )

    if connection.is_connected():
        cursor = connection.cursor()
        
        # 创建数据库（如果不存在）
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"数据库 '{MYSQL_DATABASE}' 已创建或已存在")
        
        # 选择数据库
        cursor.execute(f"USE {MYSQL_DATABASE}")
        print(f"已选择数据库 '{MYSQL_DATABASE}'")

except Error as e:
    print(f"连接MySQL时出错: {e}")
    print("\n解决方法建议:")
    print("1. 确保MySQL服务器已启动 (在终端运行: mysql.server start)")
    print("2. 检查MySQL用户名和密码是否正确")
    print("3. 如果您是第一次使用MySQL，可能需要设置root密码或创建新用户")
    print("4. 或者，您可以手动创建数据库:")
    print(f"   CREATE DATABASE {MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print("\n注意: 数据库连接配置在 todoapp/config.py 中可以修改")

finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL连接已关闭")
