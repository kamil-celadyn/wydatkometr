# Importy bibliotek:
import pandas as pd  # do manipulacji danymi (DataFrame)
import tkinter as tk  # główna biblioteka GUI
from tkinter import filedialog, ttk, messagebox  # elementy GUI: przyciski, komunikaty itp.
import matplotlib.pyplot as plt  # do tworzenia wykresów
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # do osadzania wykresów matplotlib w tkinter

# Klasa główna aplikacji
class WydatkiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💰 Wydatkometr 2.0 - Analiza Boxplot")
        self.df = pd.DataFrame(columns=["Data", "Kategoria", "Kwota"])  # inicjalizacja pustego DataFrame z trzema kolumnami

        # Sekcja GUI - górny pasek przycisków
        top_frame = ttk.Frame(root)
        top_frame.pack(pady=10)

        # Trzy przyciski funkcyjne
        ttk.Button(top_frame, text="📂 Wczytaj CSV", command=self.load_data).grid(row=0, column=0, padx=5)
        ttk.Button(top_frame, text="💾 Zapisz CSV", command=self.save_data).grid(row=0, column=1, padx=5)
        ttk.Button(top_frame, text="📊 Generuj Boxplot", command=self.generate_plot).grid(row=0, column=2, padx=5)

        # Wyświetlanie danych w tabeli (Treeview)
        self.tree = ttk.Treeview(root, columns=("Data", "Kategoria", "Kwota"), show='headings', height=8)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center')
        self.tree.pack(pady=5)

        # Formularz do ręcznego dodawania wydatków
        form_frame = ttk.LabelFrame(root, text="➕ Dodaj wydatek")
        form_frame.pack(pady=10)

        # Pola formularza: data, kategoria, kwota
        ttk.Label(form_frame, text="Data (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=2)
        self.entry_date = ttk.Entry(form_frame)
        self.entry_date.grid(row=0, column=1, padx=5)

        ttk.Label(form_frame, text="Kategoria:").grid(row=1, column=0, padx=5, pady=2)
        self.entry_category = ttk.Entry(form_frame)
        self.entry_category.grid(row=1, column=1, padx=5)

        ttk.Label(form_frame, text="Kwota:").grid(row=2, column=0, padx=5, pady=2)
        self.entry_amount = ttk.Entry(form_frame)
        self.entry_amount.grid(row=2, column=1, padx=5)

        # Przycisk do dodania rekordu
        ttk.Button(form_frame, text="Dodaj", command=self.add_record).grid(row=3, column=0, columnspan=2, pady=5)

        # Lista rozwijana do wyboru kategorii dla wykresu
        self.category_var = tk.StringVar()
        self.category_menu = ttk.Combobox(root, textvariable=self.category_var, state="readonly")
        self.category_menu.pack(pady=5)

        # Miejsce na wykres (Canvas)
        self.canvas = None

    # Funkcja wczytywania danych z pliku CSV
    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.df = pd.read_csv(file_path)
            self.refresh_table()
            self.update_categories()

    # Funkcja zapisu danych do CSV
    def save_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv")
        if file_path:
            self.df.to_csv(file_path, index=False)
            messagebox.showinfo("Zapisano", "Dane zapisane pomyślnie!")

    # Odświeżenie tabeli po dodaniu lub załadowaniu danych
    def refresh_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for _, row in self.df.iterrows():
            self.tree.insert("", tk.END, values=list(row))

    # Aktualizacja dostępnych kategorii do wyboru w comboboxie
    def update_categories(self):
        categories = self.df["Kategoria"].unique().tolist()
        self.category_menu["values"] = categories
        if categories:
            self.category_menu.set(categories[0])  # ustaw pierwszą kategorię domyślnie

    # Dodanie nowego rekordu z formularza
    def add_record(self):
        date = self.entry_date.get()
        category = self.entry_category.get()
        amount = self.entry_amount.get()
        try:
            amount = float(amount)  # sprawdzenie, czy kwota jest liczbą
            new_row = pd.DataFrame([[date, category, amount]], columns=["Data", "Kategoria", "Kwota"])
            self.df = pd.concat([self.df, new_row], ignore_index=True)
            self.refresh_table()
            self.update_categories()
            # Czyszczenie pól formularza
            self.entry_date.delete(0, tk.END)
            self.entry_category.delete(0, tk.END)
            self.entry_amount.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Błąd", "Podaj poprawną kwotę!")

    # Generowanie wykresu boxplot dla wybranej kategorii
    def generate_plot(self):
        if self.df.empty:
            return  # brak danych

        selected_category = self.category_var.get()
        if selected_category not in self.df["Kategoria"].unique():
            return  # nieprawidłowa kategoria

        # Filtrowanie danych dla danej kategorii
        filtered = self.df[self.df["Kategoria"] == selected_category]

        # Tworzenie wykresu boxplot
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.boxplot(filtered["Kwota"])
        ax.set_title(f"Boxplot - {selected_category}")
        ax.set_ylabel("Kwota [PLN]")

        # Usuwanie starego wykresu, jeśli istnieje
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        # Osadzenie nowego wykresu w GUI
        self.canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

# Uruchomienie aplikacji
if __name__ == "__main__":
    root = tk.Tk()
    app = WydatkiApp(root)
    root.mainloop()