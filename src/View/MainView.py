from tkinter import ttk
from src.View.BookingView import BookingView
from src.View.AircraftView import AircraftView
from src.View.AirportView import AirportView
from src.View.BoardingPassView import BoardingPassView
from src.View.FlightsView import FlightsView
from src.View.SeatsView import SeatsView
from src.View.TicketFlightsView import TicketFlightsView
from src.View.TicketsView import TicketsView



class MainView:
    def __init__(self, root, booking_controller, aircraft_controller, airport_controller, boarding_pass_controller, flights_controller
                 , seats_controller, ticket_flights_controller, tickets_controller):
        self.root = root
        self.booking_controller = booking_controller
        self.aircraft_controller = aircraft_controller
        self.airport_controller = airport_controller
        self.boarding_pass_controller = boarding_pass_controller
        self.flights_controller = flights_controller
        self.seats_controller = seats_controller
        self.ticket_flights_controller = ticket_flights_controller
        self.tickets_controller = tickets_controller
        self.views = {}  # Словарь для хранения представлений
        self.setup_ui()

    def setup_ui(self):
        """Настройка главного UI с вкладками"""
        self.root.title("Авиационная система управления")
        #self.root.geometry("1200x800")

        # Центрируем окно
        self.center_window()

        # Создаем Notebook (вкладки)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Создаем вкладки и соответствующие представления
        self.create_tab("Бронирования", BookingView, self.booking_controller)
        self.create_tab("Самолеты", AircraftView, self.aircraft_controller)
        self.create_tab("Аэропорты", AirportView, self.airport_controller)
        self.create_tab("Посадочные талоны", BoardingPassView, self.boarding_pass_controller)
        self.create_tab("Рейсы", FlightsView, self.flights_controller)
        self.create_tab("Места", SeatsView, self.seats_controller)
        #self.create_tab("Билеты и рейсы", TicketFlightsView, self.ticket_flights_controller)
        self.create_tab("Билеты", TicketsView, self.tickets_controller)


    def create_tab(self, tab_name, view_class, controller):
        """Создание новой вкладки с представлением"""
        # Создаем фрейм для вкладки
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=tab_name)

        # Создаем представление для этой вкладки
        view = view_class(tab, controller, tab_name)
        self.views[tab_name] = view

        return tab

    def add_new_tab(self, tab_name, view_class, controller):
        """Метод для легкого добавления новых вкладок"""
        return self.create_tab(tab_name, view_class, controller)

    def center_window(self):
        """Размещение окна по центру экрана (альтернативная реализация)"""
        # Устанавливаем фиксированные размеры окна
        window_width = 1200
        window_height = 800

        # Получаем размеры экрана
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Вычисляем позицию для центрирования
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Устанавливаем размер и позицию окна
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")