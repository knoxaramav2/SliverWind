

import os
from tkinter import BooleanVar, Button, Canvas, Checkbutton, Frame, Label, Listbox, Menu, OptionMenu, Scrollbar, StringVar, Tk, messagebox, simpledialog, filedialog as fd
import tkinter
from tkinter.ttk import Notebook
from os.path import dirname, join
from icon import Icons, GetIcons
from world_config import WorldConfig
from editor_settings import EditorSettings
import rsc_manager
from rsc_manager import AType, RSCManager
from file_manager import FileManager
from ed_util import Util, GetUtil
from PIL import ImageTk

class Window:

    __root      : Tk
    __map       : Canvas
    __assetlib  : Canvas
    __atlas     : Canvas

    __asset_nb  : Notebook = None
    __asset_btns: Frame = None
    __asset_slct: dict
    __asset_pane: Frame = None

    __colls     : dict = {}

    __width     : int = 1100
    __height    : int = 600
    __assets_w  : int = 250
    __atlas_w   : int = 250
    __grid_w    : int = 40
    __grid_h    : int = 25
    __asset_w   : int = 200
    __asset_h   : int = 200

    __util      : Util
    __icons     : Icons
    __rsc_man   : RSCManager = None
    __file_man  : FileManager = None
    __settings  : EditorSettings = None
    __world     : WorldConfig = None

    #Controls disabled when world not loaded
    __wrld_dep  : list = []

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

    def __validate_ctrl_state(self):
        state = 'normal' if self.__world != None else 'disabled'
        
        for c in self.__wrld_dep:
            c.configure(state=state)

    def __import_asset(self):
        
        group, coll = self.__get_asset_select()

        ext = []
        ext_tip = ''
        spath = self.__util.rsc_uri

        match group:
            case 'bg':
                spath = self.__world.last_bg_dir
                ext = rsc_manager.SPRITE_EXT
                ext_tip = 'Image'
            case 'fg':
                spath = self.__world.last_fg_dir
                ext = rsc_manager.SPRITE_EXT
                ext_tip = 'Image'
            case 'actors':
                spath = self.__world.last_sprite_dir
                ext = rsc_manager.SPRITE_EXT
                ext_tip = 'Image'
            case 'scripts':
                spath = self.__world.last_script_dir
                ext = rsc_manager.SCRIPT_EXT
                ext_tip = 'Script'
            case 'audio':
                spath = self.__world.last_aud_dir
                ext = rsc_manager.AUDIO_EXT
                ext_tip = 'Script'
            
        
        files = fd.askopenfilenames(initialdir=spath, filetypes=[(ext_tip, ext)], )

        if len(files) == 0:
            return 
        
        self.__world.last_bg_dir = os.path.dirname(files[0])
        
        for f in files:
            self.__rsc_man.import_asset(f, group, coll.get())

        self.__world.save()
        self.__update_coll_menu()

    def __remove_asset(self):

        group, coll = self.__get_asset_select()
        name = None
        #TODO
        if name == None:
            print('No asset to remove (TODO)')
            return
        
        self.__rsc_man.remove_asset(group, coll.get(), name)

        self.__world.save()
        self.__update_coll_menu()

    def __update_coll_menu(self):
        group,_ = self.__get_asset_select()
        group = group.lower()
        var = self.__rsc_man.get_coll_var(group)
        old_sel = var.get()
        var.set('')
        cols = self.__rsc_man.list_collections(group)

        col:OptionMenu = self.__colls[group]
        col['menu'].delete(0, 'end')

        for c in cols:
            col['menu'].add_command(label=c, command=tkinter._setit(var, c))

        var.set(old_sel)
        self.__world.save()

    def __add_collection(self):
        
        group, var = self.__get_asset_select()

        coll = simpledialog.askstring('New Collection', 'Collection Name')
        if coll == None or coll == '': 
            return
        if self.__rsc_man.collection_exists(group, coll):
            messagebox.showerror('Error', 'Collection already exists')
            return
        
        self.__rsc_man.add_collection(group, coll)
        self.__update_coll_menu()
        var.set(coll)

    def __remove_collection(self):
        group, coll = self.__get_asset_select()

        resp = messagebox.askyesno('Confirm', f'Delete collection "{coll.get()}" and its assets?')
        if resp == 'no':
            return
        
        self.__rsc_man.remove_collection(group, coll.get())
        self.__update_coll_menu()

        if not self.__rsc_man.collection_exists(group, coll.get()):
            coll.set('default')

    def __get_asset_select(self):

        if self.__asset_nb == None:
            return (None, None)

        group = self.__asset_nb.tab(self.__asset_nb.select(), 'text')
        coll = self.__rsc_man.get_coll_var(group)

        return (group, coll)

    def __init_atlas(self, cvc):
        pass

    def __make_select_frame(self, cvc, group:str):

        frame = Frame(cvc, background='green',
                      width=self.__asset_w, height=self.__asset_h)

        

        return frame

    def __init_tab(self, cvc, group):
        frame = Frame(cvc, background='yellow')
        dropframe = Frame(frame, background='blue')

        var = self.__rsc_man.get_coll_var(group)
        options = self.__rsc_man.list_collections(group)
        var.set(options[0])
        dropdown = OptionMenu(dropframe, var, *options)

        sel_frame = self.__make_select_frame(frame, group)

        dropdown.pack(fill='x')
        dropframe.pack(anchor='nw', side='top', fill='x')
        sel_frame.pack(anchor='n', side='top', fill='both', expand=1)
        frame.pack()

        #Todo consolidate
        self.__colls[group] = dropdown
        self.__wrld_dep.append(dropdown)

        return frame

    def __init_tabs(self, cvc):

        if self.__asset_nb != None:
            self.__wrld_dep = []
            self.__asset_nb.destroy()
        
        tabs = self.__asset_nb = Notebook(cvc)

        groups = self.__rsc_man.list_groups(AType.sprite)

        for group in groups:
            tab = self.__init_tab(tabs, group)
            tabs.add(tab, text=group)

        return tabs

    def __init_asset_buttons(self, cvc):
        if self.__asset_nb != None:
            return self.__asset_btns
        
        btnf = Frame(cvc)
        self.__asset_btns = btnf

        ip = ImageTk.PhotoImage(self.__icons.icons['import'][0].resize((16,16), resample=2))
        rp = ImageTk.PhotoImage(self.__icons.icons['cross'][0].resize((16,16), resample=2))
        nc = ImageTk.PhotoImage(self.__icons.icons['newfolder'][0].resize((16,16), resample=2))
        rc = ImageTk.PhotoImage(self.__icons.icons['remfolder'][0].resize((16,16), resample=2))

        imp_btn = Button(btnf, image=ip)
        imp_btn.img = ip
        imp_btn.grid(column=0, row=0)
        rem_btn = Button(btnf, image=rp)
        rem_btn.img = rp
        rem_btn.grid(column=1, row=0)

        ncol_btn = Button(btnf, image=nc)
        ncol_btn.img = nc
        ncol_btn.grid(column=2, row=0)
        rem_col = Button(btnf, image=rc)
        rem_col.img = rc
        rem_col.grid(column=3, row=0)

        self.__wrld_dep.append(imp_btn)
        self.__wrld_dep.append(rem_btn)
        self.__wrld_dep.append(ncol_btn)
        self.__wrld_dep.append(rem_col)

        imp_btn.configure(command=lambda :self.__import_asset())
        rem_btn.configure(command=lambda :self.__remove_asset())
        ncol_btn.configure(command=lambda:self.__add_collection())
        rem_col.configure(command=lambda:self.__remove_collection())

        return btnf

    def __init_assets(self, cvc):

        tabf = Frame(cvc)
        
        btnf = self.__init_asset_buttons(tabf)
        tabs = self.__init_tabs(tabf)
        self.__asset_nb = tabs

        btnf.grid(column=0, row=0, sticky='w')
        tabs.grid(column=0, row=1)
        tabf.pack(fill='both', expand=1)

    def __init_map(self, cvc):
        pass

    def __create_world(self):

        name = simpledialog.askstring('Create New World', 'World Name')
        
        tpath = os.path.join(self.__util.gamedata_uri, name)
        if os.path.exists(tpath):
            messagebox.showerror('Error', f'Project "{os.path.basename(tpath)}" already exists')

        if name == None or name == '':
            return

        self.__util.set_project_name(name)
        self.__world = self.__file_man.new_world(name)
        self.__set_title(name)

        self.__init_configs()
        self.__init_assets(self.__assetlib)
        self.__validate_ctrl_state()
        
    def __load_world(self, path:str=None):

        if path == None:
            path = dirname(dirname(__file__))
            path = join(path, 'gamedata')
            path = fd.askopenfilename(initialdir=path, filetypes=[('World File', '.swc')])
        
        if path == None or path == '':
            return
        
        if os.path.exists(path) == False:
            messagebox.showerror('Error', f'Project file "{os.path.basename(path)}" does not exist')
            return

        self.__util.set_project_name(path)
        self.__settings.last_opened = path
        self.__set_title(os.path.basename(path))

        self.__init_configs(path)
        self.__validate_ctrl_state()
        self.__init_assets(self.__assetlib)

    def __save_world(self):
        print('Saving...')
        if (self.__world == None):
            print('Nothing to save')
            return

        self.__settings.last_opened = self.__world.fullpath()
        self.__settings.save()
        self.__world.save()

    def __init_menu(self,cvc):

        lpath = self.__settings.last_opened
        if lpath != '':
            lname = os.path.basename(lpath)
            lname = f' ({lname})'

        menubar = Menu(cvc)
        filemenu = Menu(menubar, tearoff=0)
        helpmenu = Menu(menubar, tearoff=0)
        aboutmenu = Menu(menubar, tearoff=0)
        tilemenu = Menu(menubar, tearoff=0)
        show_blocking = BooleanVar(menubar, value=False)
        show_script = BooleanVar(menubar, value=False)
        
        filemenu.add_command(label='New World', command=self.__create_world)
        filemenu.add_command(label='Open', command=self.__load_world)
        filemenu.add_command(label='Recent'+lname, command=lambda:self.__load_world(lpath))
        filemenu.add_separator()
        filemenu.add_command(label='Save', command=self.__save_world)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.__root.destroy)
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

    def __set_title(self, title:str=''):

        if title != '':
            title = ' *'+title.split('.')[0]

        self.__root.title('SWedit '+title)

    def __init_configs(self, path:str = None):
        self.__rsc_man = RSCManager(self.__root)
        self.__file_man = FileManager(self.__rsc_man)

        if path != None:
            if self.__world == None or self.__world._path != path:
                self.__world = WorldConfig(path, self.__rsc_man)
                self.__world.open(self.__root)

        if self.__asset_nb != None:
            self.__update_coll_menu()
        self.__validate_ctrl_state()

    def __init__(self):

        self.__root = Tk()
        self.__util = GetUtil()
        self.__icons = GetIcons()
        self.__settings = EditorSettings()
        self.__init_configs()
        r = self.__root
        w = self.__width
        h = self.__height
        assets_w = self.__assets_w
        atlas_w = self.__atlas_w

        self.__set_title()
        r.wm_iconphoto(True, ImageTk.PhotoImage(self.__icons.icons['main'][0]))
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

        self.__clean_grid(self.__map)
        self.__init_menu(r)
        self.__init_atlas(self.__atlas)
        self.__init_assets(self.__assetlib)
        self.__init_map(self.__map)

        self.__adjust_win()
        self.__validate_ctrl_state()

