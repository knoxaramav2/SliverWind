

import math
from tkinter import BooleanVar, Button, Canvas, Checkbutton, Frame, Label, Listbox, Menu, OptionMenu, Scrollbar, StringVar, Tk
import tkinter
from tkinter.ttk import Notebook


class Window:

    __root      : Tk
    __map       : Canvas
    __assetlib  : Canvas
    __atlas     : Canvas

    __width     : int = 1100
    __height    : int = 600
    __assets_w  : int = 250
    __atlas_w   : int = 250
    __grid_w    : int = 40
    __grid_h    : int = 25

    def __adjust_win(self):
        self.__root.update()
        total_w = (self.__atlas.winfo_width() +
                   self.__map.winfo_width()+
                   self.__assetlib.winfo_width())
        total_h = max(self.__atlas.winfo_height(),
                   self.__map.winfo_height(),
                #    self.__assetlib.winfo_height()
                   )
        self.__root.geometry(f'{total_w}x{total_h}')
        

    def __spacer(self, cvc, col, row):
        sp = Label(cvc, bd=1, borderwidth=1,
              fg='white', background='grey',
              width=2, height=1,
              highlightthickness=1, bg='black')
        sp.grid(row=row, column=col, padx=0, pady=0)

    def __clean_grid(self, cvc):
        for y in range(0, self.__grid_h):
            for x in range(0, self.__grid_w):
                self.__spacer(cvc, x, y)

    def __init_atlas(self, cvc):
        pass

    def __init_scripts(self, cvc):
        pass

    def __init_actors(self, cvc):
        pass

    def __create_scrollgrid(self, cvc):
        sframe = Frame(cvc)
        cvc.configure(scrollregion=cvc.bbox('all'))
        scroll = Scrollbar(cvc, orient='vertical', command=cvc.yview)
        cvc.configure(yscrollcommand=scroll.set)

        
        scroll.pack(side='right', fill='y')
        
        cvc.pack(side='bottom', anchor='nw', fill='x')
        sframe.pack(anchor='w', fill='x')

        cvc.create_line(0, 0, self.__assets_w, self.__grid_h)
        cvc.configure(scrollregion=cvc.bbox('all'))

        for x in range(0, 7):
            for y in range(0, 10):
                self.__spacer(sframe, x, y)

        return sframe, scroll

    def __init_fg(self, cvc):
        pass

    def __init_bg(self, cvc:Canvas):

        options = ['Testset1', 'Testset2']
        value = StringVar(cvc)
        value.set(options[0])
        dropdown = OptionMenu(cvc, value, *options)
        dropdown.pack(anchor='nw', side='top', fill='both')

        sframe, scroll = self.__create_scrollgrid(cvc)

    def __init_assets(self, cvc):
        tabs = Notebook(cvc)
        bg_tab = Canvas(tabs, height=self.__grid_h, width=self.__assets_w)
        fg_tab = Frame(tabs)
        actor_tab = Frame(tabs)
        script_tab = Frame(tabs)

        self.__init_bg(bg_tab)
        self.__init_fg(fg_tab)
        self.__init_actors(actor_tab)
        self.__init_scripts(script_tab)

        tabs.add(bg_tab, text='Bg')
        tabs.add(fg_tab, text='Fg')
        tabs.add(actor_tab, text='Actors')
        tabs.add(script_tab, text='Scripts')

        tabs.pack()


    def __init_map(self, cvc):
        pass

    def __init_menu(self,cvc):

        menubar = Menu(cvc)
        filemenu = Menu(menubar, tearoff=0)
        helpmenu = Menu(menubar, tearoff=0)
        aboutmenu = Menu(menubar, tearoff=0)
        tilemenu = Menu(menubar, tearoff=0)
        show_blocking = BooleanVar(menubar, value=False)
        show_script = BooleanVar(menubar, value=False)
        
        
        filemenu.add_command(label='New World', command=None)
        filemenu.add_command(label='Open', command=None)
        filemenu.add_command(label='Recent', command=None)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=None)
        menubar.add_cascade(label='File', menu=filemenu)

        helpmenu.add_command(label='Help', command=None)
        menubar.add_cascade(label='Help', menu=helpmenu)

        aboutmenu.add_command(label='About', command=None)
        menubar.add_cascade(label='About', menu=aboutmenu)

        menubar.add_separator()

        tilemenu.add_checkbutton(label='Blocking', onvalue=1, offvalue=0, 
                                variable=show_blocking, selectcolor='blue')
        tilemenu.add_checkbutton(label='Script', onvalue=1, offvalue=0, 
                                variable=show_script, selectcolor='blue')
        menubar.add_cascade(label='Tiles', menu=tilemenu)
        
        self.__root.config(menu=menubar)

    def show(self):
        self.__root.update()
        self.__root.mainloop()

    def __init__(self):

        self.__root = Tk()

        r = self.__root
        w = self.__width
        h = self.__height
        assets_w = self.__assets_w
        atlas_w = self.__atlas_w

        r.title('SWedit')
        r.geometry('%sx%s'%(w, h))
        r.resizable(False, False)
        r.configure(background='grey')

        self.__atlas = tkinter.Canvas(r, background='red',
                                        width=atlas_w, height=h,
                                        )

        self.__map = tkinter.Canvas(r, background='green',
                             width=w, height=h,
                             )

        self.__assetlib = tkinter.Canvas(r, background='blue',
                                        width=assets_w, height=h,
                                        )
        
        self.__atlas.grid(sticky='NW', column=0, row=0)
        self.__map.grid(sticky='NW', column=1, row=0)
        self.__assetlib.grid(sticky='NE', column=2, row=0)

        self.__init_menu(r)
        self.__init_atlas(self.__atlas)
        self.__init_assets(self.__assetlib)
        self.__init_map(self.__map)

        self.__clean_grid(self.__map)
        self.__adjust_win()


