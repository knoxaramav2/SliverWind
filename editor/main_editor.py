

from functools import partial
import os
from tkinter import BooleanVar, Button, Canvas, Checkbutton, Entry, Frame, IntVar, Label, Listbox, Menu, OptionMenu, Scrollbar, StringVar, Text, Tk, messagebox, simpledialog, filedialog as fd
import tkinter
from tkinter.ttk import Notebook
from os.path import dirname, join
from gridmap import GridManager, GridMap
from icon import Icons, GetIcons
from world_config import WorldConfig
from editor_settings import EditorSettings
import rsc_manager
from rsc_manager import AType, Asset, RSCManager
from file_manager import FileManager
from ed_util import Util, GetUtil
from PIL import ImageTk

class DynamicDiolog(tkinter.Toplevel):

    def __init__(self, parent, title:str, prompts:[tuple[str,StringVar|BooleanVar|IntVar|list[str], StringVar|None]]):
        
        tkinter.Toplevel.__init__(self, parent)
        self.resizable(False, False)

        i = 0
        for p in prompts:

            lbl = Label(self, text=p[0])
            input = None

            if isinstance(p[1], StringVar):
                input = Entry(self, textvariable=p[1])
            elif isinstance(p[1], BooleanVar):
                input = Checkbutton(self, variable=p[1])
            elif isinstance(p[1], IntVar):
                input = Entry(self, textvariable=p[1], validate='all', validatecommand=(self.register(self.__validate_entry), '%P'))
            elif isinstance(p[1], list[str]):
                if len(p[1]) > 0:
                    p[2].set(p[1][0])
                input = OptionMenu(self, p[2], *p[1])

            lbl.grid(column=0, row=i)
            input.grid(column=1, row=i)

            i += 1

        self.accept_btn = Button(self, text='OK', command=self.__accept)
        self.accept_btn.grid(column=2)

    def __validate_entry(self, p):
        return str.isdigit(p)

    def __accept(self, event=None):
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.focus_force()
        self.wait_window()
        return


