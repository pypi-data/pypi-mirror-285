from tkinter import *
import os
from datetime import datetime
from gtki_module_treeview.tests.functions import *

""" Тестируем отрисовку """
# Определяем пути
dirname = os.getcwd()
imgs_dir = os.path.join(dirname, 'imgs')

# Создаем всякие полезные ништяки
root = Tk()
canvas = Canvas(root, bg='black')


# Кнопочку для вызова туда же
canvas.pack(fill=BOTH, expand=YES)
Button(root, text='Show Error', bg='white', command=lambda: test_current_treeview(root, canvas)).pack()
root.mainloop()