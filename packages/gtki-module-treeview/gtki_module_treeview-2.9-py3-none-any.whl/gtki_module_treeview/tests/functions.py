from gtki_module_treeview.main import *
from datetime import datetime


def draw_tree(tar, canvas, information):
    tar.createTree()
    tree = tar.get_tree()
    tar.fillTree(information)
    canvas.create_window(500,500, window=tree)

def test_current_treeview(root,canvas):
    tar = CurrentTreeview(root, text_foreground_color='red')
    information = [['salfk','salfk','salfk','salfk','salfk','salfk', datetime.now(),'salfk','salfk','salfk','salfk']]
    draw_tree(tar, canvas, information)

def test_notif_treeview(root, canvas):
    tar = NotificationTreeview(root, text_foreground_color='red')
    info = {'test1': {'status': True},
            'test2': {'status': False}}
    draw_tree(tar, canvas, info)

def test_stat_treeview(root,canvas):
    pass
