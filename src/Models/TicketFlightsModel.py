class TicketFlight:
    def __init__(self, ticket_no, flight_id, fare_conditions, amount):
        self.ticket_no = ticket_no
        self.flight_id = flight_id
        self.fare_conditions = fare_conditions
        self.amount = amount

    def __str__(self):
        return f"Ticket {self.ticket_no}, Flight {self.flight_id}: {self.fare_conditions} - ${self.amount}"

    @staticmethod
    def create_table(db):
        """Создание таблицы ticket_flights"""
        try:
            cursor = db.get_cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS bookings.ticket_flights
            (
                ticket_no character(13) COLLATE pg_catalog."default" NOT NULL,
                flight_id integer NOT NULL,
                fare_conditions character varying(10) COLLATE pg_catalog."default" NOT NULL,
                amount numeric(10,2) NOT NULL,
                CONSTRAINT ticket_flights_pkey PRIMARY KEY (ticket_no, flight_id),
                CONSTRAINT ticket_flights_amount_check CHECK (amount >= 0::numeric),
                CONSTRAINT ticket_flights_fare_conditions_check CHECK (fare_conditions::text = ANY (
                    ARRAY['Economy'::character varying::text, 'Comfort'::character varying::text, 'Business'::character varying::text]
                ))
            );
            """
            cursor.execute(create_table_query)
            db.connection.commit()
            print("Таблица ticket_flights создана или уже существует")
        except Exception as e:
            print(f"Ошибка при создании таблицы ticket_flights: {e}")

    @staticmethod
    def create(db, ticket_no, flight_id, fare_conditions, amount):
        """Создание новой записи билета на рейс"""
        try:
            valid_fare_conditions = ['Economy', 'Comfort', 'Business']
            if fare_conditions not in valid_fare_conditions:
                print(f"Ошибка: неверный класс обслуживания. Допустимые значения: {', '.join(valid_fare_conditions)}")
                return False

            if amount < 0:
                print("Ошибка: сумма не может быть отрицательной")
                return False

            cursor = db.get_cursor()
            insert_query = """
            INSERT INTO bookings.ticket_flights (ticket_no, flight_id, fare_conditions, amount)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (ticket_no, flight_id, fare_conditions, amount))
            db.connection.commit()
            print(f"Билет {ticket_no} на рейс {flight_id} успешно создан")
            return True
        except Exception as e:
            print(f"Ошибка при создании билета на рейс: {e}")
            return False

    @staticmethod
    def read_all(db):
        """Чтение всех записей билетов на рейсы"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT * FROM bookings.ticket_flights 
                ORDER BY flight_id, ticket_no
            """)
            results = cursor.fetchall()

            ticket_flights = []
            for row in results:
                ticket_flight = TicketFlight(
                    ticket_no=row['ticket_no'],
                    flight_id=row['flight_id'],
                    fare_conditions=row['fare_conditions'],
                    amount=row['amount']
                )
                ticket_flights.append(ticket_flight)

            return ticket_flights
        except Exception as e:
            print(f"Ошибка при чтении билетов на рейсы: {e}")
            return []

    @staticmethod
    def read_by_ticket_and_flight(db, ticket_no, flight_id):
        """Чтение билета на рейс по номеру билета и рейсу"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT * FROM bookings.ticket_flights 
                WHERE ticket_no = %s AND flight_id = %s
            """, (ticket_no, flight_id))
            result = cursor.fetchone()

            if result:
                return TicketFlight(
                    ticket_no=result['ticket_no'],
                    flight_id=result['flight_id'],
                    fare_conditions=result['fare_conditions'],
                    amount=result['amount']
                )
            return None
        except Exception as e:
            print(f"Ошибка при поиске билета на рейс: {e}")
            return None

    @staticmethod
    def read_by_ticket(db, ticket_no):
        """Чтение всех рейсов для билета"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT * FROM bookings.ticket_flights 
                WHERE ticket_no = %s 
                ORDER BY flight_id
            """, (ticket_no,))
            results = cursor.fetchall()

            ticket_flights = []
            for row in results:
                ticket_flight = TicketFlight(
                    ticket_no=row['ticket_no'],
                    flight_id=row['flight_id'],
                    fare_conditions=row['fare_conditions'],
                    amount=row['amount']
                )
                ticket_flights.append(ticket_flight)

            return ticket_flights
        except Exception as e:
            print(f"Ошибка при поиске рейсов для билета: {e}")
            return []

    @staticmethod
    def read_by_flight(db, flight_id):
        """Чтение всех билетов на рейс"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT * FROM bookings.ticket_flights 
                WHERE flight_id = %s 
                ORDER BY ticket_no
            """, (flight_id,))
            results = cursor.fetchall()

            ticket_flights = []
            for row in results:
                ticket_flight = TicketFlight(
                    ticket_no=row['ticket_no'],
                    flight_id=row['flight_id'],
                    fare_conditions=row['fare_conditions'],
                    amount=row['amount']
                )
                ticket_flights.append(ticket_flight)

            return ticket_flights
        except Exception as e:
            print(f"Ошибка при поиске билетов на рейс: {e}")
            return []

    @staticmethod
    def read_by_fare_conditions(db, fare_conditions):
        """Чтение билетов по классу обслуживания"""
        try:
            valid_fare_conditions = ['Economy', 'Comfort', 'Business']
            if fare_conditions not in valid_fare_conditions:
                print(f"Ошибка: неверный класс обслуживания. Допустимые значения: {', '.join(valid_fare_conditions)}")
                return []

            cursor = db.get_cursor()
            cursor.execute("""
                SELECT * FROM bookings.ticket_flights 
                WHERE fare_conditions = %s 
                ORDER BY flight_id, ticket_no
            """, (fare_conditions,))
            results = cursor.fetchall()

            ticket_flights = []
            for row in results:
                ticket_flight = TicketFlight(
                    ticket_no=row['ticket_no'],
                    flight_id=row['flight_id'],
                    fare_conditions=row['fare_conditions'],
                    amount=row['amount']
                )
                ticket_flights.append(ticket_flight)

            return ticket_flights
        except Exception as e:
            print(f"Ошибка при поиске билетов по классу обслуживания: {e}")
            return []

    @staticmethod
    def update_fare_conditions(db, ticket_no, flight_id, fare_conditions):
        """Обновление класса обслуживания"""
        try:
            valid_fare_conditions = ['Economy', 'Comfort', 'Business']
            if fare_conditions not in valid_fare_conditions:
                print(f"Ошибка: неверный класс обслуживания. Допустимые значения: {', '.join(valid_fare_conditions)}")
                return False

            cursor = db.get_cursor()
            update_query = """
            UPDATE bookings.ticket_flights 
            SET fare_conditions = %s 
            WHERE ticket_no = %s AND flight_id = %s
            """

            cursor.execute(update_query, (fare_conditions, ticket_no, flight_id))
            db.connection.commit()

            if cursor.rowcount > 0:
                print(f"Класс обслуживания для билета {ticket_no} на рейс {flight_id} обновлен: {fare_conditions}")
                return True
            else:
                print("Билет на рейс не найден")
                return False
        except Exception as e:
            print(f"Ошибка при обновлении класса обслуживания: {e}")
            return False

    @staticmethod
    def update_amount(db, ticket_no, flight_id, amount):
        """Обновление стоимости"""
        try:
            if amount < 0:
                print("Ошибка: сумма не может быть отрицательной")
                return False

            cursor = db.get_cursor()
            update_query = """
            UPDATE bookings.ticket_flights 
            SET amount = %s 
            WHERE ticket_no = %s AND flight_id = %s
            """

            cursor.execute(update_query, (amount, ticket_no, flight_id))
            db.connection.commit()

            if cursor.rowcount > 0:
                print(f"Стоимость для билета {ticket_no} на рейс {flight_id} обновлена: ${amount}")
                return True
            else:
                print("Билет на рейс не найден")
                return False
        except Exception as e:
            print(f"Ошибка при обновлении стоимости: {e}")
            return False

    @staticmethod
    def delete(db, ticket_no, flight_id):
        """Удаление билета на рейс"""
        try:
            cursor = db.get_cursor()
            delete_query = """
            DELETE FROM bookings.ticket_flights 
            WHERE ticket_no = %s AND flight_id = %s
            """
            cursor.execute(delete_query, (ticket_no, flight_id))
            db.connection.commit()

            if cursor.rowcount > 0:
                print(f"Билет {ticket_no} на рейс {flight_id} успешно удален")
                return True
            else:
                print("Билет на рейс не найден")
                return False
        except Exception as e:
            print(f"Ошибка при удалении билета на рейс: {e}")
            return False

    @staticmethod
    def get_flight_statistics(db, flight_id):
        """Получение статистики по рейсу"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT 
                    fare_conditions,
                    COUNT(*) as ticket_count,
                    SUM(amount) as total_amount,
                    AVG(amount) as avg_amount,
                    MIN(amount) as min_amount,
                    MAX(amount) as max_amount
                FROM bookings.ticket_flights 
                WHERE flight_id = %s 
                GROUP BY fare_conditions
                ORDER BY 
                    CASE 
                        WHEN fare_conditions = 'Business' THEN 1
                        WHEN fare_conditions = 'Comfort' THEN 2
                        WHEN fare_conditions = 'Economy' THEN 3
                    END
            """, (flight_id,))
            results = cursor.fetchall()

            return results
        except Exception as e:
            print(f"Ошибка при получении статистики по рейсу: {e}")
            return []

    @staticmethod
    def get_ticket_statistics(db, ticket_no):
        """Получение статистики по билету"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as flight_count,
                    SUM(amount) as total_amount,
                    AVG(amount) as avg_amount
                FROM bookings.ticket_flights 
                WHERE ticket_no = %s
            """, (ticket_no,))
            result = cursor.fetchone()

            return result
        except Exception as e:
            print(f"Ошибка при получении статистики по билету: {e}")
            return None

    @staticmethod
    def get_available_fare_conditions():
        """Получение списка доступных классов обслуживания"""
        return ['Economy', 'Comfort', 'Business']

    @staticmethod
    def read_all_paginated(db, offset, limit):
        """Чтение записей билетов на рейсы с пагинацией"""
        try:
            cursor = db.get_cursor()

            # Получаем данные
            cursor.execute("""
                SELECT * FROM bookings.ticket_flights 
                ORDER BY flight_id, ticket_no
                LIMIT %s OFFSET %s
            """, (limit, offset))
            results = cursor.fetchall()

            ticket_flights = []
            for row in results:
                ticket_flight = TicketFlight(
                    ticket_no=row['ticket_no'],
                    flight_id=row['flight_id'],
                    fare_conditions=row['fare_conditions'],
                    amount=row['amount']
                )
                ticket_flights.append(ticket_flight)

            # Получаем общее количество
            cursor.execute("SELECT COUNT(*) FROM bookings.ticket_flights")
            total = cursor.fetchone()['count']

            return ticket_flights, total
        except Exception as e:
            print(f"Ошибка при чтении билетов на рейсы: {e}")
            return [], 0