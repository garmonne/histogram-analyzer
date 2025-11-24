import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
import customtkinter as ctk
import statistics
import numpy as np
from scipy.interpolate import make_interp_spline

# Функции для вывода статистики
def show_statistics(numbers):
    if not numbers:
        messagebox.showwarning("Нет данных", "Нет данных для вычисления статистики!")
        return

    mean = statistics.mean(numbers)  # Среднее значение
    median = statistics.median(numbers)  # Медиана
    stdev = statistics.stdev(numbers)  # Стандартное отклонение
    variance = statistics.variance(numbers)  # Дисперсия
    min_val = min(numbers)
    max_val = max(numbers)
    range_val = max_val - min_val
    count = len(numbers)

    stats = f"Статистика:\n" \
            f"Среднее: {mean:.2f}\n" \
            f"Медиана: {median}\n" \
            f"Стандартное отклонение: {stdev:.2f}\n" \
            f"Дисперсия: {variance:.2f}\n" \
            f"Минимум: {min_val}\n" \
            f"Максимум: {max_val}\n" \
            f"Размах: {range_val}\n" \
            f"Количество элементов: {count}"

    messagebox.showinfo("Статистика", stats)

# Функции для работы с гистограммой
def write_histogram_to_file(histogram, min_val, max_val, intervals, step, filename):
    try:
        with open(filename, "w") as file:
            max_height = max(histogram)
            file.write("Гистограмма (в виде символов):\n")

            for y in range(max_height, 0, -1):
                for count in histogram:
                    file.write(" * " if count >= y else "   ")
                file.write("\n")

            for i in range(intervals):
                lower_bound = min_val + int(i * step)
                upper_bound = min_val + int((i + 1) * step)
                file.write(f" {lower_bound}-{upper_bound} ")
            file.write("\n")
        print(f"Результаты сохранены в файл {filename}")
    except IOError:
        print("Не удалось открыть файл для записи!")



def plot_histogram(histogram, min_val, max_val, intervals, step, save_image=False):
    lower_bounds = [min_val + int(i * step) for i in range(intervals)]
    upper_bounds = [min_val + int((i + 1) * step) for i in range(intervals)]
    labels = [f"{lower_bounds[i]}-{upper_bounds[i]}" for i in range(intervals)]

    # Находим максимальное значение в гистограмме
    max_height = max(histogram)

    # Определяем диапазоны частот
    low_threshold = max_height / 3
    high_threshold = 2 * max_height / 3

    # Создаем список цветов для каждой колонки (3 цвета)
    colors = []
    for count in histogram:
        if count <= low_threshold:
            colors.append('lightblue')  # Малые значения
        elif count <= high_threshold:
            colors.append('yellow')     # Средние значения
        else:
            colors.append('darkred')    # Большие значения

    # Строим гистограмму
    plt.bar(labels, histogram, color=colors, edgecolor='black')
    plt.xlabel('Интервалы', fontsize=14)
    plt.ylabel('Частота', fontsize=14)
    plt.title('Гистограмма с линией распределения', fontsize=16)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Создаем массив индексов для столбцов
    x = np.arange(len(histogram))

    # Синусоидальная линия, которая будет "плавать" в зависимости от высоты столбцов
    sin_wave = np.sin(x) * max_height / 20 + max_height / 20  # Синусоида, которая масштабируется по высоте столбцов

    # Применим к синусоиде частоту столбцов
    sin_wave = sin_wave + np.array(histogram)  # Добавляем значения гистограммы (чтобы линия плавала по вершинам столбцов)

    # Интерполируем для сглаживания линии
    spline = make_interp_spline(x, sin_wave, k=3)  # k=3 для кубической интерполяции
    x_smooth = np.linspace(min(x), max(x), 500)  # Большее количество точек для сглаженной линии
    y_smooth = spline(x_smooth)

    # Строим плавную линию распределения
    plt.plot(x_smooth, y_smooth, color='green', linestyle='-', linewidth=2, label='Линия распределения')

    # Добавляем легенду
    plt.legend()

    # Сохраняем изображение, если требуется
    if save_image:
        image_filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg")])
        if image_filename:
            plt.savefig(image_filename)
            print(f"Гистограмма сохранена как изображение: {image_filename}")

    # Показываем гистограмму
    plt.show()


