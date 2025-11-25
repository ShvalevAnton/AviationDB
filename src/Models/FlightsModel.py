from datetime import datetime


class Flight:
    def __init__(self, flight_id, flight_no, scheduled_departure, scheduled_arrival,
                 departure_airport, arrival_airport, status, aircraft_code,
                 actual_departure=None, actual_arrival=None):
        self.flight_id = flight_id
        self.flight_no = flight_no
        self.scheduled_departure = scheduled_departure
        self.scheduled_arrival = scheduled_arrival
        self.departure_airport = departure_airport
        self.arrival_airport = arrival_airport
        self.status = status
        self.aircraft_code = aircraft_code
        self.actual_departure = actual_departure
        self.actual_arrival = actual_arrival

    def __str__(self):
        return (f"Flight {self.flight_no} (ID: {self.flight_id}): {self.departure_airport} -> {self.arrival_airport}, "
                f"Status: {self.status}, Aircraft: {self.aircraft_code}")

    @staticmethod
    def create_table(db):
        """Создание таблицы flights"""
        try:
            cursor = db.get_cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS bookings.flights
            (
                flight_id integer NOT NULL DEFAULT nextval('flights_flight_id_seq'::regclass),
                flight_no character(6) COLLATE pg_catalog."default" NOT NULL,
                scheduled_departure timestamp with time zone NOT NULL,
                scheduled_arrival timestamp with time zone NOT NULL,
                departure_airport character(3) COLLATE pg_catalog."default" NOT NULL,
                arrival_airport character(3) COLLATE pg_catalog."default" NOT NULL,
                status character varying(20) COLLATE pg_catalog."default" NOT NULL,
                aircraft_code character(3) COLLATE pg_catalog."default" NOT NULL,
                actual_departure timestamp with time zone,
                actual_arrival timestamp with time zone,
                CONSTRAINT flights_pkey PRIMARY KEY (flight_id),
                CONSTRAINT flights_flight_no_scheduled_departure_key UNIQUE (flight_no, scheduled_departure),
                CONSTRAINT flights_check CHECK (scheduled_arrival > scheduled_departure),
                CONSTRAINT flights_check1 CHECK (actual_arrival IS NULL OR 
                    (actual_departure IS NOT NULL AND actual_arrival IS NOT NULL AND actual_arrival > actual_departure)),
                CONSTRAINT flights_status_check CHECK (status::text = ANY (ARRAY['On Time'::character varying::text, 
                    'Delayed'::character varying::text, 'Departed'::character varying::text, 
                    'Arrived'::character varying::text, 'Scheduled'::character varying::text, 
                    'Cancelled'::character varying::text]))
            );
            """
            cursor.execute(create_table_query)
            db.connection.commit()
            print("Таблица flights создана или уже существует")
        except Exception as e:
            print(f"Ошибка при создании таблицы flights: {e}")

    @staticmethod
    def create(db, flight_no, scheduled_departure, scheduled_arrival,
               departure_airport, arrival_airport, status, aircraft_code,
               actual_departure=None, actual_arrival=None):
        """Создание новой записи рейса"""
        try:
            cursor = db.get_cursor()
            insert_query = """
            INSERT INTO bookings.flights 
            (flight_no, scheduled_departure, scheduled_arrival, departure_airport, 
             arrival_airport, status, aircraft_code, actual_departure, actual_arrival)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING flight_id
            """
            cursor.execute(insert_query, (
                flight_no, scheduled_departure, scheduled_arrival,
                departure_airport, arrival_airport, status, aircraft_code,
                actual_departure, actual_arrival
            ))

            result = cursor.fetchone()
            flight_id = result['flight_id']

            db.connection.commit()
            print(f"Рейс {flight_no} (ID: {flight_id}) успешно создан")
            return flight_id
        except Exception as e:
            print(f"Ошибка при создании рейса: {e}")
            return None

    @staticmethod
    def read_all(db):
        """Чтение всех записей рейсов"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT * FROM bookings.flights 
                ORDER BY scheduled_departure DESC
            """)
            results = cursor.fetchall()

            flights = []
            for row in results:
                flight = Flight(
                    flight_id=row['flight_id'],
                    flight_no=row['flight_no'],
                    scheduled_departure=row['scheduled_departure'],
                    scheduled_arrival=row['scheduled_arrival'],
                    departure_airport=row['departure_airport'],
                    arrival_airport=row['arrival_airport'],
                    status=row['status'],
                    aircraft_code=row['aircraft_code'],
                    actual_departure=row['actual_departure'],
                    actual_arrival=row['actual_arrival']
                )
                flights.append(flight)

            return flights
        except Exception as e:
            print(f"Ошибка при чтении рейсов: {e}")
            return []

    @staticmethod
    def read_by_id(db, flight_id):
        """Чтение рейса по ID"""
        try:
            cursor = db.get_cursor()
            cursor.execute("SELECT * FROM bookings.flights WHERE flight_id = %s", (flight_id,))
            result = cursor.fetchone()

            if result:
                return Flight(
                    flight_id=result['flight_id'],
                    flight_no=result['flight_no'],
                    scheduled_departure=result['scheduled_departure'],
                    scheduled_arrival=result['scheduled_arrival'],
                    departure_airport=result['departure_airport'],
                    arrival_airport=result['arrival_airport'],
                    status=result['status'],
                    aircraft_code=result['aircraft_code'],
                    actual_departure=result['actual_departure'],
                    actual_arrival=result['actual_arrival']
                )
            return None
        except Exception as e:
            print(f"Ошибка при поиске рейса: {e}")
            return None

    @staticmethod
    def read_by_flight_no(db, flight_no):
        """Чтение рейсов по номеру рейса"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT * FROM bookings.flights 
                WHERE flight_no = %s 
                ORDER BY scheduled_departure DESC
            """, (flight_no,))
            results = cursor.fetchall()

            flights = []
            for row in results:
                flight = Flight(
                    flight_id=row['flight_id'],
                    flight_no=row['flight_no'],
                    scheduled_departure=row['scheduled_departure'],
                    scheduled_arrival=row['scheduled_arrival'],
                    departure_airport=row['departure_airport'],
                    arrival_airport=row['arrival_airport'],
                    status=row['status'],
                    aircraft_code=row['aircraft_code'],
                    actual_departure=row['actual_departure'],
                    actual_arrival=row['actual_arrival']
                )
                flights.append(flight)

            return flights
        except Exception as e:
            print(f"Ошибка при поиске рейсов по номеру: {e}")
            return []

    @staticmethod
    def read_by_airport(db, airport_code):
        """Чтение рейсов по аэропорту (вылет или прилет)"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT * FROM bookings.flights 
                WHERE departure_airport = %s OR arrival_airport = %s 
                ORDER BY scheduled_departure DESC
            """, (airport_code, airport_code))
            results = cursor.fetchall()

            flights = []
            for row in results:
                flight = Flight(
                    flight_id=row['flight_id'],
                    flight_no=row['flight_no'],
                    scheduled_departure=row['scheduled_departure'],
                    scheduled_arrival=row['scheduled_arrival'],
                    departure_airport=row['departure_airport'],
                    arrival_airport=row['arrival_airport'],
                    status=row['status'],
                    aircraft_code=row['aircraft_code'],
                    actual_departure=row['actual_departure'],
                    actual_arrival=row['actual_arrival']
                )
                flights.append(flight)

            return flights
        except Exception as e:
            print(f"Ошибка при поиске рейсов по аэропорту: {e}")
            return []

    @staticmethod
    def read_by_status(db, status):
        """Чтение рейсов по статусу"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT * FROM bookings.flights 
                WHERE status = %s 
                ORDER BY scheduled_departure DESC
            """, (status,))
            results = cursor.fetchall()

            flights = []
            for row in results:
                flight = Flight(
                    flight_id=row['flight_id'],
                    flight_no=row['flight_no'],
                    scheduled_departure=row['scheduled_departure'],
                    scheduled_arrival=row['scheduled_arrival'],
                    departure_airport=row['departure_airport'],
                    arrival_airport=row['arrival_airport'],
                    status=row['status'],
                    aircraft_code=row['aircraft_code'],
                    actual_departure=row['actual_departure'],
                    actual_arrival=row['actual_arrival']
                )
                flights.append(flight)

            return flights
        except Exception as e:
            print(f"Ошибка при поиске рейсов по статусу: {e}")
            return []

    @staticmethod
    def read_by_date_range(db, start_date, end_date):
        """Чтение рейсов по диапазону дат"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT * FROM bookings.flights 
                WHERE scheduled_departure BETWEEN %s AND %s 
                ORDER BY scheduled_departure
            """, (start_date, end_date))
            results = cursor.fetchall()

            flights = []
            for row in results:
                flight = Flight(
                    flight_id=row['flight_id'],
                    flight_no=row['flight_no'],
                    scheduled_departure=row['scheduled_departure'],
                    scheduled_arrival=row['scheduled_arrival'],
                    departure_airport=row['departure_airport'],
                    arrival_airport=row['arrival_airport'],
                    status=row['status'],
                    aircraft_code=row['aircraft_code'],
                    actual_departure=row['actual_departure'],
                    actual_arrival=row['actual_arrival']
                )
                flights.append(flight)

            return flights
        except Exception as e:
            print(f"Ошибка при поиске рейсов по диапазону дат: {e}")
            return []

    @staticmethod
    def update_status(db, flight_id, status):
        """Обновление статуса рейса"""
        try:
            valid_statuses = ['Scheduled', 'On Time', 'Delayed', 'Departed', 'Arrived', 'Cancelled']
            if status not in valid_statuses:
                print(f"Ошибка: неверный статус. Допустимые значения: {', '.join(valid_statuses)}")
                return False

            cursor = db.get_cursor()
            update_query = "UPDATE bookings.flights SET status = %s WHERE flight_id = %s"

            cursor.execute(update_query, (status, flight_id))
            db.connection.commit()

            if cursor.rowcount > 0:
                print(f"Статус рейса {flight_id} обновлен: {status}")
                return True
            else:
                print(f"Рейс {flight_id} не найден")
                return False
        except Exception as e:
            print(f"Ошибка при обновлении статуса рейса: {e}")
            return False

    @staticmethod
    def update_actual_times(db, flight_id, actual_departure=None, actual_arrival=None):
        """Обновление фактического времени вылета/прилета"""
        try:
            cursor = db.get_cursor()
            update_fields = []
            params = []

            if actual_departure is not None:
                update_fields.append("actual_departure = %s")
                params.append(actual_departure)

            if actual_arrival is not None:
                update_fields.append("actual_arrival = %s")
                params.append(actual_arrival)

            if not update_fields:
                print("Нет данных для обновления")
                return False

            params.append(flight_id)
            update_query = f"UPDATE bookings.flights SET {', '.join(update_fields)} WHERE flight_id = %s"

            cursor.execute(update_query, params)
            db.connection.commit()

            if cursor.rowcount > 0:
                print(f"Фактическое время рейса {flight_id} обновлено")
                return True
            else:
                print(f"Рейс {flight_id} не найден")
                return False
        except Exception as e:
            print(f"Ошибка при обновлении фактического времени: {e}")
            return False

    @staticmethod
    def update_scheduled_times(db, flight_id, scheduled_departure=None, scheduled_arrival=None):
        """Обновление планового времени вылета/прилета"""
        try:
            cursor = db.get_cursor()
            update_fields = []
            params = []

            if scheduled_departure is not None:
                update_fields.append("scheduled_departure = %s")
                params.append(scheduled_departure)

            if scheduled_arrival is not None:
                update_fields.append("scheduled_arrival = %s")
                params.append(scheduled_arrival)

            if not update_fields:
                print("Нет данных для обновления")
                return False

            params.append(flight_id)
            update_query = f"UPDATE bookings.flights SET {', '.join(update_fields)} WHERE flight_id = %s"

            cursor.execute(update_query, params)
            db.connection.commit()

            if cursor.rowcount > 0:
                print(f"Плановое время рейса {flight_id} обновлено")
                return True
            else:
                print(f"Рейс {flight_id} не найден")
                return False
        except Exception as e:
            print(f"Ошибка при обновлении планового времени: {e}")
            return False

    @staticmethod
    def delete(db, flight_id):
        """Удаление рейса"""
        try:
            cursor = db.get_cursor()
            delete_query = "DELETE FROM bookings.flights WHERE flight_id = %s"
            cursor.execute(delete_query, (flight_id,))
            db.connection.commit()

            if cursor.rowcount > 0:
                print(f"Рейс {flight_id} успешно удален")
                return True
            else:
                print(f"Рейс {flight_id} не найден")
                return False
        except Exception as e:
            print(f"Ошибка при удалении рейса: {e}")
            return False

    @staticmethod
    def get_available_statuses():
        """Получение списка доступных статусов"""
        return ['Scheduled', 'On Time', 'Delayed', 'Departed', 'Arrived', 'Cancelled']

    @staticmethod
    def read_all_paginated(db, offset, limit):
        """Чтение записей рейсов с пагинацией"""
        try:
            cursor = db.get_cursor()

            # Получаем данные
            cursor.execute("""
                    SELECT * FROM bookings.flights 
                    ORDER BY scheduled_departure DESC
                    LIMIT %s OFFSET %s
                """, (limit, offset))
            results = cursor.fetchall()

            flights = []
            for row in results:
                flight = Flight(
                    flight_id=row['flight_id'],
                    flight_no=row['flight_no'],
                    scheduled_departure=row['scheduled_departure'],
                    scheduled_arrival=row['scheduled_arrival'],
                    departure_airport=row['departure_airport'],
                    arrival_airport=row['arrival_airport'],
                    status=row['status'],
                    aircraft_code=row['aircraft_code'],
                    actual_departure=row['actual_departure'],
                    actual_arrival=row['actual_arrival']
                )
                flights.append(flight)

            # Получаем общее количество
            cursor.execute("SELECT COUNT(*) FROM bookings.flights")
            total = cursor.fetchone()['count']

            return flights, total
        except Exception as e:
            print(f"Ошибка при чтении рейсов: {e}")
            return [], 0