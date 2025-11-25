import tkinter as tk
from tkinter import ttk, messagebox
import json


class BaseView:
    """Базовый класс для всех представлений с пагинацией"""

    def __init__(self, tab, controller, tab_name):
        self.tab = tab
        self.controller = controller
        self.tab_name = tab_name
        self.current_page = 1
        self.page_size = 50  # Количество записей на странице
        self.total_records = 0
        self.setup_ui()

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

    def setup_ui(self):
        """Базовая настройка UI (должна быть переопределена в дочерних классах)"""
        pass

    def setup_pagination_controls(self, parent_frame):
        """Создание элементов управления пагинацией"""
        pagination_frame = ttk.Frame(parent_frame)
        pagination_frame.pack(pady=5)

        # Кнопка "Первая"
        self.first_btn = ttk.Button(pagination_frame, text="<<",
                                    command=self.first_page, width=3)
        self.first_btn.pack(side=tk.LEFT, padx=2)

        # Кнопка "Предыдущая"
        self.prev_btn = ttk.Button(pagination_frame, text="<",
                                   command=self.prev_page, width=3)
        self.prev_btn.pack(side=tk.LEFT, padx=2)

        # Информация о странице
        self.page_label = ttk.Label(pagination_frame, text="Страница 1 из 1")
        self.page_label.pack(side=tk.LEFT, padx=10)

        # Кнопка "Следующая"
        self.next_btn = ttk.Button(pagination_frame, text=">",
                                   command=self.next_page, width=3)
        self.next_btn.pack(side=tk.LEFT, padx=2)

        # Кнопка "Последняя"
        self.last_btn = ttk.Button(pagination_frame, text=">>",
                                   command=self.last_page, width=3)
        self.last_btn.pack(side=tk.LEFT, padx=2)

        # Выбор размера страницы
        ttk.Label(pagination_frame, text="Записей на странице:").pack(side=tk.LEFT, padx=(20, 5))
        self.page_size_var = tk.StringVar(value=str(self.page_size))
        page_size_combo = ttk.Combobox(pagination_frame,
                                       textvariable=self.page_size_var,
                                       values=['10', '25', '50', '100', '200'],
                                       width=5, state='readonly')
        page_size_combo.pack(side=tk.LEFT, padx=5)
        page_size_combo.bind('<<ComboboxSelected>>', self.change_page_size)

        # Общее количество записей
        self.total_label = ttk.Label(pagination_frame, text="Всего: 0")
        self.total_label.pack(side=tk.LEFT, padx=20)

        return pagination_frame

    def update_pagination_controls(self):
        """Обновление состояния элементов управления пагинацией"""
        total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)

        # Обновляем информацию о странице
        self.page_label.config(text=f"Страница {self.current_page} из {total_pages}")
        self.total_label.config(text=f"Всего: {self.total_records}")

        # Обновляем состояние кнопок
        self.first_btn.config(state='normal' if self.current_page > 1 else 'disabled')
        self.prev_btn.config(state='normal' if self.current_page > 1 else 'disabled')
        self.next_btn.config(state='normal' if self.current_page < total_pages else 'disabled')
        self.last_btn.config(state='normal' if self.current_page < total_pages else 'disabled')

    def first_page(self):
        """Переход на первую страницу"""
        self.current_page = 1
        self.refresh_data()

    def prev_page(self):
        """Переход на предыдущую страницу"""
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_data()

    def next_page(self):
        """Переход на следующую страницу"""
        total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)
        if self.current_page < total_pages:
            self.current_page += 1
            self.refresh_data()

    def last_page(self):
        """Переход на последнюю страницу"""
        total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)
        self.current_page = total_pages
        self.refresh_data()

    def change_page_size(self, event=None):
        """Изменение количества записей на странице"""
        try:
            new_size = int(self.page_size_var.get())
            if new_size != self.page_size:
                self.page_size = new_size
                self.current_page = 1  # Сбрасываем на первую страницу
                self.refresh_data()
        except ValueError:
            pass

    def get_pagination_params(self):
        """Получение параметров пагинации для запроса"""
        offset = (self.current_page - 1) * self.page_size
        return offset, self.page_size

    def refresh_data(self):
        """Обновление данных (должен быть переопределен в дочерних классах)"""
        pass

    def create_dialog(self, title, fields, callback, size="500x400"):
        """Создание диалогового окна с полями ввода"""
        dialog = tk.Toplevel(self.tab)
        dialog.title(title)
        dialog.geometry(size)
        dialog.transient(self.tab)
        dialog.grab_set()

        entries = {}
        row = 0

        for field_name, field_config in fields.items():
            ttk.Label(dialog, text=field_config['label']).grid(row=row, column=0, sticky='w', padx=10, pady=5)

            if field_config['type'] == 'entry':
                entry = ttk.Entry(dialog, width=40)
                entry.grid(row=row, column=1, padx=10, pady=5, sticky='ew')
                entries[field_name] = entry

            elif field_config['type'] == 'combobox':
                combobox = ttk.Combobox(dialog, width=37, values=field_config.get('values', []))
                combobox.grid(row=row, column=1, padx=10, pady=5, sticky='ew')
                entries[field_name] = combobox

            elif field_config['type'] == 'text':
                text_widget = tk.Text(dialog, height=4, width=40)
                text_widget.grid(row=row, column=1, padx=10, pady=5, sticky='ew')
                entries[field_name] = text_widget

            row += 1

        def submit():
            data = {}
            for field_name, widget in entries.items():
                if isinstance(widget, (ttk.Entry, ttk.Combobox)):
                    data[field_name] = widget.get()
                elif isinstance(widget, tk.Text):
                    data[field_name] = widget.get('1.0', 'end-1c')
            callback(data)
            dialog.destroy()

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Создать", command=submit).pack(side='left', padx=10)
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side='left', padx=10)

        dialog.columnconfigure(1, weight=1)

        # ЦЕНТРИРУЕМ ДИАЛОГОВОЕ ОКНО
        self.center_dialog(dialog)