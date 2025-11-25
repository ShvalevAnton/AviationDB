import tkinter as tk
from src.View.BaseView import BaseView
from tkinter import ttk, messagebox
import json


class AircraftView(BaseView):
    def setup_ui(self):
        """Настройка UI для самолетов с пагинацией"""
        # Заголовок
        title_label = ttk.Label(self.tab, text="Управление самолетами",
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
        columns = ('aircraft_code', 'model', 'range')
        self.tree = ttk.Treeview(self.tab, columns=columns, show='headings')

        # Настраиваем заголовки колонок
        self.tree.heading('aircraft_code', text='Код самолета')
        self.tree.heading('model', text='Модель')
        self.tree.heading('range', text='Дальность (км)')

        # Настраиваем ширину колонок
        self.tree.column('aircraft_code', width=100)
        self.tree.column('model', width=300)
        self.tree.column('range', width=120)

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
        aircrafts, total = self.controller.get_all_aircrafts_paginated(offset, limit)
        self.total_records = total

        for aircraft in aircrafts:
            # Форматируем JSON модель для отображения
            model_str = str(aircraft.model)[:200] if aircraft.model else "Нет данных"
            model_str = model_str.replace('{', '').replace('}', '').replace("'", "")


            self.tree.insert('', 'end', values=(
                aircraft.aircraft_code,
                model_str,
                aircraft.range
            ))

        # Обновляем элементы управления пагинацией
        self.update_pagination_controls()

    def show_create_dialog(self):
        """Диалог создания самолета"""
        fields = {
            'aircraft_code': {'label': 'Код самолета (3 символа):', 'type': 'entry'},
            'model_en': {'label': 'Название модели (английский):', 'type': 'entry'},
            'model_ru': {'label': 'Название модели (русский):', 'type': 'entry'},
            'range': {'label': 'Дальность полета (км):', 'type': 'entry'}
        }

        def create_callback(data):
            aircraft_code = data['aircraft_code'].upper()
            model_en = data['model_en'].strip()
            model_ru = data['model_ru'].strip()
            range_input = data['range']

            if len(aircraft_code) != 3:
                messagebox.showerror("Ошибка", "Код самолета должен содержать 3 символа")
                return

            if not model_en or not model_ru:
                messagebox.showerror("Ошибка", "Заполните оба названия модели")
                return

            # Создаем JSON из отдельных полей
            model_data = {
                "en": model_en,
                "ru": model_ru
            }

            try:
                aircraft_range = int(range_input)
                if aircraft_range <= 0:
                    messagebox.showerror("Ошибка", "Дальность должна быть больше 0")
                    return
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное число для дальности")
                return

            if self.controller.create_aircraft(aircraft_code, model_data, aircraft_range):
                messagebox.showinfo("Успех", "Самолет создан!")
                self.refresh_data()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать самолет")

        self.create_dialog("Создание самолета", fields, create_callback, "400x200")

    def show_find_dialog(self):
        """Диалог поиска самолета"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Поиск самолета")
        dialog.geometry("300x150")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="Код самолета:").pack(pady=5)
        code_entry = ttk.Entry(dialog)
        code_entry.pack(pady=5)

        def find():
            aircraft_code = code_entry.get().upper()
            aircraft = self.controller.find_aircraft(aircraft_code)

            if aircraft:
                # Парсим JSON данные модели
                model_en = aircraft.model.get('en', 'Нет данных') if aircraft.model else 'Нет данных'
                model_ru = aircraft.model.get('ru', 'Нет данных') if aircraft.model else 'Нет данных'

                result = f"Найден самолет:\n\n"
                result += f"Код: {aircraft.aircraft_code}\n"
                result += f"Модель (англ.): {model_en}\n"
                result += f"Модель (рус.): {model_ru}\n"
                result += f"Дальность: {aircraft.range} км"
                messagebox.showinfo("Результат поиска", result)
            else:
                messagebox.showinfo("Результат поиска", "Самолет не найден")

            dialog.destroy()

        ttk.Button(dialog, text="Найти", command=find).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)

    def show_update_dialog(self):
        """Диалог обновления самолета"""
        fields = {
            'aircraft_code': {'label': 'Код самолета для обновления:', 'type': 'entry'},
            'model_en': {'label': 'Новое название (английский, оставьте пустым чтобы не менять):', 'type': 'entry'},
            'model_ru': {'label': 'Новое название (русский, оставьте пустым чтобы не менять):', 'type': 'entry'},
            'range': {'label': 'Новая дальность (оставьте пустым чтобы не менять):', 'type': 'entry'}
        }

        def update_callback(data):
            aircraft_code = data['aircraft_code'].upper()
            model_en = data['model_en'].strip()
            model_ru = data['model_ru'].strip()
            range_input = data['range']

            model_data = None
            if model_en or model_ru:
                model_data = {}
                if model_en:
                    model_data["en"] = model_en
                if model_ru:
                    model_data["ru"] = model_ru

            aircraft_range = None
            if range_input:
                try:
                    aircraft_range = int(range_input)
                    if aircraft_range <= 0:
                        messagebox.showerror("Ошибка", "Дальность должна быть больше 0")
                        return
                except ValueError:
                    messagebox.showerror("Ошибка", "Введите корректное число для дальности")
                    return

            if self.controller.update_aircraft(aircraft_code, model_data, aircraft_range):
                messagebox.showinfo("Успех", "Самолет обновлен!")
                self.refresh_data()
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить самолет")

        self.create_dialog("Обновление самолета", fields, update_callback, "700x200")


    def show_delete_dialog(self):
        """Диалог удаления самолета"""
        dialog = tk.Toplevel(self.tab)
        dialog.title("Удаление самолета")
        dialog.geometry("300x150")
        dialog.transient(self.tab)
        dialog.grab_set()

        ttk.Label(dialog, text="Код самолета для удаления:").pack(pady=5)
        code_entry = ttk.Entry(dialog)
        code_entry.pack(pady=5)

        def delete():
            aircraft_code = code_entry.get().upper()
            if messagebox.askyesno("Подтверждение",
                                   f"Вы уверены, что хотите удалить самолет {aircraft_code}?"):
                if self.controller.delete_aircraft(aircraft_code):
                    messagebox.showinfo("Успех", "Самолет удален!")
                    self.refresh_data()
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось удалить самолет")

        ttk.Button(dialog, text="Удалить", command=delete).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

        # Центрируем диалоговое окно
        self.center_dialog(dialog)