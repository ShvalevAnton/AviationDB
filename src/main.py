import tkinter as tk
from tkinter import ttk, messagebox
from src.Models.database import PostgreSQLDatabase
from src.Controllers.BookingController import BookingController
from src.Controllers.AircraftController import AircraftController
from src.Controllers.AirportsDataController import AirportController
from src.Controllers.BoardingPassesController import BoardingPassController
from src.Controllers.FlightsController import FlightController
from src.Controllers.SeatsController import SeatController
from src.Controllers.TicketFlightsController import TicketFlightsController
from src.Controllers.TicketsController import TicketsController
from src.View.MainView import MainView


class DatabaseConnectionDialog:
    """Диалоговое окно для подключения к базе данных"""

    def __init__(self):
        self.result = None

        # Создаем отдельное окно для диалога подключения
        self.dialog = tk.Tk()
        self.dialog.title("Подключение к базе данных")
        self.dialog.geometry("300x250")
        self.dialog.resizable(False, False)

        # Центрирование диалога на экране
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - self.dialog.winfo_reqwidth()) // 2
        y = (self.dialog.winfo_screenheight() - self.dialog.winfo_reqheight()) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self.create_widgets()

    def create_widgets(self):
        """Создание элементов интерфейса"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Поля для ввода данных
        ttk.Label(main_frame, text="База данных:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.database_entry = ttk.Entry(main_frame, width=25)
        self.database_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.database_entry.insert(0, "demo")

        ttk.Label(main_frame, text="Пользователь:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.user_entry = ttk.Entry(main_frame, width=25)
        self.user_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.user_entry.insert(0, "anton")

        ttk.Label(main_frame, text="Пароль:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(main_frame, width=25, show="*")
        self.password_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.password_entry.insert(0, "q1")

        ttk.Label(main_frame, text="Хост:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.host_entry = ttk.Entry(main_frame, width=25)
        self.host_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.host_entry.insert(0, "127.0.0.1")

        ttk.Label(main_frame, text="Порт:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.port_entry = ttk.Entry(main_frame, width=25)
        self.port_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.port_entry.insert(0, "5432")

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=15)

        ttk.Button(button_frame, text="Подключиться",
                   command=self.on_connect).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена",
                   command=self.on_cancel).pack(side=tk.LEFT, padx=5)

        # Настройка расширения колонок
        main_frame.columnconfigure(1, weight=1)

        # Установка фокуса на первое поле
        self.database_entry.focus()

    def on_connect(self):
        """Обработчик нажатия кнопки подключения"""
        database = self.database_entry.get()
        user = self.user_entry.get()
        password = self.password_entry.get()
        host = self.host_entry.get()
        port = self.port_entry.get()

        if not all([database, user, host, port]):
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
            return

        self.result = (database, user, password, host, port)
        self.dialog.quit()
        self.dialog.destroy()

    def on_cancel(self):
        """Обработчик нажатия кнопки отмены"""
        self.result = None
        self.dialog.quit()
        self.dialog.destroy()

    def show(self):
        """Показать диалог и вернуть результат"""
        self.dialog.mainloop()
        return self.result


class MainController:
    """Главный контроллер для объединения функциональности"""

    def __init__(self, db):
        self.booking_controller = BookingController(db)
        self.aircraft_controller = AircraftController(db)
        self.airport_controller = AirportController(db)
        self.boarding_pass_controller = BoardingPassController(db)
        self.flights_controller = FlightController(db)
        self.seats_controller = SeatController(db)
        self.ticket_flights_controller = TicketFlightsController(db)
        self.tickets_controller = TicketsController(db)


def main():
    # Сначала показываем диалог подключения к БД как отдельное приложение
    connection_dialog = DatabaseConnectionDialog()
    connection_params = connection_dialog.show()

    if connection_params is None:
        print("Подключение отменено пользователем")
        return

    # Создаем подключение к БД с введенными параметрами
    database, user, password, host, port = connection_params
    db = PostgreSQLDatabase(database, user, password, host, port)

    if db.connect():
        # Создаем главное окно приложения
        root = tk.Tk()
        root.title("Авиабилеты")

        # Создаем главный контроллер
        main_controller = MainController(db)

        # Создаем представление
        view = MainView(root,
                        main_controller.booking_controller,
                        main_controller.aircraft_controller,
                        main_controller.airport_controller,
                        main_controller.boarding_pass_controller,
                        main_controller.flights_controller,
                        main_controller.seats_controller,
                        main_controller.ticket_flights_controller,
                        main_controller.tickets_controller)

        # Запускаем главный цикл
        root.mainloop()

        # Закрываем соединение с БД при выходе
        db.disconnect()
    else:
        print("Не удалось подключиться к базе данных")
        messagebox.showerror("Ошибка", "Не удалось подключиться к базе данных")


if __name__ == "__main__":
    main()