def build_histogram(numbers, intervals=10, save_image=False):
    if not numbers:
        print("Нет данных для построения гистограммы!")
        return

    min_val = min(numbers)
    max_val = max(numbers)
    range_val = max_val - min_val
    step = range_val / intervals

    histogram = [0] * intervals

    for x in numbers:
        index = min(int((x - min_val) / step), intervals - 1)
        histogram[index] += 1

    max_height = max(histogram)
    print("\nГистограмма (в виде координат):")
    print(f"Минимум: {min_val}, Максимум: {max_val}, Шаг: {step}")

    for y in range(max_height, 0, -1):
        for count in histogram:
            print(" * " if count >= y else "   ", end="")
        print()

    for i in range(intervals):
        lower_bound = min_val + int(i * step)
        upper_bound = min_val + int((i + 1) * step)
        print(f" {lower_bound}-{upper_bound} ", end="")
    print()

    write_histogram_to_file(histogram, min_val, max_val, intervals, step, "histogram_output.txt")
    plot_histogram(histogram, min_val, max_val, intervals, step, save_image)


# Функции для ввода данных
def input_from_file(filename):
    if not os.path.exists(filename):
        print("Не удалось открыть файл. Проверьте имя и расположение файла!")
        return []

    try:
        with open(filename, "r") as file:
            numbers = [int(line.strip()) for line in file]
            if not numbers:
                print("Файл пуст или не содержит данных.")
            return numbers
    except ValueError:
        print("Файл содержит некорректные данные.")
        return []

def generate_random_numbers(n, min_val, max_val):
    return [random.randint(min_val, max_val) for _ in range(n)]


