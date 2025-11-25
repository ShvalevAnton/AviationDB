import json


class Airport:
    def __init__(self, airport_code, airport_name, city, coordinates, timezone):
        self.airport_code = airport_code
        self.airport_name = airport_name  # JSONB данные
        self.city = city  # JSONB данные
        self.coordinates = coordinates  # Geometry Point
        self.timezone = timezone

    def __str__(self):
        airport_name_str = json.dumps(self.airport_name, ensure_ascii=False)
        city_str = json.dumps(self.city, ensure_ascii=False)
        return f"Airport {self.airport_code}: {airport_name_str}, {city_str}, Timezone: {self.timezone}"

    @staticmethod
    def create_table(db):
        """Создание таблицы airports_data"""
        try:
            cursor = db.get_cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS bookings.airports_data
            (
                airport_code character(3) COLLATE pg_catalog."default" NOT NULL,
                airport_name jsonb NOT NULL,
                city jsonb NOT NULL,
                coordinates geometry(Point,4326) NOT NULL,
                timezone text COLLATE pg_catalog."default" NOT NULL,
                CONSTRAINT airports_data_pkey PRIMARY KEY (airport_code)
            );
            """
            cursor.execute(create_table_query)
            db.connection.commit()
            print("Таблица airports_data создана или уже существует")
        except Exception as e:
            print(f"Ошибка при создании таблицы airports_data: {e}")

    @staticmethod
    def create(db, airport_code, airport_name, city, longitude, latitude, timezone):
        """Создание новой записи аэропорта"""
        try:
            cursor = db.get_cursor()
            insert_query = """
            INSERT INTO bookings.airports_data (airport_code, airport_name, city, coordinates, timezone)
            VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
            """
            cursor.execute(insert_query, (
                airport_code,
                json.dumps(airport_name),
                json.dumps(city),
                longitude,
                latitude,
                timezone
            ))
            db.connection.commit()
            print(f"Аэропорт {airport_code} успешно создан")
            return True
        except Exception as e:
            print(f"Ошибка при создании аэропорта: {e}")
            return False

    @staticmethod
    def read_all(db):
        """Чтение всех записей аэропортов"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT airport_code, airport_name, city, timezone,
                       ST_X(coordinates) as longitude, 
                       ST_Y(coordinates) as latitude
                FROM bookings.airports_data 
                ORDER BY airport_code
            """)
            results = cursor.fetchall()

            airports = []
            for row in results:
                airport = Airport(
                    airport_code=row['airport_code'],
                    airport_name=row['airport_name'],
                    city=row['city'],
                    coordinates=f"POINT({row['longitude']} {row['latitude']})",
                    timezone=row['timezone']
                )
                airports.append(airport)

            return airports
        except Exception as e:
            print(f"Ошибка при чтении аэропортов: {e}")
            return []

    @staticmethod
    def read_by_code(db, airport_code):
        """Чтение аэропорта по коду"""
        try:
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT airport_code, airport_name, city, timezone,
                       ST_X(coordinates) as longitude, 
                       ST_Y(coordinates) as latitude
                FROM bookings.airports_data 
                WHERE airport_code = %s
            """, (airport_code,))
            result = cursor.fetchone()

            if result:
                return Airport(
                    airport_code=result['airport_code'],
                    airport_name=result['airport_name'],
                    city=result['city'],
                    coordinates=f"POINT({result['longitude']} {result['latitude']})",
                    timezone=result['timezone']
                )
            return None
        except Exception as e:
            print(f"Ошибка при поиске аэропорта: {e}")
            return None

    @staticmethod
    def update(db, airport_code, airport_name=None, city=None, longitude=None, latitude=None, timezone=None):
        """Обновление данных аэропорта"""
        try:
            cursor = db.get_cursor()
            update_fields = []
            params = []

            if airport_name is not None:
                update_fields.append("airport_name = %s")
                params.append(json.dumps(airport_name))

            if city is not None:
                update_fields.append("city = %s")
                params.append(json.dumps(city))

            if longitude is not None and latitude is not None:
                update_fields.append("coordinates = ST_SetSRID(ST_MakePoint(%s, %s), 4326)")
                params.extend([longitude, latitude])

            if timezone is not None:
                update_fields.append("timezone = %s")
                params.append(timezone)

            if not update_fields:
                print("Нет данных для обновления")
                return False

            params.append(airport_code)
            update_query = f"""
            UPDATE bookings.airports_data 
            SET {', '.join(update_fields)} 
            WHERE airport_code = %s
            """

            cursor.execute(update_query, params)
            db.connection.commit()

            if cursor.rowcount > 0:
                print(f"Аэропорт {airport_code} успешно обновлен")
                return True
            else:
                print(f"Аэропорт {airport_code} не найден")
                return False
        except Exception as e:
            print(f"Ошибка при обновлении аэропорта: {e}")
            return False

    @staticmethod
    def delete(db, airport_code):
        """Удаление аэропорта"""
        try:
            cursor = db.get_cursor()
            delete_query = "DELETE FROM bookings.airports_data WHERE airport_code = %s"
            cursor.execute(delete_query, (airport_code,))
            db.connection.commit()

            if cursor.rowcount > 0:
                print(f"Аэропорт {airport_code} успешно удален")
                return True
            else:
                print(f"Аэропорт {airport_code} не найден")
                return False
        except Exception as e:
            print(f"Ошибка при удалении аэропорта: {e}")
            return False

    @staticmethod
    def find_nearby_airports(db, longitude, latitude, radius_km=100):
        """Поиск аэропортов в радиусе от заданной точки"""
        try:
            cursor = db.get_cursor()
            query = """
            SELECT airport_code, airport_name, city, timezone,
                   ST_X(coordinates) as longitude, 
                   ST_Y(coordinates) as latitude,
                   ST_Distance(coordinates::geography, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography) / 1000 as distance_km
            FROM bookings.airports_data 
            WHERE ST_DWithin(coordinates::geography, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography, %s * 1000)
            ORDER BY distance_km
            """
            cursor.execute(query, (longitude, latitude, longitude, latitude, radius_km))
            results = cursor.fetchall()

            airports = []
            for row in results:
                airport = Airport(
                    airport_code=row['airport_code'],
                    airport_name=row['airport_name'],
                    city=row['city'],
                    coordinates=f"POINT({row['longitude']} {row['latitude']})",
                    timezone=row['timezone']
                )
                airports.append((airport, row['distance_km']))

            return airports
        except Exception as e:
            print(f"Ошибка при поиске ближайших аэропортов: {e}")
            return []

    @staticmethod
    def read_all_paginated(db, offset, limit):
        """Чтение записей аэропортов с пагинацией"""
        try:
            cursor = db.get_cursor()

            # Получаем данные
            cursor.execute("""
                   SELECT airport_code, airport_name, city, timezone,
                          ST_X(coordinates) as longitude, 
                          ST_Y(coordinates) as latitude
                   FROM bookings.airports_data 
                   ORDER BY airport_code 
                   LIMIT %s OFFSET %s
               """, (limit, offset))
            results = cursor.fetchall()

            airports = []
            for row in results:
                airport = Airport(
                    airport_code=row['airport_code'],
                    airport_name=row['airport_name'],
                    city=row['city'],
                    coordinates=f"POINT({row['longitude']} {row['latitude']})",
                    timezone=row['timezone']
                )
                airports.append(airport)

            # Получаем общее количество
            cursor.execute("SELECT COUNT(*) FROM bookings.airports_data")
            total = cursor.fetchone()['count']

            return airports, total
        except Exception as e:
            print(f"Ошибка при чтении аэропортов: {e}")
            return [], 0