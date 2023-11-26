

from functools import partial
import os
import subprocess
import sys
from tkinter import BooleanVar, Button, Canvas, Checkbutton, Entry, Frame, IntVar, Label, Listbox, Menu, OptionMenu, Scrollbar, StringVar, Text, Tk, Widget, messagebox, simpledialog, filedialog as fd
import tkinter
from tkinter.ttk import Notebook, Treeview
from os.path import dirname, join
import types
from gridmap import Block, Event, GridManager, GridMap
from icon import Icons, GetIcons
from world_config import WorldConfig
from editor_settings import EditorSettings
import rsc_manager
from rsc_manager import AType, Asset, RSCManager
from ed_util import Util, GetUtil, coall
from PIL import ImageTk

#####################################
#####SUPPORT CLASSES
#####################################
class DynamicDiolog(tkinter.Toplevel):

    def __init__(self, parent, title:str,options:list, prompts:[tuple[str,StringVar|BooleanVar|IntVar|list[str], StringVar|None]]):
        
        tkinter.Toplevel.__init__(self, parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()

        self.result = StringVar(self, 'Unknown')

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
            elif isinstance(p[1], list):
                if len(p[1]) == 0:
                    p[1].append('default')
                    p[2].set(p[1][0])
                input = OptionMenu(self, p[2], *p[1])
            elif isinstance(p[1], types.LambdaType):
                input = Button(self, text='New Zone', command=p[1])

            lbl.grid(column=0, row=i)
            input.grid(column=1, row=i)

            i += 1

        self.btns = []
        j = 0
        for opt in options:
            btn = Button(self, text=opt, command=partial(self.__close, opt))
            btn.grid(row = i, column=j)
            self.btns.append(btn)
            j += 1

    def __validate_entry(self, p):
        return str.isdigit(p)

    def __close(self, result:str):
        self.result.set(result)
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.focus_force()
        self.wait_window()
        return self.result.get()

class Config:
    debug       : bool = False

    def __parse(self, args:[str]):

        for arg in args:
            match arg:
                case '-d': self.debug = True

    def __init__(self) -> None:
        self.__parse(sys.argv)


#####################################
#####MAIN CLASS
#####################################

class Window:

    __root      : Tk
    __map       : Canvas = None
    __assetlib  : Canvas = None
    __atlas     : Canvas = None

    __asset_nb  : Notebook = None
    __asset_btns: Frame = None
    __asset_slct: dict = {}
    __zone_pane : Frame = None
    __curr_asset: Asset = None
    __curr_zone : StringVar = None

    __colls     : dict = {}
    __zones     : OptionMenu
    __grid      : list[list[Button]]

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
    __map_man   : GridManager = None
    __settings  : EditorSettings = None
    __world     : WorldConfig = None
    __cfg       : Config = None

    __md_above  : BooleanVar = None
    __md_block  : BooleanVar = None
    __md_event  : BooleanVar = None

    __curr_block: Button     = None
    __toolbox_txt: dict = None
    __isstart   : Checkbutton

    #Controls disabled when world not loaded
    __wrld_dep  : list = []


#####################################
#####HACKY SUPPORT STUFF
#####################################
    def __adjust_win(self):
        self.__root.update()
        total_w = (self.__atlas.winfo_width() +
                   self.__map.winfo_width()+
                   self.__assetlib.winfo_width())
        total_h = max(self.__atlas.winfo_height(),
                   self.__map.winfo_height(),
                   self.__assetlib.winfo_height()
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

#####################################
#####RESOURCE MANAGEMENT/HELPERS
#####################################

    def __get_ico(self, imgname:str, sz=16):
        return ImageTk.PhotoImage(self.__icons.icons[imgname][0].resize((sz,sz), resample=2))
#TODO: Add identifiers to controls for validation support
    def __validate_ctrl_state(self):
        state = 'disabled' if self.__world == None or self.__map_man.curr_map() == None else 'normal'
        for c in self.__wrld_dep:
            if not issubclass(type(c), Widget): continue
            c.configure(state=state)


    def __clear_frame(self, f:Frame|Canvas):
        for c in f.winfo_children():
            c.destroy()

    def __clear_data(self):
        self.__world = None
        self.__rsc_man = None
        self.__map_man = None

        self.__asset_nb = None
        self.__asset_btns = None
        self.__asset_slct = {}
        self.__curr_asset = None

#####################################
#####ASSET MANAGEMENT
#####################################
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
        self.__refresh_asset_select_frame()

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

            if old_sel in cols:
                var.set(old_sel)

        self.__refresh_asset_select_frames()

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
        self.__refresh_asset_select_frame()
        var.set(coll)

    def __remove_collection(self):
        group, coll = self.__get_asset_select()

        resp = messagebox.askyesno('Confirm', f'Delete collection "{coll.get()}" and its assets?')
        if resp == 'no':
            return
        
        self.__rsc_man.remove_collection(group, coll.get())
        self.__update_coll_menu()
        self.__refresh_asset_select_frame()

        if not self.__rsc_man.collection_exists(group, coll.get()):
            coll.set('default')

    def __get_asset_select(self):

        if self.__asset_nb == None:
            return (None, None)

        group = self.__asset_nb.tab(self.__asset_nb.select(), 'text')
        coll = self.__rsc_man.get_coll_var(group)

        return (group, coll)
    
    def __click_asset_grid(self, abtn:Button):
        self.__curr_asset = abtn.asset

#####################################
#####ATLAST MANAGEMENT
#####################################
    def __init_atlas(self, cvc):

        self.__clear_frame(cvc)
        frame = Frame(cvc)
        
        map_panel = self.__init_map_panel(frame)

        map_panel.grid(column=0, row=0, sticky='w')
        frame.pack(fill='both', expand=True)

        #self.__refresh_map_panel()

        return frame
    
    def __refresh_map_panel(self, *args):
        frame = self.__zone_pane
        maps = self.__map_man.list_maps(self.__curr_zone.get())

        self.__clear_frame(frame)
        for i in range(0, len(maps)):
            map:GridMap = maps[i]
            bg = 'gray' if map != self.__map_man.get_start_map() else 'gold'
            b = Button(frame, background=bg, text=f'{map.name} : ({map.id})')
            b.configure(command=partial(self.__change_map, map))
            b.pack(expand=True, fill='x', pady=3)

    def __init_map_panel(self, cvc):
        frame = Frame(cvc)
        zone_select = Frame(frame)

        add_zone = Button(frame, text='Add Zone', command=partial(self.__add_zone, frame))

        if self.__curr_zone == None: 
            self.__curr_zone = StringVar(self.__atlas, 'default')

        zone_var = self.__curr_zone
        options = self.__map_man.list_zones()
        if len(options) == 0:
            options.append('default')
        zone_var.set(options[0])
        print(f'>> IMP ZV {self.__curr_zone.get()}')
        
        dropdown = OptionMenu(zone_select, zone_var, *options)
        zone_var.trace('w', self.__refresh_map_panel)

        self.__zone_pane = Frame(frame, width=self.__atlas_w, background='red')

        add_zone.pack(fill='x', side='top', anchor='ne')
        dropdown.pack(fill='x')
        zone_select.pack(anchor='nw', side='top', fill='x')
        self.__zone_pane.pack(anchor='n', side='top', fill='both', expand=1)
        frame.pack()

        self.__zones = dropdown
        #self.__wrld_dep.append(dropdown)

        return frame
    
    def __refresh_zone_menu(self, *args):        
        zones = self.__map_man.list_zones()
        if len(zones) == 0:
            zones.append('default')

        print(f'<< RZM {self.__curr_zone.get()}')
        old_val = self.__curr_zone.get()
        self.__curr_zone.set('default')
        print(f'>> RZM {self.__curr_zone.get()}')

        self.__zones['menu'].delete(0, 'end')
        for z in zones:
            self.__zones['menu'].add_command(label=z, command=tkinter._setit(self.__curr_zone, z))

        if old_val in zones:
            self.__curr_zone.set(old_val)
            print(f'>>> RZM {self.__curr_zone.get()}')
        else:
            self.__curr_zone.set(zones[-1])
            print(f'>>> RZM {self.__curr_zone.get()}')

    def __refresh_asset_select_frames(self):

        for group in self.__asset_slct.keys():
            coll = self.__rsc_man.get_coll_var(group).get()
            self.__refresh_asset_select_frame(group, coll)

    def __refresh_asset_select_frame(self, group:str=None, col:str=None):

        if group == None or col== None:
            group, col = self.__get_asset_select()
            col = col.get()

        frame:Frame = self.__asset_slct[group]
        assets = self.__rsc_man.list_assets(group, col)

        self.__clear_frame(frame)

        for i in range(0, len(assets)):
            a = assets[i]
            b = Button(frame, width=16, height=16, image=a.rsc)
            b.asset = a
            b.configure(command=partial(self.__click_asset_grid, b))

            x = i %5
            y = int(i/5)
            b.grid(column=x, row=y)

    def __make_select_frame(self, cvc, var_list:dict, group:str):

        frame = Frame(cvc, background='orange',
                      width=self.__asset_w, height=self.__asset_h)
        var_list[group] = frame
        return frame

    def __on_asset_coll_change(self, *args):
        grp, col = self.__get_asset_select()
        self.__refresh_asset_select_frame(grp, col.get())

    def __init_tab(self, cvc, group):
        frame = Frame(cvc, background='yellow')
        coll_select = Frame(frame, background='blue')

        var = self.__rsc_man.get_coll_var(group)
        options = self.__rsc_man.list_collections(group)
        var.set(options[0])
        var.trace('w', self.__on_asset_coll_change)
        dropdown = OptionMenu(coll_select, var, *options)

        sel_frame = self.__make_select_frame(frame, self.__asset_slct, group)

        dropdown.pack(fill='x')
        coll_select.pack(anchor='nw', side='top', fill='x')
        sel_frame.pack(anchor='n', side='top', fill='both', expand=1)
        frame.pack()

        #Todo consolidate
        self.__colls[group] = dropdown
        #self.__wrld_dep.append(dropdown)

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

        self.__clear_frame(cvc)
        tabf = Frame(cvc, height=self.__asset_h)
        
        btnf = self.__init_asset_buttons(tabf)
        tabs = self.__init_tabs(tabf)
        self.__asset_nb = tabs

        btnf.grid(column=0, row=0, sticky='w')
        tabs.grid(column=0, row=1)
        tabf.pack(fill='both', expand=True)

    def __add_zone(self, cvc = None):
        cvc = coall(cvc, self.__atlas)
        zone = StringVar(cvc, value='')
        dlg = DynamicDiolog(cvc, 'New Zone',
                            ['OK', 'Cancel'],
                            [('Zone Name: ', zone)]
                            )
        res = dlg.show()

        if res == 'Cancel' or zone.get() == '':
            return False
        zn_txt = zone.get()
        self.__curr_zone.set(zn_txt)
        print(f'>> AZ {self.__curr_zone.get()}')
        self.__map_man.add_zone(zn_txt)
        self.__refresh_map_panel()
        self.__refresh_zone_menu()

        return True

    def __new_map(self, cvc, old_map:GridMap=None, src_dir:str=None):
        
        w:int
        h:int
        zone:str
        name:str

        w_var = IntVar(cvc, value=10)
        h_var = IntVar(cvc, value=10)
        zones = self.__map_man.list_zones()
        zone_var = StringVar(cvc, value=self.__curr_zone.get())
        name_var = StringVar(cvc, value='')

        prompt = DynamicDiolog(cvc, 'New Map', 
                               ['OK', 'Cancel'],
                               [('New Zone', zone_var),
                                ('Zone', zones, zone_var),
                                ('Map Name:', name_var),
                                ('Width: ', w_var),
                                ('Height: ', h_var)]
                               )
        if prompt.show() == 'Cancel':
            return

        if zone_var.get() != '':
            self.__curr_zone.set(zone_var.get())
            self.__map_man.add_zone(zone_var.get())

        w = w_var.get()
        h = h_var.get()
        zone = zone_var.get()
        name = name_var.get()

        if (name == '' or zone == '' or w < 0 or h < 0):
            err = ''
            if name == '': err = 'map name'
            elif zone == '': err = 'zone name'
            elif w < 0 or h < 0: err = 'dimension'
            messagebox.showerror(f'Invalid Input', f'Map cannot be created. Invalid {err}.')
            return

        self.__map_man.add_map(zone, name ,w, h)

        if old_map != None and src_dir != None:
            src_dir = src_dir.upper()
            new_map = self.__map_man.curr_map()
            if src_dir == 'NORTH':
                old_map.North = new_map
                new_map.South = old_map
            elif src_dir == 'SOUTH':
                old_map.South = new_map
                new_map.North = old_map
            elif src_dir == 'EAST':
                old_map.East = new_map
                new_map.West = old_map
            elif src_dir == 'WEST':
                old_map.West = new_map
                new_map.East = old_map

        self.__init_map(self.__map)
        self.__refresh_map_panel()
        self.__update_toolbox()

    def __remove_map(self, cvc):
        
        self.__refresh_map_panel()
        self.__update_toolbox()
        self.__init_map(self.__map)

#####################################
#####MAP MANAGEMENT
#####################################
    def __refresh_cell(self, block:Block, cell:Button):

        if block == None: return

        bg = 'gray'
        edge = 'flat'
        img = None if block.image == None else block.image.rsc

        if block.overimage != None: edge = 'ridge'
        
        if block.block and block.event == None: bg = 'firebrick1'
        elif not block.block and block.event != None: bg = 'dodger blue'
        elif block.block and block.event != None: bg = 'DarkOrchid1'

        cell.configure(image=img, bg=bg, relief=edge)

    def __refresh_grid(self):
        print(f'refresh {len(self.__grid)}x{len(self.__grid[0])}')
        map = self.__map_man.curr_map()
        for y in range(len(self.__grid)):
            for x in range(len(self.__grid[y])):
                cell = self.__grid[y][x]
                block = map.get_block(x, y)
                self.__refresh_cell(block, cell)

    def __fill_grid(self, event):
        map = self.__map_man.curr_map()
        if map == None or self.__curr_asset == None: return
        pos = self.__curr_block.pos
        curr = map.get_block(pos[0], pos[1]).image

        for y in range(len(self.__grid)):
            for x in range(len(self.__grid[y])):
                cell = self.__grid[y][x]
                block = map.get_block(x, y)
                if block == None:
                    block = Block()
                    block.image = self.__curr_asset
                elif block.image != curr: continue
                block.image = self.__curr_asset
                map.place_block(x, y, block)
        
        self.__refresh_grid()

    def __click_map_grid(self, cvc, abtn:Button, event):
        
        can_edit = self.__curr_asset != None and self.__curr_asset.rsc != None
        self.__curr_block = abtn

        shift = True if event.state == 9 or event.state == 13 else False
        ctrl = True if event.state == 12 or event.state == 13 else False
        alt = event.state == 131080

        x, y = abtn.pos
        map = self.__map_man.curr_map()

        block = map.get_block(x, y)
        
        if block == None:
            block = Block()
            block.pos = (x, y)
            block.image = None
            block.overimage = None
        abtn.data = block
    
        print(block.pos)

        if (shift and not ctrl and can_edit):#Toggle blockings
            block.block = not block.block
        elif (not shift and ctrl and can_edit):#Set overdraw
            if block.overimage == self.__curr_asset:
                block.overimage = None
                img = None if block.image == None else block.image.rsc
                abtn.configure(image=img)
            else:
                block.overimage = self.__curr_asset
                img = None if block.overimage == None else block.overimage.rsc
                abtn.configure(image=img)
            
        elif (shift and ctrl and can_edit):#Set/edit event
            block_event = block.event
            if block_event == None:
                block_event = Event()

            collide = BooleanVar(cvc, value=block_event.collide)
            transport = StringVar(cvc, value='')
            options = map.list_neightbors()
            if len(options) > 0:
                transport.set(options[0])
            script = StringVar(cvc, value='')
            script_args = StringVar(cvc, value='')
            script_options = ['']
            if len(script_options) > 0:
                script.set(script_options[0])

            input = DynamicDiolog(cvc, 'Event Select', ['OK', 'Remove', 'Cancel'], [
                ('On Contact', collide),
                ('Transport', options, transport),
                ('Script', script_options, script),
                ('Script Args', script_args)
            ])       
            res = input.show()
            if res == 'OK':
                block_event.collide = collide.get()
                block_event.transport = transport.get()
                block_event.script_args = script_args.get()
                block.event = block_event
                if abtn.event_img == None:
                    bx, by = abtn.winfo_x(), abtn.winfo_y()
                    w = abtn.winfo_width()
                    evi = Canvas(abtn.master, width=5, height=5, background='gold', bd=0, border=0, highlightthickness=0)
                    evi.place(anchor='ne', x=bx+w, y=by)
                    abtn.event_img = evi
            elif res == 'Remove':
                block.event = None
                abtn.event_img.destroy()
                abtn.event_img = None

        elif can_edit and not alt:#Normal place
            block.image = self.__curr_asset

        self.__refresh_cell(block, abtn)
        map.place_block(x, y, block)
        self.__update_toolbox()

    def __script_select(self, cvc):
        
        map = self.__map_man.curr_map()
        if map == None: return
        
        coll = StringVar(cvc, '')
        script = StringVar(cvc, '')

        class ScriptSelect(tkinter.Toplevel):
            
            col_sel     : OptionMenu
            scr_sel     : OptionMenu

            colls       : list[str] = []
            asts        : list[str] = []
            load_lbl    : Label

            coll_var    : StringVar
            scr_var     : StringVar

            rsc         : RSCManager

            
            def __init__(self, parent, rsc:RSCManager, coll_var:StringVar, scr_var:StringVar):
                tkinter.Toplevel.__init__(self, parent)
                self.title('Select Onload Script')
                self.resizable(False, False)
                self.grab_set()

                self.rsc = rsc
                self.col_var = coll_var
                self.scr_var = scr_var
                self.res = StringVar(self, '')

                self.colls = rsc.list_collections('scripts')
                if len(self.colls) == 0: self.colls.append('default')
                coll_var.set(self.colls[0])
                print(f'>>> {self.colls[0]}')
                self.asts = [t.name for t in rsc.list_assets('scripts', coll_var.get())]
                if len(self.asts) == 0: self.asts.append('')

                new_col = Button(self, text='New Collection', command=self.new_coll)
                new_scr = Button(self, text='New Script', command=self.new_script)
                self.col_sel = OptionMenu(self, coll_var, *self.colls)
                self.scr_sel = OptionMenu(self, scr_var, *self.asts)

                coll_var.trace('w', self.reload_colls)
                scr_var.trace('w', self.reload_script)

                self.load_lbl = Label(self, text=f'Load script: {self.scr_var.get()}')

                self.ok = Button(self, state=self.ok_state(), text='OK', command=lambda:self.close('OK'))
                cancel = Button(self, text='Cancel', command=lambda:self.close('Close'))

                self.col_sel.grid(row=0, column=0)
                new_col.grid(row=0, column=1)
                self.scr_sel.grid(row=1, column=0)
                new_scr.grid(row=1, column=1)
                self.load_lbl.grid(row=2, column=0)
                self.ok.grid(row=3, column=0)
                cancel.grid(row=3, column=1)

            def ok_state(self):
                return 'disabled' if self.scr_var.get() == '' or self.col_var.get() == '' else 'normal'

            def new_coll(self):
                col_name = simpledialog.askstring('New Collection', 'Name: ')
                if col_name == None or col_name == '': return
                if col_name in self.colls: return
                self.colls.append(col_name)
                self.reload_colls()
                self.col_var.set(col_name)
                self.reload_script()

            def new_script(self, *args):
                scr_name = simpledialog.askstring('New Collection', 'Name: ')
                if scr_name == None or scr_name == '' or scr_name in self.asts: return
                self.asts.append(scr_name)
                self.scr_var.set(scr_name)
                self.reload_script()

            def reload_colls(self, *args):
                new = self.rsc.list_collections('scripts')
                self.col_sel['menu'].delete(0, 'end')
                if len(new) > 0: new = [t for t in new if t != '']
                for i in new:
                    self.col_sel['menu'].add_command(label=i, command=tkinter._setit(self.col_var, i))
                self.reload_script()

            def reload_script(self, *args):
                group = self.col_var.get()
                new = coall(self.rsc.list_assets('scripts', group), [])
                new = [t.name for t in new ]

                if len(new) == 0: new.append('')
                self.scr_sel['menu'].delete(0, 'end')
                if len(new) > 0: new = [t for t in new if t != '']
                for i in new:
                    self.scr_sel['menu'].add_command(label=i, command=tkinter._setit(self.scr_var, i))
                self.ok.configure(state=self.ok_state())

                self.scr_var.set(new[0])
                self.load_lbl.configure(text=f'Load Script: {self.scr_var.get()}')
                

            def close(self, res:str):
                self.res.set(res)
                self.destroy()

            def show(self):
                self.wm_deiconify()
                self.focus_force()
                self.wait_window()
                return self.res.get()
        
        ss = ScriptSelect(cvc, self.__rsc_man, coll, script)
        res = ss.show()
        if res != 'OK' or coll.get() == '' or script.get() == '':
            return
        
        path = self.__util.join(self.__util.script_uri, [coll.get(), script.get()+'.swrit'])
        ast = Asset(script.get(), AType.script, path)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, 'w').close()
        self.__rsc_man.add_asset('scripts', coll.get(), ast)

        map.on_load = ast

    def __launch_editor(self):
        map = self.__map_man.curr_map()

        if map == None: return

        if map.on_load == None or map.on_load == '':
            messagebox.showwarning('Missing script', 
                                   'No load script set')
            return

        if self.__settings.script_editor == '':
            self.__select_editor()
        if self.__settings.script_editor == '':
            return
        
        map = self.__map_man.curr_map()
        args = [self.__settings.script_editor, map.on_load.path]
        subprocess.call(args)

    def __init_map_toolbar(self, cvc):

        frame = Frame(cvc, width=500, height=25, background='purple', name='map_toolbar')

        script_select = Button(frame, text='Choose Script', command=lambda:self.__script_select(frame))
        script_edit = Button(frame, text='Onload Script', command=self.__launch_editor)

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

        new_map.configure(command=partial(self.__new_map, cvc))
        rem_map.configure(command=partial(self.__remove_map, cvc))

        script_select.pack(side='left', padx=5)
        script_edit.pack(side='left', padx=5)
        rem_map.pack(side='right', padx=5)
        new_map.pack(side='right', padx=5)
        
        # event.pack(anchor='center', side='right', padx=5)
        # overdraw.pack(anchor='center', side='right', padx=5)
        # block.pack(anchor='center', side='right', padx=5)
        frame.pack(side='top', expand=True, fill='x')
        self.__wrld_dep.extend([script_edit, script_select, new_map, rem_map, 
                                # overdraw, block, event
                                ])

        return frame
    
    def __init_map_grid(self, cvc, map:GridMap):
        frame = Frame(cvc, name='map_grid')
        self.__root.bind('<KeyPress-F>', self.__fill_grid)
        if map == None:
            return frame

        w, h = map.size()

        self.__grid = [[None]*w for _ in range(h)]

        frame.blank = self.__get_ico('blank')
        for y in range(h):
            for x in range(w):
                cell = Button(
                    frame, image=frame.blank,
                    background='gray',
                    relief='flat',
                    activebackground='gray',
                    highlightthickness=0, 
                    border=0, 
                    bd=1
                    )
                cell.pos = (x, y)
                cell.event_img = None
                cell.bind('<Button-1>', partial(self.__click_map_grid, frame, cell))
                cell.grid(row=y, column=x, padx=0, pady=0)

                self.__grid[y][x] = cell
        self.__refresh_grid()
        return frame

    def __update_dir_btn(self, btn:Button, map:GridMap):
        enabled = map != None
        #state = 'normal' if enabled else 'disabled'
        state = 'normal'
        img = btn.img_green if enabled else btn.img_gray
        btn.configure(state=state, image=img)

    def __update_toolbox(self):

        map = self.__map_man.curr_map()
        if map == None: return
        block = None
        curr = self.__curr_block
        if curr == None:
            x,y = '-','-'
        else:
            sz = map.size()
            x, y = curr.pos
            if x >= sz[0]: x = sz[0] - 1
            if y >= sz[1]: y = sz[1] - 1
            curr.pos = (x, y)
            block = map.get_block(x, y)
        
        if block == None:
            block = Block
            block.block = '---'
            block.overimage = '---'
            block.event = None

        self.__toolbox_txt['POS'].configure(text=f'Pos: ({x}, {y})')
        self.__toolbox_txt['BLOCKED'].configure(text=f'Blocked: {block.block}')
        self.__toolbox_txt['OVERDRAW'].configure(text=f'Over Layer: {block.overimage != None}')

        event_tmp:Event = block.event
        if event_tmp == None:
            event_tmp = Event()
            event_tmp.transport = '---'
            event_tmp.collide = '---'
            event_tmp.script = '---'
            event_tmp.script_args = '---'

        self.__toolbox_txt['TRANSPORT'].configure(text=f'Transport: {event_tmp.transport}')
        self.__toolbox_txt['COLLIDE'].configure(text=f'On Collide: {event_tmp.collide}')
        self.__toolbox_txt['SCRIPT'].configure(text=f'Script: {event_tmp.script}')
        self.__toolbox_txt['SCRIPT_ARGS'].configure(text=f'Args: {event_tmp.script_args}')
        self.__isstart.var.set(map == self.__map_man.get_start_map())
        coms = self.__util.combine_funcs(
                partial(self.__map_man.set_start_map, map._zone, map.name),
                self.__refresh_map_panel)
        self.__isstart.configure(
            command=self.__util.combine_funcs(
                partial(self.__map_man.set_start_map, map._zone, map.name),
                self.__refresh_map_panel)
        )

        self.__update_dir_btn(self.__toolbox_txt['MAPDIR_UP'], map.North)
        self.__update_dir_btn(self.__toolbox_txt['MAPDIR_DOWN'], map.South)
        self.__update_dir_btn(self.__toolbox_txt['MAPDIR_LEFT'], map.West)
        self.__update_dir_btn(self.__toolbox_txt['MAPDIR_RIGHT'], map.East)

        self.__toolbox_txt['MAP_NAME'].configure(text=f'Map name: {map.name}')
        self.__toolbox_txt['MAP_ID'].configure(text=f'Map id: {map.id}')
        self.__toolbox_txt['ZONE_NAME'].configure(text=f'Zone : {map._zone}')

    def __change_map(self, map:GridMap):
        
        self.__save_world()
        self.__map_man.set_curr_map(map)
        self.__init_map(self.__map)

        self.__update_toolbox()

    def __map_dir_pressed(self, dir:str):

        if self.__map_man.curr_map() == None:
            return

        dir = dir.upper()
        map = self.__map_man.curr_map()
        new_map = None

        if dir == 'NORTH': new_map = map.North
        elif dir == 'SOUTH': new_map = map.South
        elif dir == 'EAST': new_map = map.East
        elif dir == 'WEST': new_map = map.West
        
        if new_map == None: self.__new_map(self.__map, map, dir)
        else: self.__change_map(new_map)

    def __init_map_toolbox(self, cvc):

        self.__toolbox_txt = {}

        frame = Frame(cvc)
        
        cell_box = Frame(frame)
        basic_info = Frame(cell_box)
        event_info = Frame(cell_box)
        
        map_box = Frame(frame)
        direct = Frame(map_box)
        map_info = Frame(map_box)

        coord = Label(basic_info, text='Pos: ')
        blocked = Label(basic_info, text='Blocked: ')
        overdraw = Label(basic_info, text='Over Layer: ')

        self.__toolbox_txt['POS'] = coord
        self.__toolbox_txt['BLOCKED'] = blocked
        self.__toolbox_txt['OVERDRAW'] = overdraw

        transport = Label(event_info, text='Transport: ')
        collide = Label(event_info, text='On Collide: ')
        script = Label(event_info, text='Script: ')
        args = Label(event_info, text='Args: ')
        isstart_var = BooleanVar(event_info, value=map == self.__map_man.get_start_map())
        self.__isstart = Checkbutton(event_info, text='Start Map', variable=isstart_var)
        self.__isstart.var = isstart_var
        isstart = self.__isstart

        self.__toolbox_txt['TRANSPORT'] = transport
        self.__toolbox_txt['COLLIDE'] = collide
        self.__toolbox_txt['SCRIPT'] = script
        self.__toolbox_txt['SCRIPT_ARGS'] = args

        dir_up_img_gray = self.__get_ico('up_gray')
        dir_down_img_gray = self.__get_ico('down_gray')
        dir_left_img_gray = self.__get_ico('left_gray')
        dir_right_img_gray = self.__get_ico('right_gray')

        dir_up_img_green = self.__get_ico('up_green')
        dir_down_img_green = self.__get_ico('down_green')
        dir_left_img_green = self.__get_ico('left_green')
        dir_right_img_green = self.__get_ico('right_green')

        dir_up = Button(direct, image=dir_up_img_gray, command=lambda:self.__map_dir_pressed('NORTH'))
        dir_up.img_gray = dir_up_img_gray
        dir_up.img_green = dir_up_img_green
        dir_down = Button(direct, image=dir_down_img_gray, command=lambda:self.__map_dir_pressed('SOUTH'))
        dir_down.img_gray = dir_down_img_gray
        dir_down.img_green = dir_down_img_green
        dir_left = Button(direct, image=dir_left_img_gray, command=lambda:self.__map_dir_pressed('WEST'))
        dir_left.img_gray = dir_left_img_gray
        dir_left.img_green = dir_left_img_green
        dir_right = Button(direct, image=dir_right_img_gray, command=lambda:self.__map_dir_pressed('EAST'))
        dir_right.img_gray = dir_right_img_gray
        dir_right.img_green = dir_right_img_green

        if not dir_up in self.__wrld_dep:
            self.__wrld_dep.extend([dir_up, dir_down, dir_left, dir_right, isstart])

        self.__toolbox_txt['MAPDIR_UP'] = dir_up
        self.__toolbox_txt['MAPDIR_DOWN'] = dir_down
        self.__toolbox_txt['MAPDIR_LEFT'] = dir_left
        self.__toolbox_txt['MAPDIR_RIGHT'] = dir_right

        map_name = Label(map_info, text='Map name: ')
        map_id = Label(map_info, text='Map id: ')
        zone_name = Label(map_info, text='Zone Name: ')

        self.__toolbox_txt['MAP_NAME'] = map_name
        self.__toolbox_txt['MAP_ID'] = map_id
        self.__toolbox_txt['ZONE_NAME'] = zone_name

        coord.grid(row=0)
        blocked.grid(row=1)
        overdraw.grid(row=2)

        transport.grid(column=0, row=0)
        collide.grid(column=1, row=0)
        script.grid(column=0, row=1)
        args.grid(column=1, row=1)
        self.__isstart.grid(column=0, row=2)

        dir_up.grid(column=1, row=0)
        dir_left.grid(column=0, row=1)
        dir_right.grid(column=2, row=1)
        dir_down.grid(column=1, row=2)

        map_name.grid(row=0)
        map_id.grid(row=1)
        zone_name.grid(row=2)

        cell_box.grid(column=0, row=0)
        map_box.grid(column=1, row=0)

        basic_info.grid(column=0, row=0)
        event_info.grid(column=0, row=1)

        direct.grid(column=0, row=0)
        map_info.grid(column=0, row=1)

        return frame

    def __init_map(self, cvc):

        if self.__map_man == None:
            return
        
        self.__clear_frame(cvc)

        frame = Frame(cvc, 
                      width=self.__grid_w, height=self.__grid_h, 
                      background='black', name='map_tools',
                      border=1, bd=1, highlightthickness=1, highlightbackground='gold')

        curr_map = self.__map_man.curr_map()

        toolbar = self.__init_map_toolbar(frame)
        map = self.__init_map_grid(frame, curr_map)
        toolbox = self.__init_map_toolbox(frame)

        toolbar.pack(fill='x', side='top')
        map.pack(anchor='center', fill='both', expand=True)
        toolbox.pack(anchor='s', fill='both', expand=True, side='bottom')

        frame.pack(fill='both', expand=True)
        self.__adjust_win()
    
#####################################
#####TOP LEVEL MANAGEMENT
#####################################

    def __create_world(self):

        self.__clear_data()

        name = simpledialog.askstring('Create New World', 'World Name')
        
        tpath = os.path.join(self.__util.gamedata_uri, name)
        if os.path.exists(tpath):
            messagebox.showerror('Error', f'Project "{os.path.basename(tpath)}" already exists')

        if name == None or name == '':
            return
        
        world_path = os.path.join(tpath, os.path.basename(tpath))

        self.__util.set_project_name(name)
        self.__set_title(name)
        self.__init_configs(world_path, True)
        self.__init_atlas(self.__atlas)
        self.__init_assets(self.__assetlib)
        self.__init_map(self.__map)
        self.__update_coll_menu(refresh_all=True)
        self.__refresh_asset_select_frames()

        self.__map_man.add_map('default', 'map_1', 10, 10)
        self.__map_man.set_start_map('default', 'map_1')
        self.__change_map(self.__map_man.curr_map())

        self.__refresh_zone_menu()
        self.__refresh_map_panel()
        self.__validate_ctrl_state()
        
    def __load_world(self, path:str=None):

        self.__clear_data()

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

        self.__init_configs(path, False)
        
        self.__world.open(self.__root)

        self.__init_atlas(self.__atlas)
        self.__init_assets(self.__assetlib)
        self.__init_map(self.__map)
        self.__update_coll_menu()
        self.__refresh_asset_select_frames()

        smap = self.__map_man.get_start_map()
        self.__change_map(smap)

        self.__validate_ctrl_state()

    def __save_world(self, *args):
        print('Saving...')
        
        if self.__world != None:
            self.__settings.last_opened = self.__world.fullpath()
            self.__world.save()
        self.__settings.save()

    def __dbg_cmd(self):
        self.__curr_zone.set('TEST')

    def __select_editor(self):
        
        editor = os.path.basename(self.__settings.script_editor)
        if editor == '': editor = self.__util.editor_uri

        path = fd.askopenfilename(initialdir=editor, title='File Editor', filetypes=[('', '.*')])

        if path == None or path == '':
            return
        
        self.__settings.script_editor = path
        self.__settings.save()

        print(f'Set editor to {path}')

    def __run_map(self, *args):

        save_path = ''
        map = ''

        # args = [self.__settings.script_editor, map.on_load.path]
        # subprocess.call(args)

        exec(open(self.__util.launch_uri).read())

        pass

    def __init_menu(self,cvc):

        lpath = self.__settings.last_opened
        if lpath != '':
            lname = os.path.basename(lpath)
            lname = f' ({lname})'

        menubar = Menu(cvc)
        filemenu = Menu(menubar, tearoff=0)
        scriptmenu = Menu(menubar, tearoff=0)
        helpmenu = Menu(menubar, tearoff=0)
        aboutmenu = Menu(menubar, tearoff=0)
        tilemenu = Menu(menubar, tearoff=0)
        testmenu = Menu(menubar, tearoff=0)
        dbgmenu = Menu(menubar, tearoff=0)
        show_blocking = BooleanVar(menubar, value=False)
        show_script = BooleanVar(menubar, value=False)
        
        filemenu.add_command(label='New World', command=self.__create_world)
        filemenu.add_command(label='Open', command=self.__load_world)
        filemenu.add_command(label='Recent'+lname, command=partial(self.__load_world, lpath))
        filemenu.add_separator()
        filemenu.add_command(label='Save', command=self.__save_world)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.__root.destroy)
        menubar.add_cascade(label='File', menu=filemenu)

        scriptmenu.add_command(label='Choose Editor', command=self.__select_editor)
        menubar.add_cascade(label='Script', menu=scriptmenu)

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

        testmenu.add_command(label='Run Map (F5)', command=self.__run_map)
        menubar.add_cascade(label='Testing', menu=testmenu)

        if self.__cfg.debug:
            dbgmenu.add_command(label='DBG CMD', command=self.__dbg_cmd)
            menubar.add_cascade(label='Debug', menu=dbgmenu)
        
        self.__root.config(menu=menubar)

    def show(self):
        self.__root.update()
        self.__root.mainloop()

    def __set_title(self, title:str=''):

        if title != '':
            title = ' *'+title.split('.')[0]

        self.__root.title('SWedit '+title)

    def __init_configs(self, path:str = None, enable_defaults:bool=False):
        self.__clear_data()
        self.__rsc_man = RSCManager(self.__root)
        if enable_defaults:
            self.__rsc_man.import_default_assets()
        self.__map_man = GridManager(self.__root)
        self.__world = WorldConfig(path, self.__rsc_man, self.__map_man)

    def __init_bindings(self, cvc:Tk):

        cvc.bind('<Control-s>', self.__save_world)

        cvc.bind('<F5>', self.__run_map)

    def __init__(self):

        self.__cfg = Config()

        self.__root = Tk()
        self.__util = GetUtil()
        self.__icons = GetIcons()
        self.__settings = EditorSettings()
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

        if self.__atlas != None: self.__atlas.destroy()
        if self.__map != None: self.__map.destroy()
        if self.__assetlib != None: self.__assetlib.destroy()

        self.__atlas = tkinter.Canvas(r)
        self.__map = tkinter.Canvas(r)
        self.__assetlib = tkinter.Canvas(r)
        
        self.__atlas.grid(sticky='NW', column=0, row=0)
        self.__map.grid(sticky='NW', column=1, row=0)
        self.__assetlib.grid(sticky='NE', column=2, row=0)

        self.__init_bindings(r)
        self.__init_menu(r)
        self.__adjust_win()
        self.__validate_ctrl_state()

