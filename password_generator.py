import random
import tkinter as tk
import string
import pyperclip #pip install pyperclip
import sqlite3 as sql
from tkinter import messagebox
from cryptography.fernet import Fernet
import os
class PasswordGenerator():
    def __init__(self, root):
        self.root = root
        tk.Label(self.root, text = 'Website Link').grid(row = 0, column = 0)
        tk.Label(self.root, text = 'Username').grid(row = 1, column = 0)
        tk.Button(self.root, text = 'Quit!!!', command = self.root.quit).grid(row = 0, column = 2)
        tk.Button(self.root, text = 'Help Me', command = self.help).grid(row = 1, column = 2)
        self.web_entry = tk.Entry(self.root)
        self.web_entry.grid(row = 0, column = 1)
        self.web_entry.focus()
        self.user_entry = tk.Entry(self.root)
        self.user_entry.grid(row = 1, column = 1)
        self.generate = tk.Button(self.root, text = "Generate Password", command = self.generate_password)
        self.generate.grid(row = 3, column = 2)
        self.generate = tk.Button(self.root, text = "Lookup Password", command = self.lookup_password)
        self.generate.grid(row = 3, column = 0)
        self.symbols = string.ascii_letters + '0123456789' + '+-*!@#_()'
        self.db = sql.connect("password_collections.db")
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS PASSWORDS 
            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
            WEBSITE TEXT NOT NULL,
            USERNAME TEXT NOT NULL,
            PASSWORD TEXT NOT NULL);
        """)
        
    def help(self):
        message = "1. The password length should be NUMERIC only.\n2. The password length is usually between 8 to 12 charachters, rarely going 16.\n3. After the password is generated it is automatically copied to Clipboard.\n4. If you want to lookup password click on the button and then enter the key provided to you in key.txt file and press the button again."
        messagebox.showinfo("Help", message)
    def generate_password(self):
        buffer_size = 64 * 1024
        website = self.web_entry.get() 
        username = self.user_entry.get()
        if (website and username):
            result = self.db.cursor().execute("""
            Select username, website from PASSWORDS where username = ? AND website = ?
            """,(username, website))
            result = result.fetchone()
            if result:
                if (username in result and website in result):
                    messagebox.showerror('Exists', "This data already exists!")
            else:
                #key = Fernet.generate_key()
                key = 'CFfEbFSX6oDeNOJ6CVb_IZPUvodAuJF0ptri4waYqZY='
                if not os.path.isfile('key.txt'):
                    file = open("key.txt",'w')
                    file.write(key)
                    file.close()
                encryption_type = Fernet(key)
                password = ''.join(random.sample(self.symbols, random.randint(8,12)))
                pyperclip.copy(password)
                insert_query = """
                INSERT INTO PASSWORDS (WEBSITE, USERNAME, PASSWORD)
                VALUES (?,?,?);
                """
                data_tuple = (website, username, encryption_type.encrypt(bytes(password,'utf-8')))
                self.db.cursor().execute(insert_query, data_tuple)
                self.db.commit()
                messagebox.showinfo('Database',"Record inserted successfully")
                #messagebox.showinfo('Key',f'Given below is the key to the database.\nIf you want to lookup the keys you will have to first enter this key.\n{key}\nKEEP THIS VERY VERY SAFE.')
        else:
            messagebox.showerror('','Empty field')

    def lookup_password(self):
        tk.Label(self.root, text = 'Key').grid(row = 2, column = 0)
        self.key = tk.Entry(self.root, show = '*')
        self.key.grid(row = 2, column = 1)
        self.generate = tk.Button(self.root, text = "Lookup Password", command = self.lookup_password_key)
        self.generate.grid(row = 3, column = 0)
        
    def lookup_password_key(self):
        if self.key.get():
            website = self.web_entry.get() 
            username = self.user_entry.get()
            if (website and username):
                result = self.db.cursor().execute("""
                Select password from PASSWORDS where username = ? AND website = ?
                """,(username, website))
                result = result.fetchone()
                encryption_type = Fernet(bytes(self.key.get(),'utf-8'))
                result = encryption_type.decrypt(result[0])
                messagebox.showinfo('Your Password', 'Password copied to clipboard')
                pyperclip.copy(result.decode('utf-8'))
            else:
                messagebox.showerror('','Empty field')
if __name__ == '__main__':
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()
