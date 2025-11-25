from datetime import datetime

class Seat:
    def __init__(self, aircraft_code, seat_no, fare_conditions):
        self.aircraft_code = aircraft_code
        self.seat_no = seat_no
        self.fare_conditions = fare_conditions

    def __str__(self):
        return f"Seat {self.seat_no} on {self.aircraft_code}: {self.fare_conditions}"

    @staticmethod
    def create_table(db):
        """Создание таблицы seats"""
        try:
            cursor = db.get_cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS bookings.seats
            (
                aircraft_code character(3) NOT NULL,
                seat_no character varying(4) NOT NULL,
                fare_conditions character varying(10) NOT NULL,
                CONSTRAINT seats_pkey PRIMARY KEY (aircraft_code, seat_no),
                CONSTRAINT seats_aircraft_code_fkey FOREIGN KEY (aircraft_code)
                    REFERENCES bookings.aircrafts (aircraft_code) 
                    ON DELETE CASCADE
            );
            """
            cursor.execute(create_table_query)
            db.connection.commit()
            print("Таблица seats создана или уже существует")
        except Exception as e:
            print(f"Ошибка при создании таблицы seats: {e}")

    @staticmethod
    def create(db, aircraft_code, seat_no, fare_conditions):
        """Создание новой записи места"""
        try:
            cursor = db.get_cursor()
            insert_query = """
            INSERT INTO bookings.seats (aircraft_code, seat_no, fare_conditions)
            VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (aircraft_code, seat_no, fare_conditions))
            db.connection.commit()
            print(f"Место {seat_no} для самолета {aircraft_code} успешно создано")
            return True
        except Exception as e:
            print(f"Ошибка при создании места: {e}")
            return False

    @staticmethod
    def read_all(db):
        """Чтение всех записей мест"""
        try:
            cursor = db.get_cursor()
            cursor.execute("SELECT * FROM bookings.seats ORDER BY aircraft_code, seat_no")
            results = cursor.fetchall()

            seats = []
            for row in results:
                seat = Seat(
                    aircraft_code=row['aircraft_code'],
                    seat_no=row['seat_no'],
                    fare_conditions=row['fare_conditions']
                )
                seats.append(seat)

            return seats
        except Exception as e:
            print(f"Ошибка при чтении мест: {e}")
            return []

    @staticmethod
    def read_by_aircraft(db, aircraft_code):
        """Чтение мест по коду самолета"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT * FROM bookings.seats 
                WHERE aircraft_code = %s 
                ORDER BY seat_no
            """, (aircraft_code,))
            results = cursor.fetchall()

            seats = []
            for row in results:
                seat = Seat(
                    aircraft_code=row['aircraft_code'],
                    seat_no=row['seat_no'],
                    fare_conditions=row['fare_conditions']
                )
                seats.append(seat)

            return seats
        except Exception as e:
            print(f"Ошибка при поиске мест по самолету: {e}")
            return []

    @staticmethod
    def read_by_primary_key(db, aircraft_code, seat_no):
        """Чтение места по первичному ключу"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT * FROM bookings.seats 
                WHERE aircraft_code = %s AND seat_no = %s
            """, (aircraft_code, seat_no))
            result = cursor.fetchone()

            if result:
                return Seat(
                    aircraft_code=result['aircraft_code'],
                    seat_no=result['seat_no'],
                    fare_conditions=result['fare_conditions']
                )
            return None
        except Exception as e:
            print(f"Ошибка при поиске места: {e}")
            return None

    @staticmethod
    def update(db, aircraft_code, seat_no, fare_conditions=None):
        """Обновление данных места"""
        try:
            cursor = db.get_cursor()
            update_fields = []
            params = []

            if fare_conditions is not None:
                update_fields.append("fare_conditions = %s")
                params.append(fare_conditions)

            if not update_fields:
                print("Нет данных для обновления")
                return False

            params.extend([aircraft_code, seat_no])
            update_query = f"""
            UPDATE bookings.seats 
            SET {', '.join(update_fields)} 
            WHERE aircraft_code = %s AND seat_no = %s
            """

            cursor.execute(update_query, params)
            db.connection.commit()

            if cursor.rowcount > 0:
                print(f"Место {seat_no} для самолета {aircraft_code} успешно обновлено")
                return True
            else:
                print(f"Место {seat_no} для самолета {aircraft_code} не найдено")
                return False
        except Exception as e:
            print(f"Ошибка при обновлении места: {e}")
            return False

    @staticmethod
    def delete(db, aircraft_code, seat_no):
        """Удаление места"""
        try:
            cursor = db.get_cursor()
            delete_query = """
            DELETE FROM bookings.seats 
            WHERE aircraft_code = %s AND seat_no = %s
            """
            cursor.execute(delete_query, (aircraft_code, seat_no))
            db.connection.commit()

            if cursor.rowcount > 0:
                print(f"Место {seat_no} для самолета {aircraft_code} успешно удалено")
                return True
            else:
                print(f"Место {seat_no} для самолета {aircraft_code} не найдено")
                return False
        except Exception as e:
            print(f"Ошибка при удалении места: {e}")
            return False

    @staticmethod
    def read_all_paginated(db, offset, limit):
        """Чтение записей мест с пагинацией"""
        try:
            cursor = db.get_cursor()

            # Получаем данные
            cursor.execute("""
                SELECT * FROM bookings.seats 
                ORDER BY aircraft_code, seat_no
                LIMIT %s OFFSET %s
            """, (limit, offset))
            results = cursor.fetchall()

            seats = []
            for row in results:
                seat = Seat(
                    aircraft_code=row['aircraft_code'],
                    seat_no=row['seat_no'],
                    fare_conditions=row['fare_conditions']
                )
                seats.append(seat)

            # Получаем общее количество
            cursor.execute("SELECT COUNT(*) FROM bookings.seats")
            total = cursor.fetchone()['count']

            return seats, total
        except Exception as e:
            print(f"Ошибка при чтении мест: {e}")
            return [], 0