# Графический интерфейс с customtkinter
class HistogramApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Гистограмма")
        self.root.geometry("1200x800")  # Устанавливаем размеры окна
        self.root.resizable(True, True)  # Делаем окно масштабируемым

        ctk.set_appearance_mode("dark")  # Устанавливаем темную тему
        ctk.set_default_color_theme("blue")  # Устанавливаем цветовую схему

        self.numbers = []
        self.intervals = 10  # Начальное значение интервалов
        self.language = 'ru'  # По умолчанию язык русский

        # Заголовок
        self.title_label = ctk.CTkLabel(root, text="Построение гистограммы", font=("Helvetica", 48))
        self.title_label.pack(pady=30)

        # Контейнер для кнопок ввода
        self.buttons_frame = ctk.CTkFrame(root)
        self.buttons_frame.pack(pady=30)

        self.button_file = ctk.CTkButton(self.buttons_frame, text="Ввод данных из файла", command=self.load_from_file, font=("Helvetica", 18), height=2, width=20)
        self.button_file.pack(side="left", padx=20)

        self.button_console = ctk.CTkButton(self.buttons_frame, text="Ввод данных из консоли", command=self.load_from_console, font=("Helvetica", 18), height=2, width=20)
        self.button_console.pack(side="left", padx=20)

        self.button_random = ctk.CTkButton(self.buttons_frame, text="Генерация случайных чисел", command=self.generate_random, font=("Helvetica", 18), height=2, width=20)
        self.button_random.pack(side="left", padx=20)

        # Кнопка статистики
        self.button_statistics = ctk.CTkButton(self.buttons_frame, text="Показать статистику", command=self.show_statistics, font=("Helvetica", 18), height=2, width=20)
        self.button_statistics.pack(side="left", padx=20)

        # Кнопка сохранения изображения
        self.button_save_image = ctk.CTkButton(root, text="Сохранить как изображение", command=self.save_image, font=("Helvetica", 18), height=2, width=20)
        self.button_save_image.place(x=950, y=100)

        

        # Кнопка справки
        self.help_button = ctk.CTkButton(root, text="?", command=self.show_help, font=("Helvetica", 18), height=2, width=5)
        self.help_button.place(x=1150, y=20)


       
       # Кнопки для изменения темы

        self.button_sun = ctk.CTkButton(root, text="Свет", command=self.set_light_theme, font=("Helvetica", 18), height=2, width=10)
        self.button_sun.place(x=50, y=600)

        self.button_moon = ctk.CTkButton(root, text="Тьма", command=self.set_dark_theme, font=("Helvetica", 18), height=2, width=10)
        self.button_moon.place(x=150, y=600)
        
        # Ввод данных
        self.input_frame = ctk.CTkFrame(root)
        self.input_frame.pack(pady=10)
        
    def set_light_theme(self):
        ctk.set_appearance_mode("light")
        
    def set_dark_theme(self):
        ctk.set_appearance_mode("dark")
        
    def load_from_file(self):
        filename = filedialog.askopenfilename(title="Выберите файл", filetypes=[("Text Files", "*.txt")])
        if filename:
            self.numbers = input_from_file(filename)
            if self.numbers:
                self.build_histogram()

    def load_from_console(self):
        self.clear_input_area()

        # Многострочное поле для ввода
        self.input_label = ctk.CTkLabel(self.input_frame, text="Введите числа, каждое на новой строке (завершите ввод 0):", font=("Helvetica", 18))
        self.input_label.pack()

        self.input_text = ctk.CTkTextbox(self.input_frame, font=("Helvetica", 18), height=200, width=200)
        self.input_text.pack(pady=10)

        self.submit_button = ctk.CTkButton(self.input_frame, text="Отправить", font=("Helvetica", 18), command=self.submit_console_input)
        self.submit_button.pack(pady=10)

    def submit_console_input(self):
        input_text = self.input_text.get("1.0", "end-1c")  # Получаем текст из многострочного поля
        try:
            # Разбиваем текст по строкам, убираем пустые строки и преобразуем в список чисел
            numbers = [int(line.strip()) for line in input_text.splitlines() if line.strip()]
            if 0 in numbers:
                numbers.remove(0)  # Убираем ноль, который завершает ввод
            self.numbers = numbers
            if self.numbers:
                self.build_histogram()
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Пожалуйста, введите корректные числа.")

    def generate_random(self):
        self.clear_input_area()
        self.input_label = ctk.CTkLabel(self.input_frame, text="Введите количество чисел, минимальное и максимальное значение:", font=("Helvetica", 18))
        self.input_label.pack()

        self.n_label = ctk.CTkLabel(self.input_frame, text="Количество чисел", font=("Helvetica", 14))
        self.n_label.pack()
        self.n_entry = ctk.CTkEntry(self.input_frame, font=("Helvetica", 16))
        self.n_entry.pack()

        self.min_label = ctk.CTkLabel(self.input_frame, text="Минимальное значение", font=("Helvetica", 14))
        self.min_label.pack()
        self.min_entry = ctk.CTkEntry(self.input_frame, font=("Helvetica", 16))
        self.min_entry.pack()

        self.max_label = ctk.CTkLabel(self.input_frame, text="Максимальное значение", font=("Helvetica", 14))
        self.max_label.pack()
        self.max_entry = ctk.CTkEntry(self.input_frame, font=("Helvetica", 16))
        self.max_entry.pack()

        self.intervals_label = ctk.CTkLabel(self.input_frame, text="Количество интервалов", font=("Helvetica", 14))
        self.intervals_label.pack()
        self.intervals_entry = ctk.CTkEntry(self.input_frame, font=("Helvetica", 16))
        self.intervals_entry.pack()

        self.submit_button = ctk.CTkButton(self.input_frame, text="Генерировать", font=("Helvetica", 16), command=self.submit_random_input)
        self.submit_button.pack(pady=10)

    def submit_random_input(self):
        try:
            n = int(self.n_entry.get())
            min_val = int(self.min_entry.get())
            max_val = int(self.max_entry.get())
            intervals = int(self.intervals_entry.get())
            if n <= 0 or min_val >= max_val or intervals <= 0:
                raise ValueError
            self.numbers = generate_random_numbers(n, min_val, max_val)
            self.intervals = intervals
            if self.numbers:
                self.build_histogram()
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Пожалуйста, введите корректные значения.")

    def build_histogram(self):
        build_histogram(self.numbers, self.intervals)

    def save_image(self):
        self.clear_input_area()
        build_histogram(self.numbers, self.intervals, save_image=True)

    def clear_input_area(self):
        for widget in self.input_frame.winfo_children():
            widget.destroy()

    def show_statistics(self):
        show_statistics(self.numbers)
  

    def show_help(self):
        messagebox.showinfo(
            "Справка",
            "Работу выполнил студент второго курса Информационной безопасности Кагарманов А.Р\n"
            "Программа предназначена для построения гистограмм массива чисел X.\n\n"
            "Как пользоваться:\n"
            "1. Введите данные:\n"
            "   - Кнопка: Ввод данных из файла.\n"
            "   - Кнопка: Ввод данных из консоли.\n"
            "   - Кнопка: Генерация случайных чисел.\n"
            "        При генерации случайных чисел, сгенерированные данные отображаются только в гистограмме.\n"
            "2. Нажмите кнопку 'Показать статистику', чтобы увидеть статистику по введённым данным.\n"
            "3. Выполните построение гистограммы и сохраните её как изображение.\n\n"
            "Если есть вопросы/предложения, обратиться к разработчику: r.kagarmanov20@gmail.com"
        )
       


if __name__ == "__main__":
    root = ctk.CTk()
    app = HistogramApp(root)
    root.mainloop()
