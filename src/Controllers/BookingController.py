from datetime import datetime
from src.Models.BookingModel import Booking

class BookingController:
    def __init__(self, db):
        self.db = db
        # Создание таблицы при инициализации
        Booking.create_table(self.db)

    def get_all_bookings(self):
        """Получение всех бронирований"""
        return Booking.read_all(self.db)

    def create_booking(self, book_ref, total_amount):
        """Создание нового бронирования"""
        book_date = datetime.now()
        return Booking.create(self.db, book_ref, book_date, total_amount)

    def find_booking(self, book_ref):
        """Поиск бронирования по номеру"""
        return Booking.read_by_ref(self.db, book_ref)

    def update_booking(self, book_ref, total_amount=None):
        """Обновление данных бронирования"""
        return Booking.update(self.db, book_ref, total_amount)

    def delete_booking(self, book_ref):
        """Удаление бронирования"""
        return Booking.delete(self.db, book_ref)

    def get_all_bookings_paginated(self, offset, limit):
        """Получение бронирований с пагинацией"""
        return Booking.read_all_paginated(self.db, offset, limit)