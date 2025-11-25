# TicketsView.py
import tkinter as tk
from tkinter import ttk, messagebox
from src.View.BaseView import BaseView


class TicketsView(BaseView):
    def setup_ui(self):
        """Настройка UI для билетов с пагинацией"""
        # Заголовок
        title_label = ttk.Label(self.tab, text="Управление билетами",
                                font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)

        # Фрейм для кнопок
        button_frame = ttk.Frame(self.tab)
        button_frame.pack(pady=10)

        # Кнопки управления
        buttons = [
            ("Показать все", self.refresh_data),
            ("Создать", self.show_create_dialog),
            ("Найти по номеру", self.show_find_dialog),
            ("Обновить", self.show_update_dialog),
            ("Удалить", self.show_delete_dialog)
        ]

        for i, (text, command) in enumerate(buttons):
            ttk.Button(button_frame, text=text, command=command).grid(
                row=0, column=i, padx=5, pady=5
            )

        # Treeview
        columns = ('ticket_no', 'book_ref', 'passenger_id', 'passenger_name', 'contact_data')
        self.tree = ttk.Treeview(self.tab, columns=columns, show='headings')

        # Настраиваем заголовки колонок
        self.tree.heading('ticket_no', text='Номер билета')
        self.tree.heading('book_ref', text='Номер брони')
        self.tree.heading('passenger_id', text='ID пассажира')
        self.tree.heading('passenger_name', text='Имя пассажира')
        self.tree.heading('contact_data', text='Контактные данные')

        # Настраиваем ширину колонок
        self.tree.column('ticket_no', width=150)
        self.tree.column('book_ref', width=100)
        self.tree.column('passenger_id', width=120)
        self.tree.column('passenger_name', width=150)
        self.tree.column('contact_data', width=400)

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
        result = self.controller.get_all_tickets_paginated(offset, limit)
        tickets = result['tickets']
        self.total_records = result['total_count']

        for ticket in tickets:
            contact_info = str(ticket.contact_data)[:200] if ticket.contact_data else "Нет данных"
            contact_info = contact_info.replace('{', '').replace('}', '').replace("'", "")
            self.tree.insert('', 'end', values=(
                ticket.ticket_no,
                ticket.book_ref,
                ticket.passenger_id,
                ticket.passenger_name,
                contact_info
            ))

        # Обновляем элементы управления пагинацией
        self.update_pagination_controls()

    def show_create_dialog(self):
        """Диалог создания билета"""
        fields = {
            'ticket_no': {'label': 'Номер билета (13 символов):', 'type': 'entry'},
            'book_ref': {'label': 'Номер брони (6 символов):', 'type': 'entry'},
            'passenger_id': {'label': 'ID пассажира:', 'type': 'entry'},
            'passenger_name': {'label': 'Имя пассажира:', 'type': 'entry'},
            'email': {'label': 'Email:', 'type': 'entry'},
            'phone': {'label': 'Телефон:', 'type': 'entry'}
        }

        def create_callback(data):
            ticket_no = data['ticket_no']
            book_ref = data['book_ref']
            passenger_id = data['passenger_id']
            passenger_name = data['passenger_name']
            email = data['email'].strip()
            phone = data['phone'].strip()

            if len(ticket_no) != 13:
                messagebox.showerror("Ошибка", "Номер билета должен содержать 13 символов")
                return

            if len(book_ref) != 6:
                messagebox.showerror("Ошибка", "Номер брони должен содержать 6 символов")
                return

            # Проверка email
            if email and '@' not in email:
                messagebox.showerror("Ошибка", "Введите корректный email адрес")
                return

            # Проверка телефона (только цифры, минимум 10 символов)
            if phone and (not phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')',
                                                                                                                '').isdigit() or len(
                    phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')',
                                                                                                      '')) < 10):
                messagebox.showerror("Ошибка", "Введите корректный номер телефона (минимум 10 цифр)")
                return

            # Создаем JSON из отдельных полей
            contact_data = {}
            if email:
                contact_data["email"] = email
            if phone:
                contact_data["phone"] = phone

            if self.controller.create_ticket(ticket_no, book_ref, passenger_id, passenger_name,
                                             contact_data if contact_data else None):
                messagebox.showinfo("Успех", "Билет создан!")
                self.refresh_data()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать билет")

        self.create_dialog("Создание билета", fields, create_callback, "600x250")

    def show_find_dialog(self):
        """Диалог поиска билета по номеру"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Поиск билета по номеру")
        dialog.geometry("300x150")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="Номер билета (13 символов):").pack(pady=5)
        ticket_entry = ttk.Entry(dialog)
        ticket_entry.pack(pady=5)

        def find():
            ticket_no = ticket_entry.get()
            ticket = self.controller.find_ticket(ticket_no)

            if ticket:
                # Парсим JSON данные контактной информации
                email = ticket.contact_data.get('email', 'Нет данных') if ticket.contact_data else 'Нет данных'
                phone = ticket.contact_data.get('phone', 'Нет данных') if ticket.contact_data else 'Нет данных'

                result = f"Найден билет:\n\n"
                result += f"Билет: {ticket.ticket_no}\n"
                result += f"Бронирование: {ticket.book_ref}\n"
                result += f"Пассажир: {ticket.passenger_name}\n"
                result += f"ID пассажира: {ticket.passenger_id}\n"
                result += f"Email: {email}\n"
                result += f"Телефон: {phone}"
                messagebox.showinfo("Результат поиска", result)
            else:
                messagebox.showinfo("Результат поиска", "Билет не найден")

            dialog.destroy()

        ttk.Button(dialog, text="Найти", command=find).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)

    def show_update_dialog(self):
        """Диалог обновления билета"""
        fields = {
            'ticket_no': {'label': 'Номер билета для обновления (13 символов):', 'type': 'entry'},
            'passenger_name': {'label': 'Новое имя пассажира (оставьте пустым чтобы не менять):', 'type': 'entry'},
            'passenger_id': {'label': 'Новый ID пассажира (оставьте пустым чтобы не менять):', 'type': 'entry'},
            'email': {'label': 'Новый email (оставьте пустым чтобы не менять):', 'type': 'entry'},
            'phone': {'label': 'Новый телефон (оставьте пустым чтобы не менять):', 'type': 'entry'}
        }

        def update_callback(data):
            ticket_no = data['ticket_no']
            passenger_name = data['passenger_name'].strip()
            passenger_id = data['passenger_id'].strip()
            email = data['email'].strip()
            phone = data['phone'].strip()

            # Проверка email
            if email and '@' not in email:
                messagebox.showerror("Ошибка", "Введите корректный email адрес")
                return

            # Проверка телефона (только цифры, минимум 10 символов)
            if phone and (not phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')',
                                                                                                                '').isdigit() or len(
                    phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')) < 10):
                messagebox.showerror("Ошибка", "Введите корректный номер телефона (минимум 10 цифр)")
                return

            # Подготавливаем данные для обновления
            new_passenger_name = passenger_name if passenger_name else None
            new_passenger_id = passenger_id if passenger_id else None

            contact_data = None
            if email or phone:
                contact_data = {}
                if email:
                    contact_data["email"] = email
                if phone:
                    contact_data["phone"] = phone

            if self.controller.update_ticket(ticket_no, new_passenger_name, new_passenger_id, contact_data):
                messagebox.showinfo("Успех", "Билет обновлен!")
                self.refresh_data()
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить билет")

        self.create_dialog("Обновление билета", fields, update_callback, "600x250")

    def show_delete_dialog(self):
        """Диалог удаления билета"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Удаление билета")
        dialog.geometry("300x150")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="Номер билета:").pack(pady=5)
        ticket_entry = ttk.Entry(dialog)
        ticket_entry.pack(pady=5)

        def delete():
            ticket_no = ticket_entry.get()
            if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить билет {ticket_no}?"):
                if self.controller.delete_ticket(ticket_no):
                    messagebox.showinfo("Успех", "Билет удален!")
                    self.refresh_data()
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось удалить билет")

        ttk.Button(dialog, text="Удалить", command=delete).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)