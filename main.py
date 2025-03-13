
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os

# مسیر داینامیک برای پایگاه داده و پوشه تصاویر
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # مسیر فولدر حاوی اسکریپت
QURAN_DB_PATH = os.path.join(BASE_DIR, "quran_farsi.sqlite")
FRUITS_DB_PATH = os.path.join(BASE_DIR, "fruits_properties.db")
IMAGE_PATH = os.path.join(BASE_DIR, "image", "images")  # مسیر جدید تصاویر

# نگاشت نام فارسی میوه‌ها به انگلیسی برای نمایش تصاویر
fruit_name_mapping = {
    "زیتون": "olive",
    "خرما": "dates",
    "انجیر": "fig",
    "انار": "pomegranate",
    "موز": "banana",
    "سیر": "garlic",
    "زنجبیل": "ginger",
    "انگور": "grape",
    "عدس": "lentils",
    "پیاز": "onion",
    "کدو": "pumpkin",
}

# تابع جستجوی آیات در پایگاه داده
def get_verses_by_fruit(fruit):
    conn = sqlite3.connect(QURAN_DB_PATH)
    cursor = conn.cursor()
    query = """SELECT "نام سوره", "شماره سوره", "شماره آیه", "متن آیه", "ترجمه" FROM verses WHERE "ترجمه" LIKE ?"""
    cursor.execute(query, (f"%{fruit}%",))
    verses = cursor.fetchall()
    conn.close()
    return verses

# تابع نمایش تصویر
def display_image(fruit_name, label):
    fruit_english = fruit_name_mapping.get(fruit_name, "default")
    img_path = os.path.join(IMAGE_PATH, f"{fruit_english}.jpg")
    
    if os.path.exists(img_path):
        img = Image.open(img_path)
        img = img.resize((200, 200), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        label.config(image=img_tk)
        label.image = img_tk
    else:
        label.config(image="", text=f"❌ تصویر {fruit_name} یافت نشد!", font=("B Nazanin", 12), fg="red")

# تابع صفحه جستجوی آیات
def open_verse_search():
    verse_window = tk.Toplevel(root)
    verse_window.title("جستجوی آیات قرآنی مرتبط با میوه‌ها")
    verse_window.geometry("600x700")
    verse_window.configure(bg="#e6f7ff")

    image_label = tk.Label(verse_window, bg="#e6f7ff")
    image_label.pack(pady=10)

    frame = tk.Frame(verse_window, bg="#e6f7ff")
    frame.pack(pady=5)
    tk.Label(frame, text="نام میوه را وارد کنید:", font=("B Nazanin", 14), bg="#e6f7ff").pack()
    entry = tk.Entry(frame, font=("B Nazanin", 14))
    entry.pack(pady=5)

    text_box = tk.Text(verse_window, font=("B Nazanin", 14), wrap=tk.WORD, bg="#ffffff", fg="#333333")
    text_box.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def search_verses():
        fruit_name = entry.get().strip()
        if not fruit_name:
            messagebox.showerror("خطا", "لطفاً نام یک میوه را وارد کنید!")
            return

        display_image(fruit_name, image_label)

        verses = get_verses_by_fruit(fruit_name)
        text_box.delete("1.0", tk.END)
        if not verses:
            text_box.insert(tk.END, "❌ هیچ آیه‌ای مرتبط با این میوه یافت نشد.\n\n", "error")
        else:
            for surah, surah_num, verse_num, arabic, translation in verses:
                text_box.insert(tk.END, f"📖 سوره {surah} ({surah_num}), آیه {verse_num}\n", "title")
                text_box.insert(tk.END, f"{arabic}\n", "arabic")
                text_box.insert(tk.END, f"📝 ترجمه: {translation}\n\n", "translation")

    tk.Button(frame, text="جستجو", font=("B Nazanin", 14), bg="#4CAF50", fg="white", command=search_verses).pack()

# تابع نمایش لیست میوه‌ها
def show_fruit_list():
    try:
        conn = sqlite3.connect(FRUITS_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM fruits")
        fruits = cursor.fetchall()
        conn.close()
    except sqlite3.OperationalError as e:
        messagebox.showerror("خطا", f"امکان باز کردن پایگاه داده وجود ندارد! خطا: {e}")
        return

    list_window = tk.Toplevel()
    list_window.title("لیست میوه‌ها")
    list_window.geometry("600x400")
    list_window.configure(bg="#fff3e6")

    ttk.Label(list_window, text="لیست میوه‌های بهشتی", font=("B Nazanin", 16, "bold"), background="#fff3e6").pack(pady=10)

    button_frame = tk.Frame(list_window, bg="#fff3e6")
    button_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    buttons_per_row = 3
    row, col = 0, 0

    for fruit in fruits:
        fruit_name = fruit[0]
        btn = tk.Button(
            button_frame,
            text=fruit_name,
            font=("B Nazanin", 12),
            bg="#333333",
            fg="white",
            width=15,
            height=2,
            command=lambda f=fruit_name: show_fruit_properties(f)
        )
        btn.grid(row=row, column=col, padx=5, pady=5)

        col += 1
        if col >= buttons_per_row:
            col = 0
            row += 1

# تابع نمایش خواص هر میوه
def show_fruit_properties(fruit_name):
    try:
        conn = sqlite3.connect(FRUITS_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT properties FROM fruits WHERE name = ?", (fruit_name,))
        properties = cursor.fetchone()
        conn.close()
    except sqlite3.OperationalError as e:
        messagebox.showerror("خطا", f"خطایی در خواندن اطلاعات از پایگاه داده رخ داده است! خطا: {e}")
        return

    prop_window = tk.Toplevel()
    prop_window.title(f"خواص {fruit_name}")
    prop_window.geometry("500x400")
    prop_window.configure(bg="#ffe6e6")

    ttk.Label(prop_window, text=f"خواص {fruit_name}", font=("B Nazanin", 16, "bold"), background="#ffe6e6").pack(pady=10)

    if properties:
        text_box = tk.Text(prop_window, wrap="word", height=15, width=50, font=("B Nazanin", 14), bg="#ffffff", fg="#333333")
        text_box.insert("1.0", properties[0])
        text_box.pack(pady=10, padx=10)
        text_box.config(state="disabled")
    else:
        ttk.Label(prop_window, text="اطلاعاتی یافت نشد.", font=("B Nazanin", 14), background="#ffe6e6").pack(pady=10)

# ایجاد صفحه اصلی
root = tk.Tk()
root.title("برنامه جامع میوه‌های قرآنی و بهشتی")
root.geometry("400x300")
root.configure(bg="#f0f0f0")

tk.Button(root, text="🔍 جستجوی آیات قرآنی", font=("B Nazanin", 14), bg="#4CAF50", fg="white", command=open_verse_search).pack(pady=20)
tk.Button(root, text="🍇 خواص میوه‌های بهشتی", font=("B Nazanin", 14), bg="#FF9800", fg="white", command=show_fruit_list).pack(pady=20)

root.mainloop()
