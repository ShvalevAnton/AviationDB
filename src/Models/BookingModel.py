from datetime import datetime


class Booking:
    def __init__(self, book_ref, book_date, total_amount):
        self.book_ref = book_ref
        self.book_date = book_date
        self.total_amount = total_amount

    def __str__(self):
        return f"Booking {self.book_ref}: {self.book_date}, ${self.total_amount}"

    @staticmethod
    def create_table(db):
        """Создание таблицы bookings"""
        try:
            cursor = db.get_cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS bookings.bookings
            (
                book_ref character(6) COLLATE pg_catalog."default" NOT NULL,
                book_date timestamp with time zone NOT NULL,
                total_amount numeric(10,2) NOT NULL,
                CONSTRAINT bookings_pkey PRIMARY KEY (book_ref)
            );
            """
            cursor.execute(create_table_query)
            db.connection.commit()
            print("Таблица bookings создана или уже существует")
        except Exception as e:
            print(f"Ошибка при создании таблицы: {e}")

    @staticmethod
    def create(db, book_ref, book_date, total_amount):
        """Создание новой записи бронирования"""
        try:
            cursor = db.get_cursor()
            insert_query = """
            INSERT INTO bookings.bookings (book_ref, book_date, total_amount)
            VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (book_ref, book_date, total_amount))
            db.connection.commit()
            print(f"Бронирование {book_ref} успешно создано")
            return True
        except Exception as e:
            print(f"Ошибка при создании бронирования: {e}")
            return False

    @staticmethod
    def read_all(db):
        """Чтение всех записей бронирований"""
        try:
            cursor = db.get_cursor()
            cursor.execute("SELECT * FROM bookings.bookings ORDER BY book_date")
            results = cursor.fetchall()

            bookings = []
            for row in results:
                booking = Booking(
                    book_ref=row['book_ref'],
                    book_date=row['book_date'],
                    total_amount=row['total_amount']
                )
                bookings.append(booking)

            return bookings
        except Exception as e:
            print(f"Ошибка при чтении бронирований: {e}")
            return []

    @staticmethod
    def read_by_ref(db, book_ref):
        """Чтение бронирования по номеру"""
        try:
            cursor = db.get_cursor()
            cursor.execute("SELECT * FROM bookings.bookings WHERE book_ref = %s", (book_ref,))
            result = cursor.fetchone()

            if result:
                return Booking(
                    book_ref=result['book_ref'],
                    book_date=result['book_date'],
                    total_amount=result['total_amount']
                )
            return None
        except Exception as e:
            print(f"Ошибка при поиске бронирования: {e}")
            return None

    @staticmethod
    def update(db, book_ref, total_amount=None, book_date=None):
        """Обновление данных бронирования"""
        try:
            cursor = db.get_cursor()
            update_fields = []
            params = []

            if total_amount is not None:
                update_fields.append("total_amount = %s")
                params.append(total_amount)

            if book_date is not None:
                update_fields.append("book_date = %s")
                params.append(book_date)

            if not update_fields:
                print("Нет данных для обновления")
                return False

            params.append(book_ref)
            update_query = f"""
            UPDATE bookings.bookings 
            SET {', '.join(update_fields)} 
            WHERE book_ref = %s
            """

            cursor.execute(update_query, params)
            db.connection.commit()

            if cursor.rowcount > 0:
                print(f"Бронирование {book_ref} успешно обновлено")
                return True
            else:
                print(f"Бронирование {book_ref} не найдено")
                return False
        except Exception as e:
            print(f"Ошибка при обновлении бронирования: {e}")
            return False

    @staticmethod
    def delete(db, book_ref):
        """Удаление бронирования"""
        try:
            cursor = db.get_cursor()
            delete_query = "DELETE FROM bookings.bookings WHERE book_ref = %s"
            cursor.execute(delete_query, (book_ref,))
            db.connection.commit()

            if cursor.rowcount > 0:
                print(f"Бронирование {book_ref} успешно удалено")
                return True
            else:
                print(f"Бронирование {book_ref} не найдено")
                return False
        except Exception as e:
            print(f"Ошибка при удалении бронирования: {e}")
            return False

    @staticmethod
    def read_all_paginated(db, offset, limit):
        """Чтение записей бронирований с пагинацией"""
        try:
            cursor = db.get_cursor()

            # Получаем данные
            cursor.execute("""
                SELECT * FROM bookings.bookings 
                ORDER BY book_date 
                LIMIT %s OFFSET %s
            """, (limit, offset))
            results = cursor.fetchall()

            bookings = []
            for row in results:
                booking = Booking(
                    book_ref=row['book_ref'],
                    book_date=row['book_date'],
                    total_amount=row['total_amount']
                )
                bookings.append(booking)

            # Получаем общее количество
            cursor.execute("SELECT COUNT(*) FROM bookings.bookings")
            total = cursor.fetchone()['count']

            return bookings, total
        except Exception as e:
            print(f"Ошибка при чтении бронирований: {e}")
            return [], 0