def get_screen_kf(table_height, screen_height, screen_height_standart=1080):
    """ В связи с тем, что height в Treeview различный, для разных экранов, эта функция стандартизирует их, относительно
    заданного размера (screen_height_standart). Таким образом, высота таблицы в 18 единиц на экране 1080, будет
    выглядеть точно так-же и на разрешении 1366 (и других), поскольку превратится в 13:
    screen_kf = 1080/18 = 60
    new_table_height = 768/60 = 12.8"""
    screen_kf = screen_height_standart/table_height
    new_table_height = screen_height/screen_kf
    return int(new_table_height)
