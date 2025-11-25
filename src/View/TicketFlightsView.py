# TicketFlightsView.py
import tkinter as tk
from tkinter import ttk, messagebox
from src.View.BaseView import BaseView


class TicketFlightsView(BaseView):
    def setup_ui(self):
        """Настройка UI для билетов на рейсы с пагинацией"""
        # Заголовок
        title_label = ttk.Label(self.tab, text="Управление билетами на рейсы",
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
        columns = ('ticket_no', 'flight_id', 'fare_conditions', 'amount')
        self.tree = ttk.Treeview(self.tab, columns=columns, show='headings')

        # Настраиваем заголовки колонок
        self.tree.heading('ticket_no', text='Номер билета')
        self.tree.heading('flight_id', text='ID рейса')
        self.tree.heading('fare_conditions', text='Класс обслуживания')
        self.tree.heading('amount', text='Стоимость')

        # Настраиваем ширину колонок
        self.tree.column('ticket_no', width=150)
        self.tree.column('flight_id', width=100)
        self.tree.column('fare_conditions', width=150)
        self.tree.column('amount', width=100)

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
        ticket_flights, total = self.controller.get_all_ticket_flights_paginated(offset, limit)
        self.total_records = total

        for tf in ticket_flights:
            self.tree.insert('', 'end', values=(
                tf.ticket_no,
                tf.flight_id,
                tf.fare_conditions,
                f"${tf.amount:.2f}"
            ))

        # Обновляем элементы управления пагинацией
        self.update_pagination_controls()

    def show_create_dialog(self):
        """Диалог создания билета на рейс"""
        fields = {
            'ticket_no': {'label': 'Номер билета (13 символов):', 'type': 'entry'},
            'flight_id': {'label': 'ID рейса:', 'type': 'entry'},
            'fare_conditions': {'label': 'Класс обслуживания:', 'type': 'entry'},
            'amount': {'label': 'Стоимость:', 'type': 'entry'}
        }

        def create_callback(data):
            ticket_no = data['ticket_no']
            flight_id = data['flight_id']
            fare_conditions = data['fare_conditions']
            amount = data['amount']

            if len(ticket_no) != 13:
                messagebox.showerror("Ошибка", "Номер билета должен содержать 13 символов")
                return

            try:
                flight_id = int(flight_id)
                amount = float(amount)

                if amount < 0:
                    messagebox.showerror("Ошибка", "Стоимость не может быть отрицательной")
                    return

                if self.controller.create_ticket_flight(ticket_no, flight_id, fare_conditions, amount):
                    messagebox.showinfo("Успех", "Билет на рейс создан!")
                    self.refresh_data()
                else:
                    messagebox.showerror("Ошибка", "Не удалось создать билет на рейс")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные данные (ID рейса - число, стоимость - число)")

        self.create_dialog("Создание билета на рейс", fields, create_callback)

    def show_find_dialog(self):
        """Диалог поиска билета на рейс"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Поиск билета на рейс")
        dialog.geometry("300x200")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="Номер билета:").pack(pady=5)
        ticket_entry = ttk.Entry(dialog)
        ticket_entry.pack(pady=5)

        ttk.Label(dialog, text="ID рейса:").pack(pady=5)
        flight_entry = ttk.Entry(dialog)
        flight_entry.pack(pady=5)

        def find():
            ticket_no = ticket_entry.get()
            try:
                flight_id = int(flight_entry.get())
                ticket_flight = self.controller.find_ticket_flight(ticket_no, flight_id)

                if ticket_flight:
                    result = f"Найден билет на рейс:\n"
                    result += f"Билет: {ticket_flight.ticket_no}\n"
                    result += f"Рейс: {ticket_flight.flight_id}\n"
                    result += f"Класс: {ticket_flight.fare_conditions}\n"
                    result += f"Стоимость: ${ticket_flight.amount:.2f}"
                    messagebox.showinfo("Результат поиска", result)
                else:
                    messagebox.showinfo("Результат поиска", "Билет на рейс не найден")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректный ID рейса")

            dialog.destroy()

        ttk.Button(dialog, text="Найти", command=find).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)

    def show_update_dialog(self):
        """Диалог обновления билета на рейс"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Обновление билета на рейс")
        dialog.geometry("300x200")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="Номер билета:").pack(pady=5)
        ticket_entry = ttk.Entry(dialog)
        ticket_entry.pack(pady=5)

        ttk.Label(dialog, text="ID рейса:").pack(pady=5)
        flight_entry = ttk.Entry(dialog)
        flight_entry.pack(pady=5)

        ttk.Label(dialog, text="Новый класс обслуживания:").pack(pady=5)
        fare_conditions_entry = ttk.Entry(dialog)
        fare_conditions_entry.pack(pady=5)

        ttk.Label(dialog, text="Новая стоимость:").pack(pady=5)
        amount_entry = ttk.Entry(dialog)
        amount_entry.pack(pady=5)

        def update():
            ticket_no = ticket_entry.get()
            flight_id = flight_entry.get()
            new_fare_conditions = fare_conditions_entry.get()
            new_amount = amount_entry.get()

            try:
                flight_id = int(flight_id) if flight_id else None
                amount = float(new_amount) if new_amount else None

                if self.controller.update_ticket_flight(ticket_no, flight_id, new_fare_conditions, amount):
                    messagebox.showinfo("Успех", "Билет на рейс обновлен!")
                    self.refresh_data()
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось обновить билет на рейс")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные данные")

        ttk.Button(dialog, text="Обновить", command=update).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)

    def show_delete_dialog(self):
        """Диалог удаления билета на рейс"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Удаление билета на рейс")
        dialog.geometry("300x150")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="Номер билета:").pack(pady=5)
        ticket_entry = ttk.Entry(dialog)
        ticket_entry.pack(pady=5)

        ttk.Label(dialog, text="ID рейса:").pack(pady=5)
        flight_entry = ttk.Entry(dialog)
        flight_entry.pack(pady=5)

        def delete():
            ticket_no = ticket_entry.get()
            try:
                flight_id = int(flight_entry.get())
                if messagebox.askyesno("Подтверждение",
                                       f"Вы уверены, что хотите удалить билет {ticket_no} на рейс {flight_id}?"):
                    if self.controller.delete_ticket_flight(ticket_no, flight_id):
                        messagebox.showinfo("Успех", "Билет на рейс удален!")
                        self.refresh_data()
                        dialog.destroy()
                    else:
                        messagebox.showerror("Ошибка", "Не удалось удалить билет на рейс")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректный ID рейса")

        ttk.Button(dialog, text="Удалить", command=delete).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)