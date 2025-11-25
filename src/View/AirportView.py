import tkinter as tk
from src.View.BaseView import BaseView
from tkinter import ttk, messagebox
import json


class AirportView(BaseView):
    def setup_ui(self):
        """Настройка UI для аэропортов с пагинацией"""
        # Заголовок
        title_label = ttk.Label(self.tab, text="Управление аэропортами",
                                font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)

        # Фрейм для кнопок
        button_frame = ttk.Frame(self.tab)
        button_frame.pack(pady=10)

        # Кнопки управления
        buttons = [
            ("Показать все", self.refresh_data),
            ("Создать", self.show_create_dialog),
            ("Найти", self.show_find_dialog),
            ("Обновить", self.show_update_dialog),
            ("Удалить", self.show_delete_dialog),
            ("Ближайшие", self.show_nearby_dialog)
        ]

        # Создаем кнопки в две строки для лучшего отображения
        for i, (text, command) in enumerate(buttons[:4]):  # Первые 4 кнопки
            ttk.Button(button_frame, text=text, command=command).grid(
                row=0, column=i, padx=3, pady=3
            )

        for i, (text, command) in enumerate(buttons[4:]):  # Остальные кнопки
            ttk.Button(button_frame, text=text, command=command).grid(
                row=1, column=i, padx=3, pady=3
            )

        # Treeview
        columns = ('airport_code', 'airport_name', 'city', 'coordinates', 'timezone')
        self.tree = ttk.Treeview(self.tab, columns=columns, show='headings')

        # Настраиваем заголовки колонок
        self.tree.heading('airport_code', text='Код аэропорта')
        self.tree.heading('airport_name', text='Название')
        self.tree.heading('city', text='Город')
        self.tree.heading('coordinates', text='Координаты')
        self.tree.heading('timezone', text='Часовой пояс')

        # Настраиваем ширину колонок
        self.tree.column('airport_code', width=100)
        self.tree.column('airport_name', width=200)
        self.tree.column('city', width=150)
        self.tree.column('coordinates', width=150)
        self.tree.column('timezone', width=120)

        # Добавляем scrollbar
        scrollbar = ttk.Scrollbar(self.tab, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        # Упаковываем элементы
        self.tree.pack(fill='both', expand=True, padx=10, pady=5)
        scrollbar.pack(side='right', fill='y')

        # Элементы пагинации
        self.setup_pagination_controls(self.tab)

        # Загружаем данные
        self.refresh_data()

    def center_dialog(self, dialog):
        """Центрирование диалогового окна относительно родительского окна"""
        dialog.update_idletasks()

        # Получаем размеры диалогового окна
        dialog_width = dialog.winfo_width()
        dialog_height = dialog.winfo_height()

        # Получаем позицию родительского окна
        parent_x = self.tab.winfo_rootx()
        parent_y = self.tab.winfo_rooty()
        parent_width = self.tab.winfo_width()
        parent_height = self.tab.winfo_height()

        # Вычисляем позицию для центрирования относительно родительского окна
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2

        # Устанавливаем позицию
        dialog.geometry(f"+{x}+{y}")

    def refresh_data(self):
        """Обновление данных в таблице с пагинацией"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Получаем параметры пагинации
        offset, limit = self.get_pagination_params()

        # Получаем данные с пагинацией
        airports, total = self.controller.get_all_airports_paginated(offset, limit)
        self.total_records = total

        for airport in airports:
            # Форматируем JSON данные для отображения
            airport_name_str = str(airport.airport_name)[:200] if airport.airport_name else "Нет данных"
            airport_name_str = airport_name_str.replace('{', '').replace('}', '').replace("'", "")

            city_str = str(airport.city)[:200] if airport.city else "Нет данных"
            city_str = city_str.replace('{', '').replace('}', '').replace("'", "")

            # Извлекаем координаты из строки POINT
            coords = airport.coordinates.replace('POINT(', '').replace(')', '')

            # Форматируем координаты в формат XX.XXXX
            try:
                # Разделяем координаты на долготу и широту
                lon, lat = coords.split()
                # Форматируем каждую координату
                formatted_lon = f"{float(lon):.4f}"
                formatted_lat = f"{float(lat):.4f}"
                # Объединяем обратно
                coords = f"{formatted_lon} {formatted_lat}"
            except (ValueError, AttributeError):
                # Если возникла ошибка при преобразовании, оставляем исходное значение
                coords = coords if coords else "Нет данных"

            self.tree.insert('', 'end', values=(
                airport.airport_code,
                airport_name_str,
                city_str,
                coords,
                airport.timezone
            ))

        # Обновляем элементы управления пагинацией
        self.update_pagination_controls()

    def show_create_dialog(self):
        """Диалог создания аэропорта"""
        fields = {
            'airport_code': {'label': 'Код аэропорта (3 символа):', 'type': 'entry'},
            'airport_name_en': {'label': 'Название аэропорта (английский):', 'type': 'entry'},
            'airport_name_ru': {'label': 'Название аэропорта (русский):', 'type': 'entry'},
            'city_en': {'label': 'Город (английский):', 'type': 'entry'},
            'city_ru': {'label': 'Город (русский):', 'type': 'entry'},
            'longitude': {'label': 'Долгота:', 'type': 'entry', 'default': '37.4144'},
            'latitude': {'label': 'Широта:', 'type': 'entry', 'default': '55.9726'},
            'timezone': {'label': 'Часовой пояс:', 'type': 'entry', 'default': 'Europe/Moscow'}
        }

        def create_callback(data):
            airport_code = data['airport_code'].upper()
            airport_name_en = data['airport_name_en'].strip()
            airport_name_ru = data['airport_name_ru'].strip()
            city_en = data['city_en'].strip()
            city_ru = data['city_ru'].strip()
            longitude = data['longitude']
            latitude = data['latitude']
            timezone = data['timezone']

            if len(airport_code) != 3:
                messagebox.showerror("Ошибка", "Код аэропорта должен содержать 3 символа")
                return

            if not airport_name_en or not airport_name_ru:
                messagebox.showerror("Ошибка", "Заполните оба названия аэропорта")
                return

            if not city_en or not city_ru:
                messagebox.showerror("Ошибка", "Заполните оба названия города")
                return

            # Создаем JSON из отдельных полей
            airport_name_data = {
                "en": airport_name_en,
                "ru": airport_name_ru
            }
            city_data = {
                "en": city_en,
                "ru": city_ru
            }

            try:
                lon = float(longitude)
                lat = float(latitude)
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные координаты")
                return

            if self.controller.create_airport(airport_code, airport_name_data, city_data, lon, lat, timezone):
                messagebox.showinfo("Успех", "Аэропорт создан!")
                self.refresh_data()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать аэропорт")

        self.create_dialog("Создание аэропорта", fields, create_callback)

    def show_find_dialog(self):
        """Диалог поиска аэропорта"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Поиск аэропорта")
        dialog.geometry("300x150")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="Код аэропорта:").pack(pady=5)
        code_entry = ttk.Entry(dialog)
        code_entry.pack(pady=5)

        def find():
            airport_code = code_entry.get().upper()
            airport = self.controller.find_airport(airport_code)

            if airport:
                # Парсим JSON данные названия аэропорта и города
                airport_name_en = airport.airport_name.get('en', 'Нет данных') if airport.airport_name else 'Нет данных'
                airport_name_ru = airport.airport_name.get('ru', 'Нет данных') if airport.airport_name else 'Нет данных'
                city_en = airport.city.get('en', 'Нет данных') if airport.city else 'Нет данных'
                city_ru = airport.city.get('ru', 'Нет данных') if airport.city else 'Нет данных'

                # Форматируем координаты
                coords = airport.coordinates.replace('POINT(', '').replace(')', '')
                try:
                    lon, lat = coords.split()
                    formatted_lon = f"{float(lon):.4f}"
                    formatted_lat = f"{float(lat):.4f}"
                    coords = f"{formatted_lon} {formatted_lat}"
                except (ValueError, AttributeError):
                    coords = coords if coords else "Нет данных"

                result = f"Найден аэропорт:\n\n"
                result += f"Код: {airport.airport_code}\n"
                result += f"Название (англ.): {airport_name_en}\n"
                result += f"Название (рус.): {airport_name_ru}\n"
                result += f"Город (англ.): {city_en}\n"
                result += f"Город (рус.): {city_ru}\n"
                result += f"Координаты: {coords}\n"
                result += f"Часовой пояс: {airport.timezone}"
                messagebox.showinfo("Результат поиска", result)
            else:
                messagebox.showinfo("Результат поиска", "Аэропорт не найден")

            dialog.destroy()

        ttk.Button(dialog, text="Найти", command=find).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)

    def show_update_dialog(self):
        """Диалог обновления аэропорта"""
        fields = {
            'airport_code': {'label': 'Код аэропорта для обновления:', 'type': 'entry'},
            'airport_name_en': {'label': 'Новое название аэропорта (английский, оставьте пустым чтобы не менять):', 'type': 'entry'},
            'airport_name_ru': {'label': 'Новое название аэропорта (русский, оставьте пустым чтобы не менять):', 'type': 'entry'},
            'city_en': {'label': 'Новый город (английский, оставьте пустым чтобы не менять):', 'type': 'entry'},
            'city_ru': {'label': 'Новый город (русский, оставьте пустым чтобы не менять):', 'type': 'entry'},
            'longitude': {'label': 'Новая долгота (оставьте пустым чтобы не менять):', 'type': 'entry'},
            'latitude': {'label': 'Новая широта (оставьте пустым чтобы не менять):', 'type': 'entry'},
            'timezone': {'label': 'Новый часовой пояс (оставьте пустым чтобы не менять):', 'type': 'entry'}
        }

        def update_callback(data):
            airport_code = data['airport_code'].upper()
            airport_name_en = data['airport_name_en'].strip()
            airport_name_ru = data['airport_name_ru'].strip()
            city_en = data['city_en'].strip()
            city_ru = data['city_ru'].strip()
            longitude = data['longitude']
            latitude = data['latitude']
            timezone = data['timezone']

            airport_name_data = None
            if airport_name_en or airport_name_ru:
                airport_name_data = {}
                if airport_name_en:
                    airport_name_data["en"] = airport_name_en
                if airport_name_ru:
                    airport_name_data["ru"] = airport_name_ru

            city_data = None
            if city_en or city_ru:
                city_data = {}
                if city_en:
                    city_data["en"] = city_en
                if city_ru:
                    city_data["ru"] = city_ru

            lon = float(longitude) if longitude else None
            lat = float(latitude) if latitude else None

            if self.controller.update_airport(airport_code, airport_name_data, city_data, lon, lat, timezone):
                messagebox.showinfo("Успех", "Аэропорт обновлен!")
                self.refresh_data()
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить аэропорт")

        self.create_dialog("Обновление аэропорта", fields, update_callback, "700x400")

    def show_delete_dialog(self):
        """Диалог удаления аэропорта"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Удаление аэропорта")
        dialog.geometry("300x150")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="Код аэропорта для удаления:").pack(pady=5)
        code_entry = ttk.Entry(dialog)
        code_entry.pack(pady=5)

        def delete():
            airport_code = code_entry.get().upper()
            if messagebox.askyesno("Подтверждение",
                                   f"Вы уверены, что хотите удалить аэропорт {airport_code}?"):
                if self.controller.delete_airport(airport_code):
                    messagebox.showinfo("Успех", "Аэропорт удален!")
                    self.refresh_data()
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось удалить аэропорт")

        ttk.Button(dialog, text="Удалить", command=delete).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)

    def show_nearby_dialog(self):
        """Диалог поиска ближайших аэропортов"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Поиск ближайших аэропортов")
        dialog.geometry("300x300")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="Долгота:").pack(pady=5)
        lon_entry = ttk.Entry(dialog)
        lon_entry.pack(pady=5)
        lon_entry.insert(0, "37.6173")  # Москва

        ttk.Label(dialog, text="Широта:").pack(pady=5)
        lat_entry = ttk.Entry(dialog)
        lat_entry.pack(pady=5)
        lat_entry.insert(0, "55.7558")  # Москва

        ttk.Label(dialog, text="Радиус поиска (км):").pack(pady=5)
        radius_entry = ttk.Entry(dialog)
        radius_entry.pack(pady=5)
        radius_entry.insert(0, "100")

        def find_nearby():
            try:
                longitude = float(lon_entry.get())
                latitude = float(lat_entry.get())
                radius = float(radius_entry.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные координаты и радиус")
                return

            nearby_airports = self.controller.find_nearby_airports(longitude, latitude, radius)

            if not nearby_airports:
                messagebox.showinfo("Результат", f"В радиусе {radius} км аэропорты не найдены")
                dialog.destroy()
                return

            result = f"Аэропорты в радиусе {radius} км:\n\n"
            for airport, distance in nearby_airports:
                airport_name_str = json.dumps(airport.airport_name, ensure_ascii=False)
                result += f"• {airport.airport_code}: {airport_name_str} - {distance:.1f} км\n"

            messagebox.showinfo("Ближайшие аэропорты", result)
            dialog.destroy()

        ttk.Button(dialog, text="Найти", command=find_nearby).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)