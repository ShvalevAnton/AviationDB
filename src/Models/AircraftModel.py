import json


class Aircraft:
    def __init__(self, aircraft_code, model, range):
        self.aircraft_code = aircraft_code
        self.model = model  # JSONB данные
        self.range = range

    def __str__(self):
        model_str = json.dumps(self.model, ensure_ascii=False)
        return f"Aircraft {self.aircraft_code}: {model_str}, range: {self.range} km"

    @staticmethod
    def create_table(db):
        """Создание таблицы aircrafts_data"""
        try:
            cursor = db.get_cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS bookings.aircrafts_data
            (
                aircraft_code character(3) COLLATE pg_catalog."default" NOT NULL,
                model jsonb NOT NULL,
                range integer NOT NULL,
                CONSTRAINT aircrafts_pkey PRIMARY KEY (aircraft_code),
                CONSTRAINT aircrafts_range_check CHECK (range > 0)
            );
            """
            cursor.execute(create_table_query)
            db.connection.commit()
            print("Таблица aircrafts_data создана или уже существует")
        except Exception as e:
            print(f"Ошибка при создании таблицы aircrafts_data: {e}")

    @staticmethod
    def create(db, aircraft_code, model, range):
        """Создание новой записи самолета"""
        try:
            cursor = db.get_cursor()
            insert_query = """
            INSERT INTO bookings.aircrafts_data (aircraft_code, model, range)
            VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (aircraft_code, json.dumps(model), range))
            db.connection.commit()
            print(f"Самолет {aircraft_code} успешно создан")
            return True
        except Exception as e:
            print(f"Ошибка при создании самолета: {e}")
            return False

    @staticmethod
    def read_all(db):
        """Чтение всех записей самолетов"""
        try:
            cursor = db.get_cursor()
            cursor.execute("SELECT * FROM bookings.aircrafts_data ORDER BY aircraft_code")
            results = cursor.fetchall()

            aircrafts = []
            for row in results:
                aircraft = Aircraft(
                    aircraft_code=row['aircraft_code'],
                    model=row['model'],
                    range=row['range']
                )
                aircrafts.append(aircraft)

            return aircrafts
        except Exception as e:
            print(f"Ошибка при чтении самолетов: {e}")
            return []

    @staticmethod
    def read_by_code(db, aircraft_code):
        """Чтение самолета по коду"""
        try:
            cursor = db.get_cursor()
            cursor.execute("SELECT * FROM bookings.aircrafts_data WHERE aircraft_code = %s", (aircraft_code,))
            result = cursor.fetchone()

            if result:
                return Aircraft(
                    aircraft_code=result['aircraft_code'],
                    model=result['model'],
                    range=result['range']
                )
            return None
        except Exception as e:
            print(f"Ошибка при поиске самолета: {e}")
            return None

    @staticmethod
    def update(db, aircraft_code, model=None, range=None):
        """Обновление данных самолета"""
        try:
            cursor = db.get_cursor()
            update_fields = []
            params = []

            if model is not None:
                update_fields.append("model = %s")
                params.append(json.dumps(model))

            if range is not None:
                update_fields.append("range = %s")
                params.append(range)

            if not update_fields:
                print("Нет данных для обновления")
                return False

            params.append(aircraft_code)
            update_query = f"""
            UPDATE bookings.aircrafts_data 
            SET {', '.join(update_fields)} 
            WHERE aircraft_code = %s
            """

            cursor.execute(update_query, params)
            db.connection.commit()

            if cursor.rowcount > 0:
                print(f"Самолет {aircraft_code} успешно обновлен")
                return True
            else:
                print(f"Самолет {aircraft_code} не найден")
                return False
        except Exception as e:
            print(f"Ошибка при обновлении самолета: {e}")
            return False

    @staticmethod
    def delete(db, aircraft_code):
        """Удаление самолета"""
        try:
            cursor = db.get_cursor()
            delete_query = "DELETE FROM bookings.aircrafts_data WHERE aircraft_code = %s"
            cursor.execute(delete_query, (aircraft_code,))
            db.connection.commit()

            if cursor.rowcount > 0:
                print(f"Самолет {aircraft_code} успешно удален")
                return True
            else:
                print(f"Самолет {aircraft_code} не найден")
                return False
        except Exception as e:
            print(f"Ошибка при удалении самолета: {e}")
            return False

    @staticmethod
    def read_all_paginated(db, offset, limit):
        """Чтение записей самолетов с пагинацией"""
        try:
            cursor = db.get_cursor()

            # Получаем данные
            cursor.execute("""
                   SELECT * FROM bookings.aircrafts_data 
                   ORDER BY aircraft_code 
                   LIMIT %s OFFSET %s
               """, (limit, offset))
            results = cursor.fetchall()

            aircrafts = []
            for row in results:
                aircraft = Aircraft(
                    aircraft_code=row['aircraft_code'],
                    model=row['model'],
                    range=row['range']
                )
                aircrafts.append(aircraft)

            # Получаем общее количество
            cursor.execute("SELECT COUNT(*) FROM bookings.aircrafts_data")
            total = cursor.fetchone()['count']

            return aircrafts, total
        except Exception as e:
            print(f"Ошибка при чтении самолетов: {e}")
            return [], 0