class Window:

    __root      : Tk
    __map       : Canvas
    __assetlib  : Canvas
    __atlas     : Canvas

    __asset_nb  : Notebook = None
    __asset_btns: Frame = None
    __asset_slct: dict = {}
    __asset_pane: Frame = None
    __curr_asset: Asset = None

    __colls     : dict = {}

    __width     : int = 1100
    __height    : int = 600
    __assets_w  : int = 250
    __atlas_w   : int = 250
    __grid_w    : int = 30
    __grid_h    : int = 20
    __asset_w   : int = 200
    __asset_h   : int = 200

    __util      : Util
    __icons     : Icons
    __rsc_man   : RSCManager = None
    __file_man  : FileManager = None
    __map_man   : GridManager = None
    __settings  : EditorSettings = None
    __world     : WorldConfig = None

    __md_above  : BooleanVar = None
    __md_block  : BooleanVar = None
    __md_event  : BooleanVar = None

    __curr_block: Button     = None
    __toolbox_txt: dict = None

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

    def __get_ico(self, imgname:str, sz=16):
        return ImageTk.PhotoImage(self.__icons.icons[imgname][0].resize((sz,sz), resample=2))

    def __validate_ctrl_state(self):
        state = 'normal' if self.__world != None else 'disabled'
        
        for c in self.__wrld_dep:
            c.configure(state=state)

    def __clear_frame(self, f:Frame|Canvas):
        for c in f.winfo_children():
            c.destroy()

    def __import_asset(self):
        
        group, coll = self.__get_asset_select()

        ext = self.__rsc_man.type_extensions(AType.sprite)
        ext_tip = 'Image'
        spath = self.__world.last_sprite_dir
            
        files = fd.askopenfilenames(initialdir=spath, filetypes=[(ext_tip, ext)], )

        if len(files) == 0:
            return 
        
        self.__world.last_sprite_dir = os.path.dirname(files[0])
        
        for f in files:
            self.__rsc_man.import_asset(f, group, coll.get())

        self.__world.save()
        self.__update_coll_menu()
        self.__refresh_select_frame()

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

    def __update_coll_menu(self, refresh_all=False):

        to_refresh = []

        if refresh_all:
            to_refresh = self.__rsc_man.list_groups(AType.sprite)
            pass
        else:
            to_refresh.append(self.__get_asset_select()[0])

        for tr in to_refresh:
            group = tr
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

        self.__refresh_select_frames()

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
        self.__refresh_select_frame()
        var.set(coll)

    def __remove_collection(self):
        group, coll = self.__get_asset_select()

        resp = messagebox.askyesno('Confirm', f'Delete collection "{coll.get()}" and its assets?')
        if resp == 'no':
            return
        
        self.__rsc_man.remove_collection(group, coll.get())
        self.__update_coll_menu()
        self.__refresh_select_frame()

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

    def __click_map_grid(self, cvc, abtn:Button, shift=False, ctrl=False):
        if self.__curr_asset == None or self.__curr_asset.rsc == None: return
        
        overdraw = shift and not ctrl
        block = ctrl and not shift
        event = ctrl and shift

        x, y = abtn.pos
        map = self.__map_man.curr_map()
        block = map.get_block(x, y)
        block.overdraw = not block.overdraw
        block.block = not block.block

        if event:
            collide = BooleanVar(cvc, value=False)
            transport = StringVar(cvc, value='')
            options = map.list_neightbors()
            if len(options) > 0:
                transport.set(options[0])

            input = DynamicDiolog(cvc, 'Event Select', [
                ('On Contact', collide),
                ('Transport', options, transport),
                ('Script', options, transport)
            ])        

        bg = 'white'

        if overdraw and not block: bg = 'RoyalBlue1'
        elif not overdraw and block: bg = 'firebrick1'
        elif overdraw and block: bg = 'DarkOrchid1'

        bc = 'dodger blue' if event else 'white'
        bc = 'red'
        fg = 'green'
        if self.__curr_asset.atype == AType.sprite:
            abtn.configure(image=self.__curr_asset.rsc, background=bg, fg=fg,
                           highlightcolor=bc, relief='ridge')
        
        abtn.block = block
        abtn.overdraw = overdraw
        abtn.event = event
        self.__curr_block = abtn
        self.update_toolbox()


    def __click_asset_grid(self, abtn:Button):
        self.__curr_asset = abtn.asset

    def __refresh_select_frames(self):

        for group in self.__asset_slct.keys():
            coll = self.__rsc_man.get_coll_var(group).get()
            self.__refresh_select_frame(group, coll)

    def __refresh_select_frame(self, group:str=None, col:str=None):

        if group == None or col== None:
            group, col = self.__get_asset_select()
            col = col.get()

        frame:Frame = self.__asset_slct[group]
        assets = self.__rsc_man.get_assets(group, col)

        self.__clear_frame(frame)

        for i in range(0, len(assets)):
            a = assets[i]
            b = Button(frame, width=16, height=16, image=a.rsc)
            b.asset = a
            b.configure(command=partial(self.__click_asset_grid, b))

            x = i %5
            y = int(i/5)
            b.grid(column=x, row=y)

    def __make_select_frame(self, cvc, group:str):

        frame = Frame(cvc, background='orange',
                      width=self.__asset_w, height=self.__asset_h)
        self.__asset_slct[group] = frame
        return frame

    def __on_asset_coll_change(self, *args):
        grp, col = self.__get_asset_select()
        self.__refresh_select_frame(grp, col.get())

    def __init_tab(self, cvc, group):
        frame = Frame(cvc, background='yellow')
        dropframe = Frame(frame, background='blue')

        var = self.__rsc_man.get_coll_var(group)
        options = self.__rsc_man.list_collections(group)
        var.set(options[0])
        var.trace('w', self.__on_asset_coll_change)
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

        ip = self.__get_ico('import')
        rp = self.__get_ico('cross')
        nc = self.__get_ico('newfolder')
        rc = self.__get_ico('remfolder')

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
        rem_col.configure(command=lambda :self.__remove_collection())

        return btnf

    def __init_assets(self, cvc):

        tabf = Frame(cvc)
        
        btnf = self.__init_asset_buttons(tabf)
        tabs = self.__init_tabs(tabf)
        self.__asset_nb = tabs

        btnf.grid(column=0, row=0, sticky='w')
        tabs.grid(column=0, row=1)
        tabf.pack(fill='both', expand=1)

    def __new_map(self, cvc):
        
        w:int
        h:int
        name:str

        w_var = IntVar(cvc, value=10)
        h_var = IntVar(cvc, value=10)
        name_var = StringVar(cvc, value='')

        prompt = DynamicDiolog(cvc, 'New Map', 
                               [('Map Name:', name_var),
                                ('Width: ', w_var),
                                ('Height: ', h_var)]
                               )
        prompt.show()

        w = w_var.get()
        h = h_var.get()
        name = name_var.get()

        if (name == '' or w < 0 or h < 0):
            messagebox.showerror('Invalid Input', 'Map cannot be created')
            return

        self.__map_man.add_map(name ,w, h)
        self.__init_map(self.__map)

    def __remove_map(self, cvc):
        pass

    def __init_map_toolbar(self, cvc):

        frame = Frame(cvc, width=500, height=25, background='purple', name='map_toolbar')

        new_img = self.__get_ico('newmap')
        rem_img = self.__get_ico('remmap')
        evt_img = self.__get_ico('event')
        ovd_img = self.__get_ico('overdraw')
        blk_img = self.__get_ico('block')

        self.__md_above = BooleanVar(cvc, False)
        self.__md_block = BooleanVar(cvc, False)
        self.__md_event = BooleanVar(cvc, False)

        new_map = Button(frame, image=new_img)
        new_map.img = new_img
        rem_map = Button(frame, image=rem_img)
        rem_map.img = rem_img
        overdraw = Checkbutton(frame, image=ovd_img, variable=self.__md_above)
        overdraw.img = ovd_img
        event = Checkbutton(frame, image=evt_img, variable=self.__md_event)
        event.img = evt_img
        block = Checkbutton(frame, image=blk_img, variable=self.__md_block)
        block.img = blk_img

        new_map.configure(command=lambda:self.__new_map(cvc))
        rem_map.configure(command=lambda:self.__remove_map(cvc))

        rem_map.pack(anchor='e', side='right', padx=5)
        new_map.pack(anchor='e', side='right', padx=5)
        event.pack(anchor='center', side='right', padx=5)
        overdraw.pack(anchor='center', side='right', padx=5)
        block.pack(anchor='center', side='right', padx=5)
        self.__wrld_dep.extend([new_map, rem_map, overdraw, block, event])

        return frame
    
    def __init_map_grid(self, cvc, map:GridMap):
        frame = Frame(cvc, name='map_grid')

        if map == None:
            return frame

        w, h = map.size()

        frame.blank = self.__get_ico('blank')
        for y in range(0, h):
            for x in range(0, w):
                
                cell = Button(
                    frame, image=frame.blank,
                    background='gray',
                    highlightthickness=1, relief='flat', border=1, bd=1
                    )
                cell.pos = (x, y)
                cell.block = False
                cell.event = False
                cell.overdraw = False
                cell.configure(command=partial(self.__click_map_grid, frame, cell))
                cell.grid(row=y, column=x, padx=0, pady=0)

        return frame
    
    def update_toolbox(self):

        curr = self.__curr_block
        if curr == None:
            return
        
        x,y = curr.pos

        map = self.__map_man.curr_map()
        block = map.get_block(x, y)

        self.__toolbox_txt['POS'].configure(text=f'POS: ({x}, {y})')
        self.__toolbox_txt['BLOCK'].configure(text=f'BLOCK: {block.block}')
        self.__toolbox_txt['EVENT'].configure(text=f'EVENT: {block.event}')


    def __init_map_toolbox(self, cvc):
        frame = Frame(cvc)
        
        self.__toolbox_txt = {}

        coord = Label(frame, text='POS:')
        blocked = Label(frame, text='BLOCK:')
        overdraw = Label(frame, text='OVERDRAW:')
        event = Label(frame, text='EVENT:')

        self.__toolbox_txt['POS'] = coord
        self.__toolbox_txt['BLOCK'] = blocked
        self.__toolbox_txt['OVERDRAW'] = overdraw
        self.__toolbox_txt['EVENT'] = event

        coord.grid(column=0, row=0)
        blocked.grid(column=0, row=1)
        overdraw.grid(column=1, row=1)
        event.grid(column=2, row=1)

        return frame


    def __init_map(self, cvc):


        if self.__map_man == None:
            return
        
        self.__clear_frame(cvc)

        frame = Frame(cvc, width=self.__grid_w, height=self.__grid_h, background='black', name='map_tools')

        curr_map = self.__map_man.curr_map()

        toolbar = self.__init_map_toolbar(frame)
        map = self.__init_map_grid(frame, curr_map)
        toolbox = self.__init_map_toolbox(frame)

        toolbar.pack(expand=True, fill='x', side='top')
        map.pack(anchor='center', fill='both', expand=True)
        toolbox.pack(anchor='s', fill='both', expand=True, side='bottom')

        frame.pack(fill='both', expand=True)
        self.__adjust_win()
        
    def __clear_configs(self):
        self.__world = None
        self.__rsc_man = None
        self.__map_man = None
        self.__file_man = None

    def __create_world(self):

        self.__clear_configs()

        name = simpledialog.askstring('Create New World', 'World Name')
        
        tpath = os.path.join(self.__util.gamedata_uri, name)
        if os.path.exists(tpath):
            messagebox.showerror('Error', f'Project "{os.path.basename(tpath)}" already exists')

        if name == None or name == '':
            return
        
        world_path = os.path.join(tpath, os.path.basename(tpath))

        self.__util.set_project_name(name)
        self.__set_title(name)
        self.__init_configs(world_path)
        self.__rsc_man.import_default_assets()
        self.__init_assets(self.__assetlib)
        self.__init_map(self.__map)
        self.__update_coll_menu(refresh_all=True)
        self.__validate_ctrl_state()
        
    def __load_world(self, path:str=None):

        self.__clear_configs()

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
        self.__init_map(self.__map)
        self.__refresh_select_frame()

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
        self.__clear_configs()
        self.__rsc_man = RSCManager(self.__root)
        self.__file_man = FileManager(self.__rsc_man)
        self.__world = WorldConfig(path, self.__rsc_man)
        #self.__file_man.new_world(self.__world)
        self.__world.open(self.__root)
        self.__map_man = GridManager()

        if self.__asset_nb != None:
            self.__update_coll_menu()
        self.__validate_ctrl_state()

    def __init__(self):

        self.__root = Tk()
        self.__util = GetUtil()
        self.__icons = GetIcons()
        self.__settings = EditorSettings()
        #self.__init_configs()
        r = self.__root
        w = self.__width
        h = self.__height
        assets_w = self.__assets_w
        atlas_w = self.__atlas_w

        self.__set_title()
        r.wm_iconphoto(True, ImageTk.PhotoImage(self.__icons.icons['main'][0]))
        r.geometry('%sx%s'%(w, h))
        r.resizable(False, False)
        r.configure(background='gray')

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

        #self.__clean_grid(self.__map)
        self.__init_menu(r)
        #self.__init_atlas(self.__atlas)
        #self.__init_assets(self.__assetlib)
        #self.__init_map(self.__map)

        self.__adjust_win()
        self.__validate_ctrl_state()

