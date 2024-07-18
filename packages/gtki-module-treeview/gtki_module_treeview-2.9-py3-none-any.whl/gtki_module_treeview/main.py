from tkinter import ttk
from tkinter import *
import os
import datetime
from gtki_module_treeview import functions
from gtki_module_treeview import settings


class MainTreeview:
    def __init__(self, master, font='"Roboto" 12', text_foreground_color='white', height=18, text_background_color='black',
                 standart_screen_height=1080, *args, **kwargs):
        self.master = master
        self.screenwidth = master.winfo_screenwidth()
        self.screenheight = master.winfo_screenheight()
        self.companies = {}
        self.font = font
        self.reverse = False
        self.style = ttk.Style()
        self.style.map("Treeview",
                       foreground=self.fixed_map("foreground"),
                       background=self.fixed_map("background"))
        self.text_foreground_color = text_foreground_color
        self.text_background_color = text_background_color
        self.height = functions.get_screen_kf(table_height=height, screen_height=self.screenheight,
                                              screen_height_standart=standart_screen_height)

    def sortTime(self, tv, col):
        """ Ранжировка поля по времени """
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        newList = []
        for el in l:
            if el[0] == 'None':
                newList.append(('23:59:59', el[1]))
            else:
                newList.append((el[0], el[1]))
        newList.sort(key=lambda x: datetime.datetime.strptime(x[1], '%H:%M:%S'), reverse=self.reverse)
        for index, (val, k) in enumerate(newList):
            tv.move(k, '', index)
        self.change_reverse()

    def sortDate(self, tv, col):
        """ Ранжировака поля по дате """
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        newList = []
        for el in l:
            if el[0] == 'None':
                newList.append(('23:59 01.01', el[1]))
            else:
                newList.append((el[0], el[1]))
        try:
            newList.sort(key=lambda x: datetime.datetime.strptime(x[0], '%H:%M %d.%m'),
                         reverse=self.reverse)
        except:
            newList.sort(key=lambda x: datetime.datetime.strptime(x[0], '%H:%M %d.%m'),
                         reverse=self.reverse)
        for index, (val, k) in enumerate(newList):
            tv.move(k, '', index)
        self.change_reverse()

    def sortWeight(self, tv, col):
        """ Ранжировка поля по числам (здесь - веса) """
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        newList = []
        for el in l:
            if el[0] == 'None':
                newList.append((0, el[1]))
            else:
                newList.append((el[0], el[1]))
        newList.sort(key=lambda t: int(t[0]), reverse=self.reverse)
        for index, (val, k) in enumerate(newList):
            tv.move(k, '', index)
        self.change_reverse()

    def getMovedDate(self, date):
        """ Возвращает отформатированное время, где время стоит перед датой"""
        try:
            date = date.strftime('%H:%M %d.%m')
        except AttributeError:
            date = 'None'
        return date

    def change_reverse(self):
        """ Переключить флажок для порядка сортировки"""
        if self.reverse == False:
            self.reverse = True
        else:
            self.reverse = False

    def sortId(self, tv, col, reverse=False):
        """ Функция для ранжировки поля по ID """
        l = [(tv.item(k)["text"], k) for k in tv.get_children()]  # Display column #0 cannot be set
        if reverse == False:
            l.sort(key=lambda t: t[0], reverse=self.reverse)
            self.change_reverse()
        else:
            l.sort(key=lambda t: t[0], reverse=True)
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

    def sortUsual(self, tv, col):
        """ Обычная ранжировка поля по алфавиту """
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=self.reverse)
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)
        self.change_reverse()

    def OnClick(self, event):
        """ Реакция treeview на клик по названию поля"""
        col = self.tree.identify_column(event.x)
        if self.reverse:
            self.img = PhotoImage(file=settings.tric_up_pic_path)
        else:
            self.img = PhotoImage(file=settings.tric_down_pic_path)
        self.tree.heading(col, anchor='w', image=self.img)

    def fixed_map(self, option):
        return [elm for elm in self.style.map("Treeview", query_opt=option)
                if elm[:2] != ("!disabled", "!selected")]

    def get_tree(self):
        """ Вернуть таблицу """
        return self.tree

    def get_timenow(self):
        """ Возвращает отформатированную, читабельную дату """
        today = datetime.datetime.today()
        frmt = today.strftime('%Y.%m.%d %H:%M:%S')
        return frmt

    def clearTree(self):
        """ Очистить таблицу"""
        self.tree.delete(*self.tree.get_children())

    def create_get_tree(self):
        self.tree = self.createTree()
        return self.get_tree()

