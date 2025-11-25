import tkinter as tk
from src.View.BaseView import BaseView
from tkinter import ttk, messagebox
from datetime import datetime


class BookingView(BaseView):
    def setup_ui(self):
        """Настройка UI для бронирований с пагинацией"""
        # Заголовок
        title_label = ttk.Label(self.tab, text="Управление бронированиями",
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
        columns = ('book_ref', 'book_date', 'total_amount')
        self.tree = ttk.Treeview(self.tab, columns=columns, show='headings')

        # Настраиваем заголовки колонок
        self.tree.heading('book_ref', text='Номер брони')
        self.tree.heading('book_date', text='Дата бронирования')
        self.tree.heading('total_amount', text='Общая сумма')

        # Настраиваем ширину колонок
        self.tree.column('book_ref', width=120)
        self.tree.column('book_date', width=200)
        self.tree.column('total_amount', width=120)

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
        bookings, total = self.controller.get_all_bookings_paginated(offset, limit)
        self.total_records = total

        for booking in bookings:
            formatted_date = booking.book_date.strftime("%Y-%m-%d %H:%M:%S")
            self.tree.insert('', 'end', values=(
                booking.book_ref,
                formatted_date,
                f"${booking.total_amount:.2f}"
            ))

        # Обновляем элементы управления пагинацией
        self.update_pagination_controls()

    def show_create_dialog(self):
        """Диалог создания бронирования"""
        fields = {
            'book_ref': {'label': 'Номер брони (6 символов):', 'type': 'entry'},
            'total_amount': {'label': 'Сумма:', 'type': 'entry'}
        }

        def create_callback(data):
            book_ref = data['book_ref']
            amount = data['total_amount']

            if len(book_ref) != 6:
                messagebox.showerror("Ошибка", "Номер брони должен содержать 6 символов")
                return

            try:
                total_amount = float(amount)
                if self.controller.create_booking(book_ref, total_amount):
                    messagebox.showinfo("Успех", "Бронирование создано!")
                    self.refresh_data()
                else:
                    messagebox.showerror("Ошибка", "Не удалось создать бронирование")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректную сумму")

        self.create_dialog("Создание бронирования", fields, create_callback, "400x130")

    def show_find_dialog(self):
        """Диалог поиска бронирования"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Поиск бронирования")
        dialog.geometry("300x150")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="Номер брони:").pack(pady=5)
        ref_entry = ttk.Entry(dialog)
        ref_entry.pack(pady=5)

        def find():
            book_ref = ref_entry.get()
            booking = self.controller.find_booking(book_ref)

            if booking:
                result = f"Найдено бронирование:\n"
                result += f"Номер: {booking.book_ref}\n"
                result += f"Дата: {booking.book_date}\n"
                result += f"Сумма: ${booking.total_amount:.2f}"
                messagebox.showinfo("Результат поиска", result)
            else:
                messagebox.showinfo("Результат поиска", "Бронирование не найдено")

            dialog.destroy()

        ttk.Button(dialog, text="Найти", command=find).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)

    def show_update_dialog(self):
        """Диалог обновления бронирования"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Обновление бронирования")
        dialog.geometry("300x200")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="Номер брони для обновления:").pack(pady=5)
        ref_entry = ttk.Entry(dialog)
        ref_entry.pack(pady=5)

        ttk.Label(dialog, text="Новая сумма:").pack(pady=5)
        amount_entry = ttk.Entry(dialog)
        amount_entry.pack(pady=5)

        def update():
            book_ref = ref_entry.get()
            new_amount = amount_entry.get()

            try:
                total_amount = float(new_amount) if new_amount else None
                if self.controller.update_booking(book_ref, total_amount):
                    messagebox.showinfo("Успех", "Бронирование обновлено!")
                    self.refresh_data()
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось обновить бронирование")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректную сумму")

        ttk.Button(dialog, text="Обновить", command=update).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)

    def show_delete_dialog(self):
        """Диалог удаления бронирования"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Удаление бронирования")
        dialog.geometry("300x150")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="Номер брони для удаления:").pack(pady=5)
        ref_entry = ttk.Entry(dialog)
        ref_entry.pack(pady=5)

        def delete():
            book_ref = ref_entry.get()
            if messagebox.askyesno("Подтверждение",
                                   f"Вы уверены, что хотите удалить бронирование {book_ref}?"):
                if self.controller.delete_booking(book_ref):
                    messagebox.showinfo("Успех", "Бронирование удалено!")
                    self.refresh_data()
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось удалить бронирование")

        ttk.Button(dialog, text="Удалить", command=delete).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)