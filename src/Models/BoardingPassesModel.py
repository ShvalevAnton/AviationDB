class BoardingPass:
    def __init__(self, ticket_no, flight_id, boarding_no, seat_no):
        self.ticket_no = ticket_no
        self.flight_id = flight_id
        self.boarding_no = boarding_no
        self.seat_no = seat_no

    def __str__(self):
        return f"Boarding Pass: Ticket {self.ticket_no}, Flight {self.flight_id}, Boarding #{self.boarding_no}, Seat {self.seat_no}"

    @staticmethod
    def create_table(db):
        """Создание таблицы boarding_passes"""
        try:
            cursor = db.get_cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS bookings.boarding_passes
            (
                ticket_no character(13) COLLATE pg_catalog."default" NOT NULL,
                flight_id integer NOT NULL,
                boarding_no integer NOT NULL,
                seat_no character varying(4) COLLATE pg_catalog."default" NOT NULL,
                CONSTRAINT boarding_passes_pkey PRIMARY KEY (ticket_no, flight_id),
                CONSTRAINT boarding_passes_flight_id_boarding_no_key UNIQUE (flight_id, boarding_no),
                CONSTRAINT boarding_passes_flight_id_seat_no_key UNIQUE (flight_id, seat_no)
            );
            """
            cursor.execute(create_table_query)
            db.connection.commit()
            print("Таблица boarding_passes создана или уже существует")
        except Exception as e:
            print(f"Ошибка при создании таблицы boarding_passes: {e}")

    @staticmethod
    def create(db, ticket_no, flight_id, boarding_no, seat_no):
        """Создание новой записи посадочного талона"""
        try:
            cursor = db.get_cursor()
            insert_query = """
            INSERT INTO bookings.boarding_passes (ticket_no, flight_id, boarding_no, seat_no)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (ticket_no, flight_id, boarding_no, seat_no))
            db.connection.commit()
            print(f"Посадочный талон для билета {ticket_no} рейса {flight_id} успешно создан")
            return True
        except Exception as e:
            print(f"Ошибка при создании посадочного талона: {e}")
            return False

    @staticmethod
    def read_all(db):
        """Чтение всех записей посадочных талонов"""
        try:
            cursor = db.get_cursor()
            cursor.execute("SELECT * FROM bookings.boarding_passes ORDER BY flight_id, boarding_no")
            results = cursor.fetchall()

            boarding_passes = []
            for row in results:
                boarding_pass = BoardingPass(
                    ticket_no=row['ticket_no'],
                    flight_id=row['flight_id'],
                    boarding_no=row['boarding_no'],
                    seat_no=row['seat_no']
                )
                boarding_passes.append(boarding_pass)

            return boarding_passes
        except Exception as e:
            print(f"Ошибка при чтении посадочных талонов: {e}")
            return []

    @staticmethod
    def read_by_ticket_and_flight(db, ticket_no, flight_id):
        """Чтение посадочного талона по номеру билета и рейсу"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT * FROM bookings.boarding_passes 
                WHERE ticket_no = %s AND flight_id = %s
            """, (ticket_no, flight_id))
            result = cursor.fetchone()

            if result:
                return BoardingPass(
                    ticket_no=result['ticket_no'],
                    flight_id=result['flight_id'],
                    boarding_no=result['boarding_no'],
                    seat_no=result['seat_no']
                )
            return None
        except Exception as e:
            print(f"Ошибка при поиске посадочного талона: {e}")
            return None

    @staticmethod
    def read_by_flight(db, flight_id):
        """Чтение всех посадочных талонов для рейса"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT * FROM bookings.boarding_passes 
                WHERE flight_id = %s 
                ORDER BY boarding_no
            """, (flight_id,))
            results = cursor.fetchall()

            boarding_passes = []
            for row in results:
                boarding_pass = BoardingPass(
                    ticket_no=row['ticket_no'],
                    flight_id=row['flight_id'],
                    boarding_no=row['boarding_no'],
                    seat_no=row['seat_no']
                )
                boarding_passes.append(boarding_pass)

            return boarding_passes
        except Exception as e:
            print(f"Ошибка при поиске посадочных талонов для рейса: {e}")
            return []

    @staticmethod
    def read_by_boarding_no(db, flight_id, boarding_no):
        """Чтение посадочного талона по номеру посадки"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT * FROM bookings.boarding_passes 
                WHERE flight_id = %s AND boarding_no = %s
            """, (flight_id, boarding_no))
            result = cursor.fetchone()

            if result:
                return BoardingPass(
                    ticket_no=result['ticket_no'],
                    flight_id=result['flight_id'],
                    boarding_no=result['boarding_no'],
                    seat_no=result['seat_no']
                )
            return None
        except Exception as e:
            print(f"Ошибка при поиске посадочного талона по номеру посадки: {e}")
            return None

    @staticmethod
    def update_seat(db, ticket_no, flight_id, seat_no):
        """Обновление места в посадочном талоне"""
        try:
            cursor = db.get_cursor()
            update_query = """
            UPDATE bookings.boarding_passes 
            SET seat_no = %s 
            WHERE ticket_no = %s AND flight_id = %s
            """

            cursor.execute(update_query, (seat_no, ticket_no, flight_id))
            db.connection.commit()

            if cursor.rowcount > 0:
                print(f"Место в посадочном талоне обновлено: {seat_no}")
                return True
            else:
                print("Посадочный талон не найден")
                return False
        except Exception as e:
            print(f"Ошибка при обновлении места: {e}")
            return False

    @staticmethod
    def update_boarding_no(db, ticket_no, flight_id, boarding_no):
        """Обновление номера посадки"""
        try:
            cursor = db.get_cursor()
            update_query = """
            UPDATE bookings.boarding_passes 
            SET boarding_no = %s 
            WHERE ticket_no = %s AND flight_id = %s
            """

            cursor.execute(update_query, (boarding_no, ticket_no, flight_id))
            db.connection.commit()

            if cursor.rowcount > 0:
                print(f"Номер посадки обновлен: {boarding_no}")
                return True
            else:
                print("Посадочный талон не найден")
                return False
        except Exception as e:
            print(f"Ошибка при обновлении номера посадки: {e}")
            return False

    @staticmethod
    def delete(db, ticket_no, flight_id):
        """Удаление посадочного талона"""
        try:
            cursor = db.get_cursor()
            delete_query = """
            DELETE FROM bookings.boarding_passes 
            WHERE ticket_no = %s AND flight_id = %s
            """
            cursor.execute(delete_query, (ticket_no, flight_id))
            db.connection.commit()

            if cursor.rowcount > 0:
                print(f"Посадочный талон для билета {ticket_no} рейса {flight_id} успешно удален")
                return True
            else:
                print("Посадочный талон не найден")
                return False
        except Exception as e:
            print(f"Ошибка при удалении посадочного талона: {e}")
            return False

    @staticmethod
    def get_available_seats(db, flight_id):
        """Получение списка занятых мест для рейса"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT seat_no FROM bookings.boarding_passes 
                WHERE flight_id = %s 
                ORDER BY seat_no
            """, (flight_id,))
            results = cursor.fetchall()

            occupied_seats = [row['seat_no'] for row in results]
            return occupied_seats
        except Exception as e:
            print(f"Ошибка при получении списка занятых мест: {e}")
            return []

    @staticmethod
    def get_next_boarding_no(db, flight_id):
        """Получение следующего номера посадки для рейса"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT COALESCE(MAX(boarding_no), 0) + 1 as next_boarding_no
                FROM bookings.boarding_passes 
                WHERE flight_id = %s
            """, (flight_id,))
            result = cursor.fetchone()

            return result['next_boarding_no'] if result else 1
        except Exception as e:
            print(f"Ошибка при получении следующего номера посадки: {e}")
            return 1

    @staticmethod
    def read_all_paginated(db, offset, limit):
        """Чтение записей посадочных талонов с пагинацией"""
        try:
            cursor = db.get_cursor()

            # Получаем данные
            cursor.execute("""
                    SELECT * FROM bookings.boarding_passes 
                    ORDER BY flight_id, boarding_no 
                    LIMIT %s OFFSET %s
                """, (limit, offset))
            results = cursor.fetchall()

            boarding_passes = []
            for row in results:
                boarding_pass = BoardingPass(
                    ticket_no=row['ticket_no'],
                    flight_id=row['flight_id'],
                    boarding_no=row['boarding_no'],
                    seat_no=row['seat_no']
                )
                boarding_passes.append(boarding_pass)

            # Получаем общее количество
            cursor.execute("SELECT COUNT(*) FROM bookings.boarding_passes")
            total = cursor.fetchone()['count']

            return boarding_passes, total
        except Exception as e:
            print(f"Ошибка при чтении посадочных талонов: {e}")
            return [], 0