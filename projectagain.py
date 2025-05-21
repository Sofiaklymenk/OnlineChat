from customtkinter import *
import threading
import socket
class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x300")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(("5.tcp.eu.ngrok.io", 18841))
        except Exception as e:
            print(f":Не вдалося підключитися до сервера {e}")


        self.frame = CTkFrame(self, width=200, height=self.winfo_height())
        self.frame.pack_propagate(False)
        self.frame.configure(width = 0)
        self.frame.place(x = 0, y = 0)
        self.is_show_menu = False
        self.frame_width = 0

        self.label = CTkLabel(self.frame, text= "Type your name here:")
        self.label.pack(pady = 30)
        self.entry = CTkEntry(self.frame)
        self.entry.pack(pady = 10)

        self.label_theme = CTkOptionMenu(self.frame, values = ["Dark", "Light"], command=self.change_theme )
        self.label_theme.pack(pady = 20, side = "bottom")
        self.theme = None

        self.btn = CTkButton(self, text = "Menu", width = 150, height = 30, command=self.showMenu)
        self.btn.place(x = 0, y = 0)
        self.menu_show_speed = 20

        self.chat_field = CTkScrollableFrame(self)
        self.chat_field.place(x=0, y=40)

        self.message_input = CTkEntry(self, placeholder_text='Введіть повідомлення: ')
        self.message_input.place(x=0, y=250)
        self.send_button = CTkButton(self, text='▶', width=50, height=30, command=self.send_message)
        self.send_button.place(x=160, y=250)
        self.adaptive_ui()
    
    def showMenu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            #self.close_menu()
        else:
            self.is_show_menu = True
            self.open_menu()

    def open_menu(self):
        if self.frame_width <= 300:
            self.frame_width += self.menu_show_speed
            self.frame.configure(width = self.frame_width, height = self.winfo_height())
            if self.frame_width > 150:
                self.btn.configure(width = self.frame_width)
            self.after(20, self.open_menu)

    def change_theme(self,value):
        if value == 'Dark':
            set_appearance_mode('dark')
        else:
            set_appearance_mode('light')

        self.username = self.entry.get() or "Sofiia"
        try:
            hello = f"TEXT@{self.username}@[SYSTEM]{self.username} приєднався(лась) до чату\n"
            self.sock.send(hello.encode("utf-8"))
        except Exception as e:
            print(f"Помилка відправки: {e}")

        self.receive_thred = threading.Thread(target=self.receive_message, daemon = True)
        self.receive_thred.start()

    def send_message(self):
       message = self.message_input.get().strip()
       if not message:
           return
       self.username = self.entry.get() or "Sofiia"
       if not self.username:
           self.add_message("Помилка! Введи імя")
           return
       try:
           formatted_message = f"TEXT@{self.username}@{message}"
           self.sock.send(formatted_message.encode("utf-8"))
           self.add_message(f"{self.username}:(message)")
           self.message_input.delete(0, END)
       except Exception as e:
           self.add_message(f"Ваш мем не долетів: {e}")

    def add_message(self, message):
        message_label = CTkLabel(self.chat_field, text = message, anchor="w", wraplength=300)
        message_label.pack(anchor = "w", padx = 5, pady = 2)
           
    def receive_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except Exception as e:
                self.add_message(f"Повідомлення загубилосьЖ {e}")
                break
            self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        if len(parts) < 3:
            self.add_message(line)
            return
        msg_type, author, message = parts[0], parts[1], parts[2]
        if msg_type == "TEXT":
            self.add_message(f"{author}:{message}")
        else:
            self.add_message(line)

        








    def adaptive_ui(self):
        self.chat_field.place(x=self.frame.winfo_width() - 1)
        self.chat_field.configure(width=self.winfo_width()-self.frame.winfo_width() - 20, 
                                  height=self.winfo_height()-40)
        self.message_input.configure(width=self.winfo_width()-self.frame.winfo_width()-self.send_button.winfo_width())
        self.message_input.place(x=self.frame.winfo_width(),
                                 y=self.winfo_height()-self.send_button.winfo_height())
        self.send_button.place(x=self.winfo_width()-self.send_button.winfo_width(), y=self.winfo_height()-self.send_button.winfo_height())
        self.after(20, self.adaptive_ui)


    


win = MainWindow()
win.mainloop()