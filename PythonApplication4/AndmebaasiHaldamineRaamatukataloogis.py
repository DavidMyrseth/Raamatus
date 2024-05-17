import tkinter as tk
from tkinter import messagebox
import sqlite3
import datetime

conn = sqlite3.connect('raamatukogu.db')
c = conn.cursor()

# Функция для создания таблиц
def create_tables():
    c.execute('''CREATE TABLE IF NOT EXISTS Авторы (
                 автор_id INTEGER PRIMARY KEY,
                 имя_автора TEXT,
                 дата_рождения DATE)''')

    c.execute('''CREATE TABLE IF NOT EXISTS Жанры (
                 жанр_id INTEGER PRIMARY KEY,
                 название_жанра TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS Книги (
                 книга_id INTEGER PRIMARY KEY,
                 название TEXT,
                 дата_выпуска DATE,
                 автор_id INTEGER,
                 жанр_id INTEGER,
                 FOREIGN KEY (автор_id) REFERENCES Авторы(автор_id),
                 FOREIGN KEY (жанр_id) REFERENCES Жанры(жанр_id))''')

# Создаем таблицы, если их еще нет
create_tables()

# GUI
def add_author_book_genre():
    def save_data():
        full_name = name_entry.get()
        book_title = book_title_entry.get()
        publication_date = publication_date_entry.get()
        genre_name = genre_name_entry.get()

        if not (full_name and book_title and publication_date and genre_name):
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля!")
            return

        try:
            # Проверяем, в правильном ли формате дата выпуска
            datetime.datetime.strptime(publication_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Ошибка", "Дата выпуска указана в неправильном формате. Правильный формат: YYYY-MM-DD")
            return

        # Проверяем, существует ли указанный жанр
        c.execute("SELECT жанр_id FROM Жанры WHERE название_жанра = ?", (genre_name,))
        genre_row = c.fetchone()
        if genre_row is None:
            # Добавляем новый жанр
            c.execute("INSERT INTO Жанры (название_жанра) VALUES (?)", (genre_name,))
            genre_id = c.lastrowid
        else:
            genre_id = genre_row[0]

        # Проверяем, существует ли указанный автор
        c.execute("SELECT автор_id FROM Авторы WHERE имя_автора = ?", (full_name,))
        author_row = c.fetchone()
        if author_row is None:
            # Добавляем нового автора
            c.execute("INSERT INTO Авторы (имя_автора) VALUES (?)", (full_name,))
            author_id = c.lastrowid
        else:
            author_id = author_row[0]

        # Проверяем, существует ли указанная книга
        c.execute("SELECT книга_id FROM Книги WHERE название = ?", (book_title,))
        book_row = c.fetchone()
        if book_row is None:
            # Добавляем новую книгу
            c.execute("INSERT INTO Книги (название, дата_выпуска, автор_id, жанр_id) VALUES (?, ?, ?, ?)",
                      (book_title, publication_date, author_id, genre_id))
            conn.commit()
            messagebox.showinfo("Информация", "Данные добавлены!")
        else:
            messagebox.showerror("Ошибка", "Книга с таким названием уже существует в базе данных!")

        add_window.destroy()

    add_window = tk.Toplevel(root)
    add_window.title("Добавить автора, книгу и жанр")

    name_label = tk.Label(add_window, text="ФИО:")
    name_label.grid(row=0, column=0)
    name_entry = tk.Entry(add_window)
    name_entry.grid(row=0, column=1)

    book_title_label = tk.Label(add_window, text="Название книги:")
    book_title_label.grid(row=1, column=0)
    book_title_entry = tk.Entry(add_window)
    book_title_entry.grid(row=1, column=1)

    publication_date_label = tk.Label(add_window, text="Дата выпуска (ГГГГ-ММ-ДД):")
    publication_date_label.grid(row=2, column=0)
    publication_date_entry = tk.Entry(add_window)
    publication_date_entry.grid(row=2, column=1)

    genre_name_label = tk.Label(add_window, text="Название жанра:")
    genre_name_label.grid(row=3, column=0)
    genre_name_entry = tk.Entry(add_window)
    genre_name_entry.grid(row=3, column=1)

    save_button = tk.Button(add_window, text="Сохранить", command=save_data)
    save_button.grid(row=4, columnspan=2)


def delete_author():
    def delete_data():
        full_name = name_entry.get()

        if not full_name:
            messagebox.showerror("Ошибка", "Пожалуйста, введите имя автора!")
            return

        # Проверяем, существует ли указанный автор
        c.execute("SELECT автор_id FROM Авторы WHERE имя_автора = ?", (full_name,))
        author_row = c.fetchone()
        if author_row is not None:
            author_id = author_row[0]
            # Удаляем автора и все его книги
            c.execute("DELETE FROM Книги WHERE автор_id = ?", (author_id,))
            c.execute("DELETE FROM Авторы WHERE автор_id = ?", (author_id,))
            conn.commit()
            messagebox.showinfo("Информация", "Автор и связанные с ним книги успешно удалены!")
        else:
            messagebox.showerror("Ошибка", "Автор с таким именем не найден в базе данных!")

        delete_window.destroy()

    delete_window = tk.Toplevel(root)
    delete_window.title("Удалить автора")

    name_label = tk.Label(delete_window, text="ФИО:")
    name_label.grid(row=0, column=0)
    name_entry = tk.Entry(delete_window)
    name_entry.grid(row=0, column=1)

    delete_button = tk.Button(delete_window, text="Удалить", command=delete_data)
    delete_button.grid(row=1, columnspan=2)


def delete_books_by_author_or_genre():
    def delete_data():
        delete_type = delete_type_var.get()
        value = value_entry.get()

        if not value:
            messagebox.showerror("Ошибка", f"Пожалуйста, введите {delete_type.lower()}!")
            return

        if delete_type == "Автор":
            # Проверяем, существует ли указанный автор
            c.execute("SELECT автор_id FROM Авторы WHERE имя_автора = ?", (value,))
            author_row = c.fetchone()
            if author_row is not None:
                author_id = author_row[0]
                # Удаляем все книги этого автора
                c.execute("DELETE FROM Книги WHERE автор_id = ?", (author_id,))
                conn.commit()
                messagebox.showinfo("Информация", f"Все книги автора {value} успешно удалены!")
            else:
                messagebox.showerror("Ошибка", "Автор с таким именем не найден в базе данных!")
        elif delete_type == "Жанр":
            # Проверяем, существует ли указанный жанр
            c.execute("SELECT жанр_id FROM Жанры WHERE название_жанра = ?", (value,))
            genre_row = c.fetchone()
            if genre_row is not None:
                genre_id = genre_row[0]
                # Удаляем все книги этого жанра
                c.execute("DELETE FROM Книги WHERE жанр_id = ?", (genre_id,))
                conn.commit()
                messagebox.showinfo("Информация", f"Все книги жанра {value} успешно удалены!")
            else:
                messagebox.showerror("Ошибка", "Жанр с таким названием не найден в базе данных!")

        delete_window.destroy()

    delete_window = tk.Toplevel(root)
    delete_window.title("Удалить книги по автору или жанру")

    delete_type_var = tk.StringVar(value="Автор")
    delete_type_label = tk.Label(delete_window, text="Удалить:")
    delete_type_label.grid(row=0, column=0)
    delete_type_menu = tk.OptionMenu(delete_window, delete_type_var, "Автор", "Жанр")
    delete_type_menu.grid(row=0, column=1)

    value_label = tk.Label(delete_window, text="Имя:")
    value_label.grid(row=1, column=0)
    value_entry = tk.Entry(delete_window)
    value_entry.grid(row=1, column=1)

    delete_button = tk.Button(delete_window, text="Удалить", command=delete_data)
    delete_button.grid(row=2, columnspan=2)


def update_data():
    def save_update():
        record_type = update_type_var.get()
        old_value = old_value_entry.get()
        new_value = new_value_entry.get()
        additional_value = additional_value_entry.get()

        if not (old_value and new_value):
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля!")
            return

        if record_type == "Автор":
            c.execute("UPDATE Авторы SET имя_автора = ?, дата_рождения = ? WHERE имя_автора = ?", (new_value, additional_value, old_value))
        elif record_type == "Книга":
            c.execute("UPDATE Книги SET название = ?, дата_выпуска = ? WHERE название = ?", (new_value, additional_value, old_value))
        elif record_type == "Жанр":
            c.execute("UPDATE Жанры SET название_жанра = ? WHERE название_жанра = ?", (new_value, old_value))

        conn.commit()
        messagebox.showinfo("Информация", f"Данные по {record_type.lower()} успешно обновлены!")
        update_window.destroy()

    update_window = tk.Toplevel(root)
    update_window.title("Обновить данные")

    update_type_var = tk.StringVar(value="Автор")
    update_type_label = tk.Label(update_window, text="Обновить:")
    update_type_label.grid(row=0, column=0)
    update_type_menu = tk.OptionMenu(update_window, update_type_var, "Автор", "Книга", "Жанр")
    update_type_menu.grid(row=0, column=1)

    old_value_label = tk.Label(update_window, text="Текущее значение:")
    old_value_label.grid(row=1, column=0)
    old_value_entry = tk.Entry(update_window)
    old_value_entry.grid(row=1, column=1)

    new_value_label = tk.Label(update_window, text="Новое значение:")
    new_value_label.grid(row=2, column=0)
    new_value_entry = tk.Entry(update_window)
    new_value_entry.grid(row=2, column=1)

    additional_value_label = tk.Label(update_window, text="Дополнительное значение (по необходимости):")
    additional_value_label.grid(row=3, column=0)
    additional_value_entry = tk.Entry(update_window)
    additional_value_entry.grid(row=3, column=1)

    save_update_button = tk.Button(update_window, text="Сохранить", command=save_update)
    save_update_button.grid(row=4, columnspan=2)


def delete_table():
    def confirm_delete():
        table_name = table_var.get()
        if not table_name:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите таблицу!")
            return

        c.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        messagebox.showinfo("Информация", f"Таблица {table_name} успешно удалена!")
        delete_window.destroy()

    delete_window = tk.Toplevel(root)
    delete_window.title("Удалить таблицу")

    table_var = tk.StringVar(value="Авторы")
    table_label = tk.Label(delete_window, text="Таблица:")
    table_label.grid(row=0, column=0)
    table_menu = tk.OptionMenu(delete_window, table_var, "Авторы", "Жанры", "Книги")
    table_menu.grid(row=0, column=1)

    delete_button = tk.Button(delete_window, text="Удалить",

    command=confirm_delete)
    delete_button.grid(row=1, columnspan=2)


def recreate_tables():
    create_tables()
    messagebox.showinfo("Информация", "Все таблицы были успешно созданы заново!")


def show_authors_books_genres():
    def show_data():
        authors_books_genres_window = tk.Toplevel(root)
        authors_books_genres_window.title("Авторы, книги и жанры")

        data_label = tk.Label(authors_books_genres_window, text="Авторы, книги и жанры:")
        data_label.pack()

        data_text = tk.Text(authors_books_genres_window)
        data_text.pack()

        # Очистка вывода перед отображением новых данных
        data_text.delete('1.0', tk.END)

        for row in c.execute("SELECT Авторы.имя_автора, Книги.название, Жанры.название_жанра FROM Авторы INNER JOIN Книги ON Авторы.автор_id = Книги.автор_id INNER JOIN Жанры ON Книги.жанр_id = Жанры.жанр_id"):
            data_text.insert(tk.END, f"Автор: {row[0]}, Книга: {row[1]}, Жанр: {row[2]}\n")

    show_data()

# GUI
root = tk.Tk()
root.title("Библиотека")

add_button = tk.Button(root, text="Добавить автора, книгу и жанр", command=add_author_book_genre)
add_button.pack()

delete_button = tk.Button(root, text="Удалить автора", command=delete_author)
delete_button.pack()

delete_books_button = tk.Button(root, text="Удалить книги по автору или жанру", command=delete_books_by_author_or_genre)
delete_books_button.pack()

update_button = tk.Button(root, text="Обновить данные", command=update_data)
update_button.pack()

delete_table_button = tk.Button(root, text="Удалить таблицу", command=delete_table)
delete_table_button.pack()

recreate_tables_button = tk.Button(root, text="Создать таблицы заново", command=recreate_tables)
recreate_tables_button.pack()

show_button = tk.Button(root, text="Показать авторов, книги и жанры", command=show_authors_books_genres)
show_button.pack()

root.mainloop()

# Закрываем соединение
conn.close()
