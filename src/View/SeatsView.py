import tkinter as tk
from src.View.BaseView import BaseView
from tkinter import ttk, messagebox


class SeatsView(BaseView):
    def setup_ui(self):
        """Настройка UI для мест с пагинацией"""
        # Заголовок
        title_label = ttk.Label(self.tab, text="Управление местами в самолетах",
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
        columns = ('aircraft_code', 'seat_no', 'fare_conditions')
        self.tree = ttk.Treeview(self.tab, columns=columns, show='headings')

        # Настраиваем заголовки колонок
        self.tree.heading('aircraft_code', text='Код самолета')
        self.tree.heading('seat_no', text='Номер места')
        self.tree.heading('fare_conditions', text='Класс обслуживания')

        # Настраиваем ширину колонок
        self.tree.column('aircraft_code', width=120)
        self.tree.column('seat_no', width=120)
        self.tree.column('fare_conditions', width=150)

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
        seats, total = self.controller.get_all_seats_paginated(offset, limit)
        self.total_records = total

        for seat in seats:
            self.tree.insert('', 'end', values=(
                seat.aircraft_code,
                seat.seat_no,
                seat.fare_conditions
            ))

        # Обновляем элементы управления пагинацией
        self.update_pagination_controls()

    def show_create_dialog(self):
        """Диалог создания места"""
        fields = {
            'aircraft_code': {'label': 'Код самолета (3 символа):', 'type': 'entry'},
            'seat_no': {'label': 'Номер места:', 'type': 'entry'},
            'fare_conditions': {'label': 'Класс обслуживания:', 'type': 'combobox', 'values': ['Economy', 'Comfort', 'Business']}
        }

        def create_callback(data):
            # Валидация данных
            if len(data['aircraft_code']) != 3:
                messagebox.showerror("Ошибка", "Код самолета должен содержать 3 символа")
                return

            if not data['seat_no']:
                messagebox.showerror("Ошибка", "Номер места обязателен для заполнения")
                return

            if not data['fare_conditions']:
                messagebox.showerror("Ошибка", "Класс обслуживания обязателен для заполнения")
                return

            if self.controller.create_seat(data['aircraft_code'], data['seat_no'], data['fare_conditions']):
                messagebox.showinfo("Успех", "Место создано!")
                self.refresh_data()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать место")

        self.create_dialog("Создание места", fields, create_callback, "400x170")

    def show_find_dialog(self):
        """Диалог поиска места"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Поиск места")
        dialog.geometry("300x210")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="Код самолета:").pack(pady=5)
        aircraft_entry = ttk.Entry(dialog)
        aircraft_entry.pack(pady=5)

        ttk.Label(dialog, text="Номер места:").pack(pady=5)
        seat_entry = ttk.Entry(dialog)
        seat_entry.pack(pady=5)

        def find():
            aircraft_code = aircraft_entry.get()
            seat_no = seat_entry.get()

            if not aircraft_code or not seat_no:
                messagebox.showwarning("Предупреждение", "Заполните все поля")
                return

            seat = self.controller.find_seat(aircraft_code, seat_no)

            if seat:
                result = f"Найдено место:\n"
                result += f"Самолет: {seat.aircraft_code}\n"
                result += f"Место: {seat.seat_no}\n"
                result += f"Класс: {seat.fare_conditions}"
                messagebox.showinfo("Результат поиска", result)
            else:
                messagebox.showinfo("Результат поиска", "Место не найдено")

            dialog.destroy()

        ttk.Button(dialog, text="Найти", command=find).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)

    def show_update_dialog(self):
        """Диалог обновления места"""
        fields = {
            'aircraft_code': {'label': 'Код самолета:', 'type': 'entry'},
            'seat_no': {'label': 'Номер места:', 'type': 'entry'},
            'fare_conditions': {'label': 'Новый класс обслуживания:', 'type': 'combobox', 'values': ['Economy', 'Comfort', 'Business']}
        }

        def update_callback(data):
            aircraft_code = data['aircraft_code']
            seat_no = data['seat_no']
            new_fare_conditions = data['fare_conditions']

            if not aircraft_code or not seat_no:
                messagebox.showwarning("Предупреждение", "Заполните код самолета и номер места")
                return

            if not new_fare_conditions:
                messagebox.showwarning("Предупреждение", "Выберите класс обслуживания")
                return

            if self.controller.update_seat(aircraft_code, seat_no, new_fare_conditions):
                messagebox.showinfo("Успех", "Место обновлено!")
                self.refresh_data()
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить место")

        self.create_dialog("Обновление места", fields, update_callback, "400x170")


    def show_delete_dialog(self):
        """Диалог удаления места"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Удаление места")
        dialog.geometry("300x220")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="Код самолета:").pack(pady=5)
        aircraft_entry = ttk.Entry(dialog)
        aircraft_entry.pack(pady=5)

        ttk.Label(dialog, text="Номер места:").pack(pady=5)
        seat_entry = ttk.Entry(dialog)
        seat_entry.pack(pady=5)

        def delete():
            aircraft_code = aircraft_entry.get()
            seat_no = seat_entry.get()

            if not aircraft_code or not seat_no:
                messagebox.showwarning("Предупреждение", "Заполните все поля")
                return

            if messagebox.askyesno("Подтверждение",
                                   f"Удалить место {seat_no} для самолета {aircraft_code}?"):
                if self.controller.delete_seat(aircraft_code, seat_no):
                    messagebox.showinfo("Успех", "Место удалено!")
                    self.refresh_data()
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось удалить место")

        ttk.Button(dialog, text="Удалить", command=delete).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)