class NotificationTreeview(MainTreeview):
    """ Тревью о ситуации в системе """
    def __init__(self,  master, *args, **kwarg):
        super().__init__(master, *args, **kwarg)
        self.errors_desctription = {True: 'Подключение успешно',
                                    False: 'Подключение утеряно'}


    def createTree(self):
        self.tree = ttk.Treeview(self.master, style="Custom.Treeview")
        self.tree["columns"] = ("one")
        self.tree.column("#0", width=int(self.screenwidth/4.8), minwidth=int(self.screenwidth/36), stretch='NO')
        self.tree.column("one", width=int(self.screenwidth/1.669), minwidth=int(self.screenwidth/36), stretch='NO')

        self.tree.heading("#0", text="Пункт", anchor='w')
        self.tree.heading("one", text="Статус", anchor='w')
        self.tree.config(height=self.height)


    def fillTree(self, information):
        self.clearTree()
        for point, info in information.items():
            value = self.errors_desctription[info['status']]
            self.tree.insert("", 0, text=point, values=(value,))

class KPPTreeview(MainTreeview):
    """ Тревью о ситуации в системе """
    def __init__(self,  master, *args, **kwarg):
        super().__init__(master, *args, **kwarg)
        width = 1543

    def createTree(self):
        self.tree = ttk.Treeview(self.master, style="KPP.Treeview")
        self.tree["columns"] = ("one", "two", "three", "four", "five", "six")
        self.tree.column("#0", width=100, minwidth=43, stretch='NO')
        self.tree.column("one", width=150, stretch='NO')
        self.tree.column("two", width=175, stretch='NO')
        self.tree.column("three", width=175, stretch='NO')
        self.tree.column("four", width=300, stretch='NO')
        self.tree.column("five", width=300, stretch='NO')
        self.tree.column("six", width=343, stretch='NO')

        self.tree.heading("#0", text="№", anchor='w')
        self.tree.heading("one", text="Гос. номер", anchor='w')
        self.tree.heading("two", text="Время въезда", anchor='w')
        self.tree.heading("three", text="Время выезда", anchor='w')
        self.tree.heading("four", text="Клиент", anchor='w')
        self.tree.heading("five", text="Перевозчик", anchor='w')
        self.tree.heading("six", text="Комментарий", anchor='w')
        self.tree.config(height=self.height)

    def get_frmt_date(self, date):
        if not date:
            return "-"
        newdate = date.strftime('%H:%M %d.%m')
        return newdate

    def fillTree(self, id, car_number, time_in, time_out, client,
                 carrier, note, *args, **kwargs):
        if not car_number: car_number = "-"
        if not note: note = ''
        if not client: client = "-"
        if not carrier: carrier = "-"
        self.tree.insert("", 1, text=id, values=(car_number, self.get_frmt_date(time_in),
                                                 self.get_frmt_date(time_out),
                                                 client, carrier, note))

class CurrentTreeview(MainTreeview):
    def init(self,  master, *args, **kwarg):
        super().__init__( master, *args, **kwarg)

    def createTree(self):
        self.tree = ttk.Treeview(self.master, style="Custom.Treeview")
        self.tree["columns"] = ("one", "two", "two1", "two2", "three", "four", "five")
        self.tree.column("#0", width=int(self.screenwidth / 14.0146), minwidth=int(self.screenwidth / 64), stretch='NO')
        self.tree.column("one", width=int(self.screenwidth / 13.913), minwidth=int(self.screenwidth / 64), stretch='NO')
        self.tree.column("two", width=int(self.screenwidth / 17.1428), minwidth=int(self.screenwidth / 64),
                         stretch='NO')
        self.tree.column("two1", width=int(self.screenwidth / 17.1428), minwidth=int(self.screenwidth / 64),
                         stretch='NO')
        self.tree.column("two2", width=int(self.screenwidth / 18.8235), minwidth=int(self.screenwidth / 64),
                         stretch='NO')
        self.tree.column("three", width=int(self.screenwidth / 13.913), minwidth=int(self.screenwidth / 64),
                         stretch='NO')
        self.tree.column("four", width=int(self.screenwidth / 13.913), minwidth=int(self.screenwidth / 64),
                         stretch='NO')
        self.tree.column("five", width=int(self.screenwidth / 12.15189), minwidth=int(self.screenwidth / 64),
                         stretch='NO')

        self.tree.heading("#0", text="№ акта", anchor='w',
                          command=lambda: self.sortId(self.tree, "#0"))
        self.tree.heading("one", text="Въезд", anchor='w',
                          command=lambda: self.sortDate(self.tree, "one"))
        self.tree.heading("two", text="Брутто", anchor='w',
                          command=lambda: self.sortWeight(self.tree, "two"))
        self.tree.heading("two1", text="Тара", anchor='w',
                          command=lambda: self.sortWeight(self.tree, "two"))
        self.tree.heading("two2", text="Нетто", anchor='w',
                          command=lambda: self.sortWeight(self.tree, "two"))
        self.tree.heading("three", text="Категория", anchor='w',
                          command=lambda: self.sortUsual(self.tree, "three"))
        self.tree.heading("four", text="Гос. номер", anchor='w',
                          command=lambda: self.sortUsual(self.tree, "four"))
        self.tree.heading("five", text="Комментарии", anchor='w',
                          command=lambda: self.sortUsual(self.tree, "five"))
        #self.tree.bind("<Button-1>", self.OnClick)
        self.tree.config(height=self.height)
        self.tree.tag_configure("evenrow", background='white',
                                foreground='black')

    def fillTree(self, id, brutto, tara, cargo, time_in, trash_cat, car_number, notes, record_id, *args, **kwargs):
        if not time_in: time_in = '-'
        if cargo == None: cargo = '-'
        if tara == None: tara = '-'
        self.tree.insert("", 1, text=id, values=(self.getFrmtDate(time_in),
                                                 brutto, tara, cargo,
                                                 trash_cat, car_number, notes),
                         iid=str(record_id), **kwargs)


    def getFrmtDate(self, date):
        if not date:
            return "-"
        newdate = date.strftime('%H:%M %d.%m')
        return newdate

