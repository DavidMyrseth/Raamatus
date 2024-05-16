import tkinter as tk
from tkinter import messagebox
import sqlite3
import datetime  # Lisa datetime mooduli import

conn = sqlite3.connect('raamatukogu.db')
c = conn.cursor()

# Loome tabelid, kui neid veel pole
c.execute('''CREATE TABLE IF NOT EXISTS Autorid (
             autor_id INTEGER PRIMARY KEY,
             autor_nimi TEXT,
             sünnikuupäev DATE)''')

c.execute('''CREATE TABLE IF NOT EXISTS Žanrid (
             žanr_id INTEGER PRIMARY KEY,
             žanri_nimi TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS Raamatud (
             raamat_id INTEGER PRIMARY KEY,
             pealkiri TEXT,
             väljaandmise_kuupäev DATE,
             autor_id INTEGER,
             žanr_id INTEGER,
             FOREIGN KEY (autor_id) REFERENCES Autorid(autor_id),
             FOREIGN KEY (žanr_id) REFERENCES Žanrid(žanr_id))''')

# GUI
def add_author_book_genre():
    def save_data():
        full_name = name_entry.get()
        birth_year = birth_year_entry.get()
        book_title = book_title_entry.get()
        publication_date = publication_date_entry.get()
        genre_name = genre_name_entry.get()

        if not (full_name and birth_year and book_title and publication_date and genre_name):
            messagebox.showerror("Viga", "Palun täitke kõik väljad!")
            return

        try:
            # Kontrollime, kas väljaandmise kuupäev on õiges formaadis
            datetime.datetime.strptime(publication_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Viga", "Väljaandmise kuupäev on vigases formaadis. Õige formaat: YYYY-MM-DD")
            return

        # Kontrollime, kas žanr on olemas
        c.execute("SELECT žanr_id FROM Žanrid WHERE žanri_nimi = ?", (genre_name,))
        genre_row = c.fetchone()
        if genre_row is None:
            # Lisame uue žanri
            c.execute("INSERT INTO Žanrid (žanri_nimi) VALUES (?)", (genre_name,))
            genre_id = c.lastrowid
        else:
            genre_id = genre_row[0]

        # Kontrollime, kas autor on juba olemas
        c.execute("SELECT autor_id FROM Autorid WHERE autor_nimi = ?", (full_name,))
        author_row = c.fetchone()
        if author_row is None:
            # Lisame uue autori
            c.execute("INSERT INTO Autorid (autor_nimi, sünnikuupäev) VALUES (?, ?)", (full_name, birth_year))
            author_id = c.lastrowid
        else:
            author_id = author_row[0]

        # Kontrollime, kas raamat on juba olemas
        c.execute("SELECT raamat_id FROM Raamatud WHERE pealkiri = ?", (book_title,))
        book_row = c.fetchone()
        if book_row is None:
            # Lisame uue raamatu
            c.execute("INSERT INTO Raamatud (pealkiri, väljaandmise_kuupäev, autor_id, žanr_id) VALUES (?, ?, ?, ?)",
                      (book_title, publication_date, author_id, genre_id))
            conn.commit()
            messagebox.showinfo("Info", "Andmed lisatud!")
        else:
            messagebox.showerror("Viga", "Sellise pealkirjaga raamat on juba olemas andmebaasis!")

        add_window.destroy()

    add_window = tk.Toplevel(root)
    add_window.title("Lisa autor, raamat ja žanr")

    name_label = tk.Label(add_window, text="Täisnimi:")
    name_label.grid(row=0, column=0)
    name_entry = tk.Entry(add_window)
    name_entry.grid(row=0, column=1)

    birth_year_label = tk.Label(add_window, text="Sünniaasta:")
    birth_year_label.grid(row=1, column=0)
    birth_year_entry = tk.Entry(add_window)
    birth_year_entry.grid(row=1, column=1)

    book_title_label = tk.Label(add_window, text="Raamatu pealkiri:")
    book_title_label.grid(row=2, column=0)
    book_title_entry = tk.Entry(add_window)
    book_title_entry.grid(row=2, column=1)

    publication_date_label = tk.Label(add_window, text="Väljaandmise kuupäev (YYYY-MM-DD):")
    publication_date_label.grid(row=3, column=0)
    publication_date_entry = tk.Entry(add_window)
    publication_date_entry.grid(row=3, column=1)

    genre_name_label = tk.Label(add_window, text="Žanri nimi:")
    genre_name_label.grid(row=4,
column=0)
    genre_name_entry = tk.Entry(add_window)
    genre_name_entry.grid(row=4, column=1)

    save_button = tk.Button(add_window, text="Salvesta", command=save_data)
    save_button.grid(row=5, columnspan=2)


def delete_author():
    def delete_data():
        full_name = name_entry.get()

        if not full_name:
            messagebox.showerror("Viga", "Palun sisestage autori nimi!")
            return

        # Kontrollime, kas autor on olemas
        c.execute("SELECT autor_id FROM Autorid WHERE autor_nimi = ?", (full_name,))
        author_row = c.fetchone()
        if author_row is not None:
            author_id = author_row[0]
            # Kustutame autori ja sellega seotud raamatud
            c.execute("DELETE FROM Raamatud WHERE autor_id = ?", (author_id,))
            c.execute("DELETE FROM Autorid WHERE autor_id = ?", (author_id,))
            conn.commit()
            messagebox.showinfo("Info", "Autor ja sellega seotud raamatud on edukalt kustutatud!")
        else:
            messagebox.showerror("Viga", "Sellise nimega autorit ei leitud andmebaasist!")

        delete_window.destroy()

    delete_window = tk.Toplevel(root)
    delete_window.title("Kustuta autor")

    name_label = tk.Label(delete_window, text="Täisnimi:")
    name_label.grid(row=0, column=0)
    name_entry = tk.Entry(delete_window)
    name_entry.grid(row=0, column=1)

    delete_button = tk.Button(delete_window, text="Kustuta", command=delete_data)
    delete_button.grid(row=1, columnspan=2)


def show_authors_books_genres():
    def show_data():
        authors_books_genres_window = tk.Toplevel(root)
        authors_books_genres_window.title("Autorid, raamatud ja žanrid")

        data_label = tk.Label(authors_books_genres_window, text="Autorid, raamatud ja žanrid:")
        data_label.pack()

        data_text = tk.Text(authors_books_genres_window)
        data_text.pack()

        # Tühjenda väljund enne uute andmete kuvamist
        data_text.delete('1.0', tk.END)

        for row in c.execute("SELECT Autorid.autor_nimi, Raamatud.pealkiri, Žanrid.žanri_nimi FROM Autorid INNER JOIN Raamatud ON Autorid.autor_id = Raamatud.autor_id INNER JOIN Žanrid ON Raamatud.žanr_id = Žanrid.žanr_id"):
            data_text.insert(tk.END, f"Autor: {row[0]}, Raamat: {row[1]}, Žanr: {row[2]}\n")

    show_data()

# GUI
root = tk.Tk()
root.title("Raamatukogu")

add_button = tk.Button(root, text="Lisa autor, raamat ja žanr", command=add_author_book_genre)
add_button.pack()

delete_button = tk.Button(root, text="Kustuta autor", command=delete_author)
delete_button.pack()

show_button = tk.Button(root, text="Näita autoreid, raamatuid ja žanre", command=show_authors_books_genres)
show_button.pack()

root.mainloop()

# Sulgeme ühenduse
conn.close()
