# FlightsView.py
import tkinter as tk
from tkinter import ttk, messagebox
from src.View.BaseView import BaseView
from datetime import datetime

class FlightsView(BaseView):
    def setup_ui(self):
        """Настройка UI для рейсов с пагинацией"""
        # Заголовок
        title_label = ttk.Label(self.tab, text="Управление рейсами",
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
            ("Удалить", self.show_delete_dialog)
        ]

        for i, (text, command) in enumerate(buttons):
            ttk.Button(button_frame, text=text, command=command).grid(
                row=0, column=i, padx=5, pady=5
            )

        # Treeview
        columns = ('flight_id', 'flight_no', 'scheduled_departure', 'scheduled_arrival',
                   'departure_airport', 'arrival_airport', 'status', 'aircraft_code',
                   'actual_departure', 'actual_arrival')
        self.tree = ttk.Treeview(self.tab, columns=columns, show='headings')

        # Настраиваем заголовки колонок
        self.tree.heading('flight_id', text='ID')
        self.tree.heading('flight_no', text='Номер рейса')
        self.tree.heading('scheduled_departure', text='План. вылет')
        self.tree.heading('scheduled_arrival', text='План. прилет')
        self.tree.heading('departure_airport', text='Аэропорт вылета')
        self.tree.heading('arrival_airport', text='Аэропорт прилета')
        self.tree.heading('status', text='Статус')
        self.tree.heading('aircraft_code', text='Самолет')
        self.tree.heading('actual_departure', text='Факт. вылет')
        self.tree.heading('actual_arrival', text='Факт. прилет')

        # Настраиваем ширину колонок
        self.tree.column('flight_id', width=50)
        self.tree.column('flight_no', width=100)
        self.tree.column('scheduled_departure', width=120)
        self.tree.column('scheduled_arrival', width=120)
        self.tree.column('departure_airport', width=100)
        self.tree.column('arrival_airport', width=100)
        self.tree.column('status', width=80)
        self.tree.column('aircraft_code', width=70)
        self.tree.column('actual_departure', width=120)
        self.tree.column('actual_arrival', width=120)

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
        flights, total = self.controller.get_all_flights_paginated(offset, limit)
        self.total_records = total

        for flight in flights:
            scheduled_departure = flight.scheduled_departure.strftime(
                "%Y-%m-%d %H:%M") if flight.scheduled_departure else ""
            scheduled_arrival = flight.scheduled_arrival.strftime("%Y-%m-%d %H:%M") if flight.scheduled_arrival else ""
            actual_departure = flight.actual_departure.strftime("%Y-%m-%d %H:%M") if flight.actual_departure else ""
            actual_arrival = flight.actual_arrival.strftime("%Y-%m-%d %H:%M") if flight.actual_arrival else ""

            self.tree.insert('', 'end', values=(
                flight.flight_id,
                flight.flight_no,
                scheduled_departure,
                scheduled_arrival,
                flight.departure_airport,
                flight.arrival_airport,
                flight.status,
                flight.aircraft_code,
                actual_departure,
                actual_arrival
            ))

        # Обновляем элементы управления пагинацией
        self.update_pagination_controls()

    def show_create_dialog(self):
        """Диалог создания рейса"""
        fields = {
            'flight_no': {'label': 'Номер рейса (6 символов):', 'type': 'entry'},
            'scheduled_departure': {'label': 'Плановый вылет (ГГГГ-ММ-ДД ЧЧ:ММ):', 'type': 'entry'},
            'scheduled_arrival': {'label': 'Плановый прилет (ГГГГ-ММ-ДД ЧЧ:ММ):', 'type': 'entry'},
            'departure_airport': {'label': 'Аэропорт вылета (3 символа):', 'type': 'entry'},
            'arrival_airport': {'label': 'Аэропорт прилета (3 символа):', 'type': 'entry'},
            'aircraft_code': {'label': 'Код самолета (3 символа):', 'type': 'entry'},
            'status': {'label': 'Статус:', 'type': 'combobox', 'values': self.controller.get_available_statuses()}
        }

        def create_callback(data):
            # Валидация данных
            if len(data['flight_no']) != 6:
                messagebox.showerror("Ошибка", "Номер рейса должен содержать 6 символов")
                return

            if len(data['departure_airport']) != 3 or len(data['arrival_airport']) != 3:
                messagebox.showerror("Ошибка", "Коды аэропортов должны содержать 3 символа")
                return

            if len(data['aircraft_code']) != 3:
                messagebox.showerror("Ошибка", "Код самолета должен содержать 3 символа")
                return

            try:
                scheduled_departure = datetime.strptime(data['scheduled_departure'], "%Y-%m-%d %H:%M")
                scheduled_arrival = datetime.strptime(data['scheduled_arrival'], "%Y-%m-%d %H:%M")

                if scheduled_arrival <= scheduled_departure:
                    messagebox.showerror("Ошибка", "Время прилета должно быть позже времени вылета")
                    return

            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД ЧЧ:ММ")
                return

            flight_id = self.controller.create_flight(
                data['flight_no'],
                scheduled_departure,
                scheduled_arrival,
                data['departure_airport'],
                data['arrival_airport'],
                data['status'],
                data['aircraft_code']
            )

            if flight_id:
                messagebox.showinfo("Успех", f"Рейс создан! ID: {flight_id}")
                self.refresh_data()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать рейс")

        self.create_dialog("Создание рейса", fields, create_callback, "400x300")

    def show_find_dialog(self):
        """Диалог поиска рейса"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Поиск рейса")
        dialog.geometry("300x150")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="ID рейса:").pack(pady=5)
        id_entry = ttk.Entry(dialog)
        id_entry.pack(pady=5)

        def find():
            try:
                flight_id = int(id_entry.get())
                flight = self.controller.find_flight(flight_id)

                if flight:
                    result = f"Найден рейс:\n"
                    result += f"ID: {flight.flight_id}\n"
                    result += f"Номер: {flight.flight_no}\n"
                    result += f"Маршрут: {flight.departure_airport} -> {flight.arrival_airport}\n"
                    result += f"Статус: {flight.status}\n"
                    result += f"Самолет: {flight.aircraft_code}"
                    messagebox.showinfo("Результат поиска", result)
                else:
                    messagebox.showinfo("Результат поиска", "Рейс не найден")

                dialog.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректный ID рейса")

        ttk.Button(dialog, text="Найти", command=find).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)

    def show_update_dialog(self):
        """Диалог обновления рейса"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Обновление рейса")
        dialog.geometry("400x330")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="ID рейса для обновления:").pack(pady=5)
        id_entry = ttk.Entry(dialog)
        id_entry.pack(pady=5)

        ttk.Label(dialog, text="Новый номер рейса (6 символов):").pack(pady=5)
        flight_no_entry = ttk.Entry(dialog)
        flight_no_entry.pack(pady=5)

        ttk.Label(dialog, text="Новый статус:").pack(pady=5)
        status_combobox = ttk.Combobox(dialog, values=self.controller.get_available_statuses())
        status_combobox.pack(pady=5)

        ttk.Label(dialog, text="Новый код самолета (3 символа):").pack(pady=5)
        aircraft_entry = ttk.Entry(dialog)
        aircraft_entry.pack(pady=5)

        def update():
            try:
                flight_id = int(id_entry.get())
                new_flight_no = flight_no_entry.get().strip()
                new_status = status_combobox.get().strip()
                new_aircraft = aircraft_entry.get().strip()

                # Валидация
                if new_flight_no and len(new_flight_no) != 6:
                    messagebox.showerror("Ошибка", "Номер рейса должен содержать 6 символов")
                    return

                if new_aircraft and len(new_aircraft) != 3:
                    messagebox.showerror("Ошибка", "Код самолета должен содержать 3 символа")
                    return

                if self.controller.update_flight(
                    flight_id=flight_id,
                    flight_no=new_flight_no if new_flight_no else None,
                    status=new_status if new_status else None,
                    aircraft_code=new_aircraft if new_aircraft else None
                ):
                    messagebox.showinfo("Успех", "Рейс обновлен!")
                    self.refresh_data()
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось обновить рейс")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректный ID рейса")

        ttk.Button(dialog, text="Обновить", command=update).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)

    def show_delete_dialog(self):
        """Диалог удаления рейса"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Удаление рейса")
        dialog.geometry("300x150")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="ID рейса для удаления:").pack(pady=5)
        id_entry = ttk.Entry(dialog)
        id_entry.pack(pady=5)

        def delete():
            try:
                flight_id = int(id_entry.get())
                if messagebox.askyesno("Подтверждение",
                                       f"Вы уверены, что хотите удалить рейс {flight_id}?"):
                    if self.controller.delete_flight(flight_id):
                        messagebox.showinfo("Успех", "Рейс удален!")
                        self.refresh_data()
                        dialog.destroy()
                    else:
                        messagebox.showerror("Ошибка", "Не удалось удалить рейс")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректный ID рейса")

        ttk.Button(dialog, text="Удалить", command=delete).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)