class HistroryTreeview(MainTreeview):
    def init(self,  master, *args, **kwarg):
        super().__init__( master, *args, **kwarg)

    def createTree(self):
        self.tree = ttk.Treeview(self.master, style="Custom.Treeview", )
        self.tree["columns"] = ("1", "10", "2", "3", "4", "5", "6", "7", "8", "9",
                                "11")
        self.tree.column("#0", width=int(self.screenwidth/18.5), minwidth=int(self.screenwidth/64), anchor='w')
        # self.tree.column("preone", width=50, minwidth=30, stretch='NO')
        self.tree.column("1", width=int(self.screenwidth/14), minwidth=int(self.screenwidth/64), stretch='NO')
        self.tree.column("2", width=int(self.screenwidth/9), minwidth=int(self.screenwidth/64), anchor='w')
        self.tree.column("3", width=int(self.screenwidth/20), minwidth=int(self.screenwidth/64), stretch='NO')
        self.tree.column("4", width=int(self.screenwidth/20), minwidth=int(self.screenwidth/64), stretch='NO')
        self.tree.column("5", width=int(self.screenwidth/20), minwidth=int(self.screenwidth/64), stretch='NO')
        self.tree.column("6", width=int(self.screenwidth/17), minwidth=int(self.screenwidth/64), stretch='NO')
        self.tree.column("7", width=int(self.screenwidth/17), minwidth=int(self.screenwidth/64))
        self.tree.column("8", width=int(self.screenwidth/15), minwidth=int(self.screenwidth/64), stretch='NO')
        self.tree.column("9", width=int(self.screenwidth/15), minwidth=int(self.screenwidth/64), stretch='NO')
        self.tree.column("10", width=int(self.screenwidth/9), minwidth=int(self.screenwidth/32), stretch='NO')
        self.tree.column("11", width=int(self.screenwidth/14), minwidth=int(self.screenwidth/32), stretch='NO')
        #self.tree.bind("<Button-1>", self.OnClick)
        self.tree.heading("#0", text="№ акта", anchor='w',
                          command=lambda: self.sortId(self.tree, "#0"))
        self.tree.heading("1", text="Гос. номер", anchor='w',
                          command=lambda: self.sortUsual(self.tree, "1"))
        self.tree.heading("2", text="Перевозчик", anchor='w',
                          command=lambda: self.sortUsual(self.tree, "2"))
        self.tree.heading("3", text="Брутто", anchor='w',
                          command=lambda: self.sortWeight(self.tree, "3"))
        self.tree.heading("4", text="Тара", anchor='w',
                          command=lambda: self.sortWeight(self.tree, "4"))
        self.tree.heading("5", text="Нетто", anchor='w',
                          command=lambda: self.sortWeight(self.tree, "5"))
        self.tree.heading("6", text="Категория", anchor='w',
                          command=lambda: self.sortUsual(self.tree, "6"))
        self.tree.heading("7", text="Вид груза", anchor='w',
                          command=lambda: self.sortUsual(self.tree, "7"))
        self.tree.heading("8", text="Дата въезда", anchor='w',
                          command=lambda: self.sortDate(self.tree, "8"))
        self.tree.heading("9", text="Дата выезда", anchor='w',
                          command=lambda: self.sortDate(self.tree, "9"))
        self.tree.heading("10", text="Клиент", anchor='w',
                          command=lambda: self.sortDate(self.tree, "9"))
        # self.tree.heading("seven", text="На территории",anchor='w')
        self.tree.heading("11", text="Комментарии", anchor='w',
                          command=lambda: self.sortUsual(self.tree, "11"))
        self.tree.config(height=self.height)

    def fillTree(self, records, *args, **kwargs):
        self.clearTree()
        for record in records:
            self.insertRec(**record)

    def insertRec(self, id, car_number, carrier, brutto, tara, cargo, trash_cat, trash_type, time_in, time_out,
                  notes, client, record_id, *args, **kwargs):
        if not client: client = '-'
        if tara == None: tara = '-'
        if cargo == None: cargo = '-'
        if trash_type == None: trash_type = '-'
        self.tree.insert("", 1, text=id, values=(car_number,
                                                     client,  carrier, brutto, tara, cargo, trash_cat, trash_type,
                                                     self.getMovedDate(time_in), self.getMovedDate(time_out),
                                                     notes), tags='usual',
                         iid=str(record_id))
