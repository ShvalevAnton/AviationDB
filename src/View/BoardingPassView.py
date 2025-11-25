import tkinter as tk
import tkinter as tk
from tkinter import ttk, messagebox
from src.View.BaseView import BaseView


class BoardingPassView(BaseView):
    def setup_ui(self):
        """Настройка UI для посадочных талонов с пагинацией"""
        # Заголовок
        title_label = ttk.Label(self.tab, text="Управление посадочными талонами",
                                font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)

        # Фрейм для кнопок
        button_frame = ttk.Frame(self.tab)
        button_frame.pack(pady=10)

        # Кнопки управления
        buttons = [
            ("Показать все", self.refresh_data),
            ("Для рейса", self.show_by_flight_dialog),
            ("Создать", self.show_create_dialog),
            ("Найти по билету", self.show_find_dialog),
            ("Найти по посадке", self.show_find_by_boarding_dialog),
            ("Обновить место", self.show_update_seat_dialog),
            ("Обновить посадку", self.show_update_boarding_dialog),
            ("Удалить", self.show_delete_dialog),
            ("Занятые места", self.show_occupied_seats_dialog)
        ]

        # Создаем кнопки в две строки для лучшего отображения
        for i, (text, command) in enumerate(buttons[:5]):  # Первые 5 кнопок
            ttk.Button(button_frame, text=text, command=command).grid(
                row=0, column=i, padx=3, pady=3
            )

        for i, (text, command) in enumerate(buttons[5:]):  # Остальные кнопки
            ttk.Button(button_frame, text=text, command=command).grid(
                row=1, column=i, padx=3, pady=3
            )

        # Treeview
        columns = ('ticket_no', 'flight_id', 'boarding_no', 'seat_no')
        self.tree = ttk.Treeview(self.tab, columns=columns, show='headings')

        # Настраиваем заголовки колонок
        self.tree.heading('ticket_no', text='Номер билета')
        self.tree.heading('flight_id', text='ID рейса')
        self.tree.heading('boarding_no', text='Номер посадки')
        self.tree.heading('seat_no', text='Место')

        # Настраиваем ширину колонок
        self.tree.column('ticket_no', width=150)
        self.tree.column('flight_id', width=100)
        self.tree.column('boarding_no', width=120)
        self.tree.column('seat_no', width=80)

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
        boarding_passes, total = self.controller.get_all_boarding_passes_paginated(offset, limit)
        self.total_records = total

        for bp in boarding_passes:
            self.tree.insert('', 'end', values=(
                bp.ticket_no,
                bp.flight_id,
                bp.boarding_no,
                bp.seat_no
            ))

        # Обновляем элементы управления пагинацией
        self.update_pagination_controls()

    def show_create_dialog(self):
        """Диалог создания посадочного талона"""
        fields = {
            'ticket_no': {'label': 'Номер билета (13 символов):', 'type': 'entry'},
            'flight_id': {'label': 'ID рейса:', 'type': 'entry'},
            'seat_no': {'label': 'Номер места (например, 12A):', 'type': 'entry'}
        }

        def create_callback(data):
            ticket_no = data['ticket_no']
            flight_id_str = data['flight_id']
            seat_no = data['seat_no']

            if len(ticket_no) != 13:
                messagebox.showerror("Ошибка", "Номер билета должен содержать 13 символов")
                return

            try:
                flight_id = int(flight_id_str)
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректный ID рейса")
                return

            # Получаем следующий номер посадки
            boarding_no = self.controller.get_next_boarding_no(flight_id)

            if self.controller.create_boarding_pass(ticket_no, flight_id, boarding_no, seat_no):
                messagebox.showinfo("Успех", "Посадочный талон создан!")
                self.refresh_data()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать посадочный талон")

        self.create_dialog("Создание посадочного талона", fields, create_callback, "400x200")

    def show_find_dialog(self):
        """Диалог поиска посадочного талона по билету и рейсу"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Поиск посадочного талона")
        dialog.geometry("350x220")
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
            flight_id_str = flight_entry.get()

            try:
                flight_id = int(flight_id_str)
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректный ID рейса")
                return

            boarding_pass = self.controller.find_boarding_pass(ticket_no, flight_id)

            if boarding_pass:
                result = f"Найден посадочный талон:\n"
                result += f"Билет: {boarding_pass.ticket_no}\n"
                result += f"Рейс: {boarding_pass.flight_id}\n"
                result += f"Номер посадки: {boarding_pass.boarding_no}\n"
                result += f"Место: {boarding_pass.seat_no}"
                messagebox.showinfo("Результат поиска", result)
            else:
                messagebox.showinfo("Результат поиска", "Посадочный талон не найден")

            dialog.destroy()

        ttk.Button(dialog, text="Найти", command=find).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)

    def show_find_by_boarding_dialog(self):
        """Диалог поиска по номеру посадки"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Поиск по номеру посадки")
        dialog.geometry("300x220")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="ID рейса:").pack(pady=5)
        flight_entry = ttk.Entry(dialog)
        flight_entry.pack(pady=5)

        ttk.Label(dialog, text="Номер посадки:").pack(pady=5)
        boarding_entry = ttk.Entry(dialog)
        boarding_entry.pack(pady=5)

        def find():
            flight_id_str = flight_entry.get()
            boarding_no_str = boarding_entry.get()

            try:
                flight_id = int(flight_id_str)
                boarding_no = int(boarding_no_str)
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные числовые значения")
                return

            boarding_pass = self.controller.find_boarding_pass_by_boarding_no(flight_id, boarding_no)

            if boarding_pass:
                result = f"Найден посадочный талон:\n"
                result += f"Билет: {boarding_pass.ticket_no}\n"
                result += f"Рейс: {boarding_pass.flight_id}\n"
                result += f"Номер посадки: {boarding_pass.boarding_no}\n"
                result += f"Место: {boarding_pass.seat_no}"
                messagebox.showinfo("Результат поиска", result)
            else:
                messagebox.showinfo("Результат поиска", "Посадочный талон не найден")

            dialog.destroy()

        ttk.Button(dialog, text="Найти", command=find).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)

    def show_by_flight_dialog(self):
        """Диалог показа посадочные талоны для рейсу"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Показать посадочные талоны для рейса")
        dialog.geometry("300x150")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="ID рейса:").pack(pady=5)
        flight_entry = ttk.Entry(dialog)
        flight_entry.pack(pady=5)

        def show():
            flight_id_str = flight_entry.get()

            try:
                flight_id = int(flight_id_str)
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректный ID рейса")
                return

            # Очищаем таблицу
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Загружаем данные для конкретного рейса
            boarding_passes = self.controller.get_boarding_passes_by_flight(flight_id)

            if not boarding_passes:
                messagebox.showinfo("Информация", f"Посадочные талоны для рейсу {flight_id} не найдены")
                dialog.destroy()
                return

            for bp in boarding_passes:
                self.tree.insert('', 'end', values=(
                    bp.ticket_no,
                    bp.flight_id,
                    bp.boarding_no,
                    bp.seat_no
                ))

            messagebox.showinfo("Успех", f"Загружено {len(boarding_passes)} посадочных талонов для рейса {flight_id}")
            dialog.destroy()

        ttk.Button(dialog, text="Показать", command=show).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)

    def show_update_seat_dialog(self):
        """Диалог обновления места"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Обновление места")
        dialog.geometry("350x270")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="Номер билета:").pack(pady=5)
        ticket_entry = ttk.Entry(dialog)
        ticket_entry.pack(pady=5)

        ttk.Label(dialog, text="ID рейса:").pack(pady=5)
        flight_entry = ttk.Entry(dialog)
        flight_entry.pack(pady=5)

        ttk.Label(dialog, text="Новое место:").pack(pady=5)
        seat_entry = ttk.Entry(dialog)
        seat_entry.pack(pady=5)

        def update():
            ticket_no = ticket_entry.get()
            flight_id_str = flight_entry.get()
            new_seat = seat_entry.get()

            try:
                flight_id = int(flight_id_str)
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректный ID рейса")
                return

            if self.controller.update_boarding_pass_seat(ticket_no, flight_id, new_seat):
                messagebox.showinfo("Успех", "Место успешно обновлено!")
                self.refresh_data()
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить место")

        ttk.Button(dialog, text="Обновить", command=update).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)

    def show_update_boarding_dialog(self):
        """Диалог обновления номера посадки"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Обновление номера посадки")
        dialog.geometry("350x270")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="Номер билета:").pack(pady=5)
        ticket_entry = ttk.Entry(dialog)
        ticket_entry.pack(pady=5)

        ttk.Label(dialog, text="ID рейса:").pack(pady=5)
        flight_entry = ttk.Entry(dialog)
        flight_entry.pack(pady=5)

        ttk.Label(dialog, text="Новый номер посадки:").pack(pady=5)
        boarding_entry = ttk.Entry(dialog)
        boarding_entry.pack(pady=5)

        def update():
            ticket_no = ticket_entry.get()
            flight_id_str = flight_entry.get()
            boarding_no_str = boarding_entry.get()

            try:
                flight_id = int(flight_id_str)
                boarding_no = int(boarding_no_str)
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные числовые значения")
                return

            if self.controller.update_boarding_pass_number(ticket_no, flight_id, boarding_no):
                messagebox.showinfo("Успех", "Номер посадки успешно обновлен!")
                self.refresh_data()
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить номер посадки")

        ttk.Button(dialog, text="Обновить", command=update).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)

    def show_delete_dialog(self):
        """Диалог удаления посадочного талона"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Удаление посадочного талона")
        dialog.geometry("350x210")
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
            flight_id_str = flight_entry.get()

            try:
                flight_id = int(flight_id_str)
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректный ID рейса")
                return

            if messagebox.askyesno("Подтверждение",
                                   f"Удалить посадочный талон для билета {ticket_no} рейса {flight_id}?"):
                if self.controller.delete_boarding_pass(ticket_no, flight_id):
                    messagebox.showinfo("Успех", "Посадочный талон удален!")
                    self.refresh_data()
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось удалить посадочный талон")

        ttk.Button(dialog, text="Удалить", command=delete).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)

    def show_occupied_seats_dialog(self):
        """Диалог показа занятых мест"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Занятые места для рейса")
        dialog.geometry("300x180")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="ID рейса:").pack(pady=5)
        flight_entry = ttk.Entry(dialog)
        flight_entry.pack(pady=5)

        def show():
            flight_id_str = flight_entry.get()

            try:
                flight_id = int(flight_id_str)
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректный ID рейса")
                return

            occupied_seats = self.controller.get_occupied_seats(flight_id)

            if not occupied_seats:
                messagebox.showinfo("Информация", f"На рейсе {flight_id} нет занятых мест")
            else:
                seats_str = ", ".join(occupied_seats)
                messagebox.showinfo("Занятые места",
                                    f"Занятые места на рейсе {flight_id}:\n\n{seats_str}")

            dialog.destroy()

        ttk.Button(dialog, text="Показать", command=show).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)