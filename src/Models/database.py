import psycopg2
from psycopg2.extras import RealDictCursor


class PostgreSQLDatabase:
    def __init__(self, database, user, password, host, port):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None

    def connect(self):
        """Установка соединения с базой данных"""
        try:
            self.connection = psycopg2.connect(
                database=self.database,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.connection.autocommit = True
            print("Успешное подключение к базе данных")
            return self.connection
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return None

    def disconnect(self):
        """Закрытие соединения с базой данных"""
        if self.connection:
            self.connection.close()
            print("Соединение с базой данных закрыто")

    def get_cursor(self):
        """Получение курсора для выполнения запросов"""
        if self.connection:
            return self.connection.cursor(cursor_factory=RealDictCursor)
        return None