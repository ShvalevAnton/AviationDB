import json


class Ticket:
    def __init__(self, ticket_no, book_ref, passenger_id, passenger_name, contact_data=None):
        self.ticket_no = ticket_no
        self.book_ref = book_ref
        self.passenger_id = passenger_id
        self.passenger_name = passenger_name
        self.contact_data = contact_data

    def __str__(self):
        contact_info = json.dumps(self.contact_data, ensure_ascii=False) if self.contact_data else "Нет данных"
        return f"Ticket {self.ticket_no}: {self.passenger_name} (Booking: {self.book_ref})"

    @staticmethod
    def create_table(db):
        """Создание таблицы tickets"""
        try:
            cursor = db.get_cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS bookings.tickets
            (
                ticket_no character(13) COLLATE pg_catalog."default" NOT NULL,
                book_ref character(6) COLLATE pg_catalog."default" NOT NULL,
                passenger_id character varying(20) COLLATE pg_catalog."default" NOT NULL,
                passenger_name text COLLATE pg_catalog."default" NOT NULL,
                contact_data jsonb,
                CONSTRAINT tickets_pkey PRIMARY KEY (ticket_no)
            );
            """
            cursor.execute(create_table_query)
            db.connection.commit()
            print("Таблица tickets создана или уже существует")
        except Exception as e:
            print(f"Ошибка при создании таблицы tickets: {e}")

    @staticmethod
    def create(db, ticket_no, book_ref, passenger_id, passenger_name, contact_data=None):
        """Создание нового билета"""
        try:
            if len(ticket_no) != 13:
                print("Ошибка: номер билета должен содержать 13 символов")
                return False

            if len(book_ref) != 6:
                print("Ошибка: номер бронирования должен содержать 6 символов")
                return False

            cursor = db.get_cursor()
            insert_query = """
            INSERT INTO bookings.tickets (ticket_no, book_ref, passenger_id, passenger_name, contact_data)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                ticket_no,
                book_ref,
                passenger_id,
                passenger_name,
                json.dumps(contact_data) if contact_data else None
            ))
            db.connection.commit()
            print(f"Билет {ticket_no} для пассажира {passenger_name} успешно создан")
            return True
        except Exception as e:
            print(f"Ошибка при создании билета: {e}")
            return False

    @staticmethod
    def read_all(db):
        """Чтение всех билетов"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT * FROM bookings.tickets 
                ORDER BY book_ref, ticket_no
            """)
            results = cursor.fetchall()

            tickets = []
            for row in results:
                ticket = Ticket(
                    ticket_no=row['ticket_no'],
                    book_ref=row['book_ref'],
                    passenger_id=row['passenger_id'],
                    passenger_name=row['passenger_name'],
                    contact_data=row['contact_data']
                )
                tickets.append(ticket)

            return tickets
        except Exception as e:
            print(f"Ошибка при чтении билетов: {e}")
            return []

    @staticmethod
    def read_by_ticket_no(db, ticket_no):
        """Чтение билета по номеру"""
        try:
            cursor = db.get_cursor()
            cursor.execute("SELECT * FROM bookings.tickets WHERE ticket_no = %s", (ticket_no,))
            result = cursor.fetchone()

            if result:
                return Ticket(
                    ticket_no=result['ticket_no'],
                    book_ref=result['book_ref'],
                    passenger_id=result['passenger_id'],
                    passenger_name=result['passenger_name'],
                    contact_data=result['contact_data']
                )
            return None
        except Exception as e:
            print(f"Ошибка при поиске билета: {e}")
            return None

    @staticmethod
    def read_by_booking(db, book_ref):
        """Чтение всех билетов по бронированию"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT * FROM bookings.tickets 
                WHERE book_ref = %s 
                ORDER BY ticket_no
            """, (book_ref,))
            results = cursor.fetchall()

            tickets = []
            for row in results:
                ticket = Ticket(
                    ticket_no=row['ticket_no'],
                    book_ref=row['book_ref'],
                    passenger_id=row['passenger_id'],
                    passenger_name=row['passenger_name'],
                    contact_data=row['contact_data']
                )
                tickets.append(ticket)

            return tickets
        except Exception as e:
            print(f"Ошибка при поиске билетов по бронированию: {e}")
            return []

    @staticmethod
    def read_by_passenger_id(db, passenger_id):
        """Чтение билетов по ID пассажира"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT * FROM bookings.tickets 
                WHERE passenger_id = %s 
                ORDER BY book_ref DESC
            """, (passenger_id,))
            results = cursor.fetchall()

            tickets = []
            for row in results:
                ticket = Ticket(
                    ticket_no=row['ticket_no'],
                    book_ref=row['book_ref'],
                    passenger_id=row['passenger_id'],
                    passenger_name=row['passenger_name'],
                    contact_data=row['contact_data']
                )
                tickets.append(ticket)

            return tickets
        except Exception as e:
            print(f"Ошибка при поиске билетов по ID пассажира: {e}")
            return []

    @staticmethod
    def search_by_passenger_name(db, passenger_name):
        """Поиск билетов по имени пассажира"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT * FROM bookings.tickets 
                WHERE passenger_name ILIKE %s 
                ORDER BY passenger_name, book_ref DESC
            """, (f'%{passenger_name}%',))
            results = cursor.fetchall()

            tickets = []
            for row in results:
                ticket = Ticket(
                    ticket_no=row['ticket_no'],
                    book_ref=row['book_ref'],
                    passenger_id=row['passenger_id'],
                    passenger_name=row['passenger_name'],
                    contact_data=row['contact_data']
                )
                tickets.append(ticket)

            return tickets
        except Exception as e:
            print(f"Ошибка при поиске билетов по имени пассажира: {e}")
            return []

    @staticmethod
    def update_passenger_info(db, ticket_no, passenger_name=None, passenger_id=None, contact_data=None):
        """Обновление информации о пассажире"""
        try:
            cursor = db.get_cursor()
            update_fields = []
            params = []

            if passenger_name is not None:
                update_fields.append("passenger_name = %s")
                params.append(passenger_name)

            if passenger_id is not None:
                update_fields.append("passenger_id = %s")
                params.append(passenger_id)

            if contact_data is not None:
                update_fields.append("contact_data = %s")
                params.append(json.dumps(contact_data))

            if not update_fields:
                print("Нет данных для обновления")
                return False

            params.append(ticket_no)
            update_query = f"""
            UPDATE bookings.tickets 
            SET {', '.join(update_fields)} 
            WHERE ticket_no = %s
            """

            cursor.execute(update_query, params)
            db.connection.commit()

            if cursor.rowcount > 0:
                print(f"Информация о пассажире для билета {ticket_no} обновлена")
                return True
            else:
                print("Билет не найден")
                return False
        except Exception as e:
            print(f"Ошибка при обновлении информации о пассажире: {e}")
            return False

    @staticmethod
    def update_booking_reference(db, ticket_no, book_ref):
        """Обновление номера бронирования"""
        try:
            if len(book_ref) != 6:
                print("Ошибка: номер бронирования должен содержать 6 символов")
                return False

            cursor = db.get_cursor()
            update_query = "UPDATE bookings.tickets SET book_ref = %s WHERE ticket_no = %s"

            cursor.execute(update_query, (book_ref, ticket_no))
            db.connection.commit()

            if cursor.rowcount > 0:
                print(f"Номер бронирования для билета {ticket_no} обновлен: {book_ref}")
                return True
            else:
                print("Билет не найден")
                return False
        except Exception as e:
            print(f"Ошибка при обновлении номера бронирования: {e}")
            return False

    @staticmethod
    def delete(db, ticket_no):
        """Удаление билета"""
        try:
            cursor = db.get_cursor()
            delete_query = "DELETE FROM bookings.tickets WHERE ticket_no = %s"
            cursor.execute(delete_query, (ticket_no,))
            db.connection.commit()

            if cursor.rowcount > 0:
                print(f"Билет {ticket_no} успешно удален")
                return True
            else:
                print("Билет не найден")
                return False
        except Exception as e:
            print(f"Ошибка при удалении билета: {e}")
            return False

    @staticmethod
    def delete_by_booking(db, book_ref):
        """Удаление всех билетов по бронированию"""
        try:
            cursor = db.get_cursor()
            delete_query = "DELETE FROM bookings.tickets WHERE book_ref = %s"
            cursor.execute(delete_query, (book_ref,))
            db.connection.commit()

            print(f"Все билеты для бронирования {book_ref} удалены")
            return True
        except Exception as e:
            print(f"Ошибка при удалении билетов по бронированию: {e}")
            return False

    @staticmethod
    def get_booking_statistics(db, book_ref):
        """Получение статистики по бронированию"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as ticket_count,
                    STRING_AGG(passenger_name, ', ') as passengers
                FROM bookings.tickets 
                WHERE book_ref = %s
            """, (book_ref,))
            result = cursor.fetchone()

            return result
        except Exception as e:
            print(f"Ошибка при получении статистики по бронированию: {e}")
            return None

    @staticmethod
    def get_passenger_flight_history(db, passenger_id):
        """Получение истории полетов пассажира"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT 
                    t.ticket_no,
                    t.book_ref,
                    t.passenger_name,
                    COUNT(tf.flight_id) as flight_count,
                    SUM(tf.amount) as total_spent
                FROM bookings.tickets t
                LEFT JOIN bookings.ticket_flights tf ON t.ticket_no = tf.ticket_no
                WHERE t.passenger_id = %s
                GROUP BY t.ticket_no, t.book_ref, t.passenger_name
                ORDER BY t.book_ref DESC
            """, (passenger_id,))
            results = cursor.fetchall()

            return results
        except Exception as e:
            print(f"Ошибка при получении истории полетов: {e}")
            return []

    @staticmethod
    def read_all_paginated(db, offset, limit):
        """Чтение билетов с пагинацией"""
        try:
            cursor = db.get_cursor()

            # Получаем данные с пагинацией
            cursor.execute("""
                SELECT * FROM bookings.tickets 
                ORDER BY book_ref, ticket_no
                LIMIT %s OFFSET %s
            """, (limit, offset))
            results = cursor.fetchall()

            tickets = []
            for row in results:
                ticket = Ticket(
                    ticket_no=row['ticket_no'],
                    book_ref=row['book_ref'],
                    passenger_id=row['passenger_id'],
                    passenger_name=row['passenger_name'],
                    contact_data=row['contact_data']
                )
                tickets.append(ticket)

            # Получаем общее количество
            cursor.execute("SELECT COUNT(*) FROM bookings.tickets")
            total = cursor.fetchone()['count']

            return {
                'tickets': tickets,
                'total_count': total
            }
        except Exception as e:
            print(f"Ошибка при чтении билетов с пагинацией: {e}")
            return {
                'tickets': [],
                'total_count': 0
            }