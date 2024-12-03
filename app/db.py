import mysql.connector
from mysql.connector import Error


def create_connection():
    """Create a connection to the MySQL database."""
    connection = None
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST, user="root", password=MYSQL_ROOT_PASSWORD
        )
        if connection.is_connected():
            print("Successfully connected to MySQL DB")
    except Error as e:
        print(f"Error: {e}")
    return connection


def delete_database(connection):
    """Delete the specified database if it exists."""
    cursor = connection.cursor()
    try:
        cursor.execute(f"DROP DATABASE IF EXISTS {MYSQL_DATABASE}")
        print(
            f"Database '{MYSQL_DATABASE}' has been deleted successfully (if it existed)."
        )
    except Error as e:
        print(f"Error: {e}")


def create_database(connection):
    """Create a new database."""
    cursor = connection.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}")
        print(f"Database '{MYSQL_DATABASE}' has been created successfully.")
    except Error as e:
        print(f"Error: {e}")


def create_tables(connection):
    """Create tables in the database."""
    cursor = connection.cursor()
    create_agent_table = """
    CREATE TABLE IF NOT EXISTS characters (
        id INT AUTO_INCREMENT PRIMARY KEY,
        short_name VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        background_image TEXT,
        profile_image TEXT,
        original_price FLOAT,
        new_price FLOAT,
        percentage_discount FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );
    """
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL UNIQUE,
        email VARCHAR(255) NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );
    """

    create_history_logs_table = """
    CREATE TABLE IF NOT EXISTS history_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        agent_id INT,
        question TEXT NOT NULL,
        prompt TEXT NOT NULL,
        answer TEXT NOT NULL,
        feedback ENUM('like', 'dislike') DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
    );
    """

    try:
        cursor.execute(create_agent_table)
        cursor.execute(create_users_table)
        cursor.execute(create_history_logs_table)
        print("Tables have been created successfully.")
    except Error as e:
        print(f"Error: {e}")
