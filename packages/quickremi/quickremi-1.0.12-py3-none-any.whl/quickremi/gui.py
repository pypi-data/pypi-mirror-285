import remi.gui as tk
from datetime import datetime
import pytz

class GUI:

    '''
    class Creator v2
    '''


    def __init__(self):
        self.dt = ''
        self.tm = ''

    # ------------------------------------ INITIALIZER FUNCTIONS ------------------------------------------- ]


    def create_label(self, frame, H, W, L, T, text='.', bg='white', fg='black', fw='normal', ff='calibri',
                     align='center', justify='center', display='grid', bd_style='None', bd_radius='0px',
                     position='absolute', px=False, fs=0.8, margin='0px', bd_width='0px', bd_color='black',
                     overflow='auto', ta='center', hover='', alpha=1.0, wm='horizontal-tb', lh='-1px',
                     align_content='center'):

        '''
        Author Aru Raghuvanshi
        :param frame: container object
        :param H: float 0 to 100
        :param W: float 0 to 100
        :param L: float 0 to 100
        :param T: float 0 to 100
        :param text: str
        :param bg: str : label color, css colours or hex codes
        :param fg: str : text color, css colours or hex codes
        :param fw: str : font weight (bold, normal)
        :param ff: str: font family ('calibri')
        :param align: str: default 'center'
        :param align_content: str: default 'center' [flex-start, flex-end, center]
        :param justify: str: default 'center'
        :param display: str: default 'grid' [inline, grid, block, contents, flex, inline-flex, inline-block]
        :param bd_style: str : default 'None' (solid, dotted, dashed)
        :param bd_radius: str: default '0px'
        :param position: str: default 'absolute'
        :param px: bool : default False
        :param fs: float: font-size variable width default 0.8
        :param margin: str: default '0px'
        :param bd_width: str: default '0px'
        :param bd_color: str: default 'black'
        :param overflow: str: default 'auto' - adds scrollbar in case of overflowing content
        :param ta: str: text align : default 'center'
        :param hover: str: hover text when mouse over the label
        :param alpha: float: alpha of the colour of the label (0 to 1)
        :param wm: str: default 'horizontal-tb' (one of 'vertical-rl', 'vertical-lr', 'horizontal-tb')
        :param lh: str: line height or spacing between lines in px (default=-1')
        :return: label widget
        '''

        lbl = tk.Label(text=text)
        lbl.variable_name = 'lbl'
        if px:
            lbl.css_height = str(f'{H}px')
            lbl.css_width = str(f'{W}px')
            lbl.css_left = str(f'{L}px')
            lbl.css_top = str(f'{T}px')
            lbl.css_font_size = str(f'{fs}px')
        else:
            lbl.css_height = str(f'{H}%')
            lbl.css_width = str(f'{W}%')
            lbl.css_left = str(f'{L}%')
            lbl.css_top = str(f'{T}%')
            lbl.css_font_size = str(f'{fs}vw')
        lbl.attributes['title'] = hover
        lbl.css_margin = margin
        # lbl.css_font_size = fs
        lbl.css_background_color = bg
        lbl.css_color = fg
        lbl.css_align_self = align
        lbl.css_align_content = align_content
        lbl.css_align_items = align
        lbl.css_display = display
        lbl.css_position = position
        lbl.css_overflow = overflow
        lbl.css_justify_content = justify
        lbl.css_border_style = bd_style
        lbl.css_border_width = bd_width
        lbl.css_border_radius = bd_radius
        lbl.css_border_color = bd_color
        lbl.css_font_family = ff
        lbl.css_font_weight = fw
        lbl.css_text_align = ta
        lbl.css_opacity = alpha
        lbl.css_writing_mode = wm
        lbl.css_line_height = lh

        frame.append(lbl)
        return lbl


    def create_button(self, frame, H, W, L, T, command=None, text='.', bg='navyblue', fg='white', fw='normal',
                      align='center', justify='space-around', fs=0.8, bd_width='0px', ff='calibri', bd_color='black',
                      display='inline', position='absolute', px=False, bd_style='none', bd_radius='0px', bidx=None,
                      overflow='auto', ta='center', hover='', alpha=1.0, wm='horizontal-tb'):

        '''
        Author Aru Raghuvanshi
        :param frame: container object
        :param H: float 0 to 100
        :param W: float 0 to 100
        :param L: float 0 to 100
        :param T: float 0 to 100
        :param command : function to run on button press
        :param text: str
        :param bg: str : label color, css colours or hex codes
        :param fg: str : text color, css colours or hex codes
        :param fw: str : font weight (bold, normal)
        :param ff: str: font family ('calibri')
        :param align: str: default 'center'
        :param justify: str: default 'center'
        :param display: str: default 'grid'
        :param bd_style: str : default 'None' (solid, dotted, dashed)
        :param bd_radius: str: default '0px'
        :param position: str: default 'absolute'
        :param px: bool : default False
        :param fs: float: font-size variable width default 0.8
        :param margin: str: default '0px'
        :param bd_width: str: default '0px'
        :param bd_color: str: default 'black'
        :param overflow: str: default 'auto' - adds scrollbar in case of overflowing content
        :param ta: str: text align : default 'center'
        :param hover: str: hover text when mouse over the label
        :param alpha: float: alpha of the colour of the label (0 to 1)
        :param wm: str: default 'horizontal-tb' (one of 'vertical-rl', 'vertical-lr', 'horizontal-tb')
        :return: Button widget
        '''

        btn = tk.Button(text=text)

        if px:
            btn.variable_name = bidx
            btn.css_height = str(f'{H}px')
            btn.css_width = str(f'{W}px')
            btn.css_left = str(f'{L}px')
            btn.css_top = str(f'{T}px')
            btn.css_font_size = str(f'{fs}px')
        else:
            btn.variable_name = 'btn'
            btn.css_height = str(f'{H}%')
            btn.css_width = str(f'{W}%')
            btn.css_left = str(f'{L}%')
            btn.css_top = str(f'{T}%')
            btn.css_font_size = str(f'{fs}vw')
        btn.attributes['title']= hover
        btn.css_background_color = bg
        btn.css_color = fg
        btn.css_align_self = align
        btn.css_align_content = align
        btn.css_align_items = align
        btn.css_display = display
        btn.css_justify_content = align
        btn.css_position = position
        btn.css_justify_content = justify
        btn.css_border_style = bd_style
        btn.css_border_width = bd_width
        btn.css_border_radius = bd_radius
        btn.css_border_color = bd_color
        btn.css_overflow = overflow
        btn.css_font_weight = fw
        btn.css_font_family = ff
        btn.css_text_align = ta
        btn.css_opacity = alpha
        btn.css_writing_mode = wm
        btn.onclick.do(command)
        frame.append(btn)
        return btn


    def create_uploader(self, frame, H, W, L, T, filename, bg='navyblue', fg='white',
                        align='center', justify='space-around', command_succ=None, command_fail=None,
                        display='inline', position='absolute', px=False, bd_style='None', bd_radius='0px',
                        bd_color='black', bd_width='0px'):

        '''
         Author Aru Raghuvanshi
        :param frame: container object
        :param H: float 0 to 100
        :param W: float 0 to 100
        :param L: float 0 to 100
        :param T: float 0 to 100
        :param filename : str: path of file to be uploaded
        :param bg: str : label color, css colours or hex codes
        :param fg: str : text color, css colours or hex codes
        :param align: str: default 'center'
        :param justify: str: default 'center'
        :param display: str: default 'grid'
        :param bd_style: str : default 'None' (solid, dotted, dashed)
        :param bd_radius: str: default '0px'
        :param position: str: default 'absolute'
        :param px: bool : default False
        :param bd_width: str: default '0px'
        :param bd_color: str: default 'black'
        :return: Uploader widget
        '''

        btn = tk.FileUploader(savepath=filename)

        if px:
            btn.variable_name = 'upl'
            btn.css_height = str(f'{H}px')
            btn.css_width = str(f'{W}px')
            btn.css_left = str(f'{L}px')
            btn.css_top = str(f'{T}px')
        else:
            btn.variable_name = 'btn'
            btn.css_height = str(f'{H}%')
            btn.css_width = str(f'{W}%')
            btn.css_left = str(f'{L}%')
            btn.css_top = str(f'{T}%')
        btn.css_background_color = bg
        btn.css_color = fg
        btn.css_align_self = align
        btn.css_align_content = align
        btn.css_align_items = align
        btn.css_display = display
        btn.css_justify_content = align
        btn.css_position = position
        btn.css_justify_content = justify
        btn.css_border_style = bd_style
        btn.css_border_width = bd_width
        btn.css_border_radius = bd_radius
        btn.css_border_color = bd_color
        frame.append(btn)
        btn.onsuccess.do(command_succ)
        btn.onfailed.do(command_fail)
        return btn


    def create_container(self, frame, H, W, L, T, bg='whitesmoke', fg='black', bd_radius='0px', bd_style='None',
                         align='center', justify='space-around', overflow='auto', fs=0.8,
                         display='space-around', position='absolute', px=False, bd_width='0px', bd_color='black'):

        '''
        Author Aru Raghuvanshi
        :param frame: container object
        :param H: float 0 to 100
        :param W: float 0 to 100
        :param L: float 0 to 100
        :param T: float 0 to 100
        :param bg: str : label color, css colours or hex codes
        :param fg: str : text color, css colours or hex codes
        :param align: str: default 'center'
        :param justify: str: default 'center'
        :param display: str: default 'grid'
        :param bd_style: str : default 'None' (solid, dotted, dashed)
        :param bd_radius: str: default '0px'
        :param position: str: default 'absolute'
        :param px: bool : default False
        :param fs: float: font-size variable width default 0.8
        :param bd_width: str: default '0px'
        :param bd_color: str: default 'black'
        :param overflow: str: default 'auto' - adds scrollbar in case of overflowing content
        :return: Container widget
        '''

        btn = tk.Container()
        if px:
            btn.variable_name = 'ctn'
            btn.css_height = str(f'{H}px')
            btn.css_width = str(f'{W}px')
            btn.css_left = str(f'{L}px')
            btn.css_top = str(f'{T}px')
            btn.css_font_size = str(f'{fs}px')
        else:
            btn.variable_name = 'btn'
            btn.css_height = str(f'{H}%')
            btn.css_width = str(f'{W}%')
            btn.css_left = str(f'{L}%')
            btn.css_top = str(f'{T}%')
            btn.css_font_size = str(f'{fs}vw')
        btn.css_border_radius = bd_radius
        btn.css_border_style = bd_style
        btn.css_border_width = bd_width
        btn.css_border_color = bd_color
        btn.css_overflow = overflow
        btn.css_background_color = bg
        btn.css_color = fg
        btn.css_align_self = align
        btn.css_align_content = align
        btn.css_align_items = align
        btn.css_display = display
        btn.css_justify_content = align
        btn.css_position = position
        btn.css_justify_content = justify
        frame.append(btn)
        return btn


    def create_table(self, frame, lst, H, W, L, T, bg='seashell', fg='black', overflow='scroll',
                     align_self='center', align_content='center', align_items='center', margin='2px',
                     justify_content='center', fs=0.8, flex_wrap='wrap', bd_color='black',
                     display='space-around', position='absolute', px=False, bd_width='3px',
                     fw='normal', ff='calibri'):

        '''
        Author Aru Raghuvanshi
        :param frame: container object
        :param H: float 0 to 100
        :param W: float 0 to 100
        :param L: float 0 to 100
        :param T: float 0 to 100
        :param bg: str : label color, css colours or hex codes
        :param fg: str : text color, css colours or hex codes
        :param fw: str : font weight (bold, normal)
        :param ff: str: font family ('calibri')
        :param display: str: default 'grid'
        :param justify_content: str 'center'
        :param align_content: str: 'center'
        :param align_self: str: 'center'
        :param flex_wrap: str: 'wrap'
        :param bd_color: str: 'black
        :param bd_width: str: '3px'
        :param position: str: default 'absolute'
        :param px: bool : default False
        :param fs: float: font-size variable width default 0.8
        :param margin: str: default '0px'
        :param overflow: str: default 'auto' - adds scrollbar in case of overflowing content
        :return: Table widget
        '''

        btn = tk.Table.new_from_list(content=lst)
        if px:
            btn.variable_name = 'tbl'
            btn.css_height = str(f'{H}px')
            btn.css_width = str(f'{W}px')
            btn.css_left = str(f'{L}px')
            btn.css_top = str(f'{T}px')
        else:
            btn.variable_name = 'tbl'
            btn.css_height = str(f'{H}%')
            btn.css_width = str(f'{W}%')
            btn.css_left = str(f'{L}%')
            btn.css_top = str(f'{T}%')
        btn.css_font_size = fs
        btn.css_background_color = bg
        btn.css_color = fg
        btn.css_align_self = align_self
        btn.css_align_content = align_content
        btn.css_align_items = align_items
        btn.css_display = display
        btn.css_justify_content = justify_content
        btn.css_position = position
        btn.css_overflow = overflow
        btn.css_flex_wrap = flex_wrap
        btn.css_border_color = bd_color
        btn.css_border_width = bd_width
        btn.css_font_weight = fw
        btn.css_font_family = ff
        btn.css_margin = margin
        frame.append(btn)
        return btn



    def create_image(self, frame, imagepath, H, W, L, T, h=100, w=100, bg='navyblue', fg='white',
                     align='center', justify='space-around',
                     display='inline', position='absolute', px=False):
        '''
        Author Aru Raghuvanshi
        :param frame: container object
        :param imagepath: str: path of imagefile
        :param H: float 0 to 100
        :param W: float 0 to 100
        :param L: float 0 to 100
        :param T: float 0 to 100
        :param h: float 0 to 100 default 100 (height of the image within container)
        :param w: float 0 to 100 default 100 (height of the image within container)
        :param bg: str : label color, css colours or hex codes
        :param fg: str : text color, css colours or hex codes
        :param display: str: default 'inline'
        :param justify: str 'space-around'
        :param align: str: 'center'
        :param position: str: default 'absolute'
        :param px: bool : default False
        :return: Image widget
        '''


        btn = tk.Image(tk.load_resource(imagepath), h=f'{h}%', w=f'{w}%')

        # btn.set_image(imagepath)
        if px:
            btn.variable_name = 'img'
            btn.css_height = str(f'{H}px')
            btn.css_width = str(f'{W}px')
            btn.css_left = str(f'{L}px')
            btn.css_top = str(f'{T}px')
        else:
            btn.variable_name = 'btn'
            btn.css_height = str(f'{H}%')
            btn.css_width = str(f'{W}%')
            btn.css_left = str(f'{L}%')
            btn.css_top = str(f'{T}%')
        btn.css_background_color = bg
        btn.css_color = fg
        btn.css_align_self = align
        btn.css_align_content = align
        btn.css_align_items = align
        btn.css_display = display
        btn.css_justify_content = align
        btn.css_position = position
        btn.css_justify_content = justify
        frame.append(btn)
        return btn


    def create_listview(self, frame, lst, H, W, L, T, command=None, bg='skyblue', fg='black',
                        align='center', justify='space-around', fs=0.8, bd_radius='0px',
                        display='inline', position='absolute', px=False, fw='normal', ff='calibri'):

        '''
        Author Aru Raghuvanshi
        Usage:

        lst = ['Tiger', 'Lion', 'Jaguar']
        lv = C.create_listview(frame, lst, 40, 50, 5, 5, command=on_selection)
        def on_selection(w, val):
            print(f'val: {lv.children[val].get_text()}')

        :param frame: container object
        :param lst: list: iterable containing items to display in listview
        :param H: float 0 to 100
        :param W: float 0 to 100
        :param L: float 0 to 100
        :param T: float 0 to 100
        :param command: function to run on select
        :param bg: str : label color, css colours or hex codes
        :param fg: str : text color, css colours or hex codes
        :param fw: str : font weight (bold, normal)
        :param ff: str: font family ('calibri')
        :param fs: float: font-size variable width default 0.8
        :param display: str: default 'inline'
        :param justify: str 'space-around'
        :param align: str: 'center'
        :param position: str: default 'absolute'
        :param px: bool : default False
        :return: Listview widget
        '''

        btn = tk.ListView.new_from_list(items=lst)

        if px:
            btn.variable_name = 'lvw'
            btn.css_height = str(f'{H}px')
            btn.css_width = str(f'{W}px')
            btn.css_left = str(f'{L}px')
            btn.css_top = str(f'{T}px')
        else:
            btn.variable_name = 'btn'
            btn.css_height = str(f'{H}%')
            btn.css_width = str(f'{W}%')
            btn.css_left = str(f'{L}%')
            btn.css_top = str(f'{T}%')
            btn.css_font_size = str(f'{fs}vs')
        # btn.css_font_size = fs
        btn.css_background_color = bg
        btn.css_color = fg
        btn.css_align_self = align
        btn.css_align_content = align
        btn.css_align_items = align
        btn.css_display = display
        btn.css_position = position
        btn.css_justify_content = justify
        btn.css_border_radius = bd_radius
        btn.css_font_weight = fw
        btn.css_font_family = ff
        btn.onselection.do(command)
        frame.append(btn)
        return btn


    def create_progress(self, frame, H, W, L, T, a, b=100, bg='lightgreen', fg='pink',
                        align='center', justify='space-around',
                        display='inline', position='absolute', px=False):

        '''Author Aru Raghuvanshi
        :param frame: container object
        :param H: float 0 to 100
        :param W: float 0 to 100
        :param L: float 0 to 100
        :param T: float 0 to 100
        :param a: start position of progress bar
        :param b: float : end position of progress bar (default 100)
        :param bg: str : label color, css colours or hex codes
        :param fg: str : text color, css colours or hex codes
        :param display: str: default 'inline'
        :param justify: str 'space-around'
        :param align: str: 'center'
        :param position: str: default 'absolute'
        :param px: bool : default False
        :return: Progressbar widget'''

        btn = tk.Progress(a, b)
        if px:
            btn.variable_name = 'prg'
            btn.css_height = str(f'{H}px')
            btn.css_width = str(f'{W}px')
            btn.css_left = str(f'{L}px')
            btn.css_top = str(f'{T}px')
        else:
            btn.variable_name = 'btn'
            btn.css_height = str(f'{H}%')
            btn.css_width = str(f'{W}%')
            btn.css_left = str(f'{L}%')
            btn.css_top = str(f'{T}%')
        btn.css_background_color = bg
        btn.css_color = fg
        btn.css_align_self = align
        btn.css_align_content = align
        btn.css_align_items = align
        btn.css_display = display
        btn.css_justify_content = align
        btn.css_position = position
        btn.css_justify_content = justify
        frame.append(btn)
        return btn


    def create_dropdown(self, frame, lst, H, W, L, T, command=None, bg='navyblue', fg='black',
                        align='center', justify='space-around', fs=0.7,
                        display='inline', position='absolute', px=False):

        '''Author Aru Raghuvanshi
        :param frame: container object
        :param lst: List (members to populate in the dropdown)
        :param H: float 0 to 100
        :param W: float 0 to 100
        :param L: float 0 to 100
        :param T: float 0 to 100
        :param command: function to run on selection
        :param bg: str : label color, css colours or hex codes
        :param fg: str : text color, css colours or hex codes
        :param fs: float: font-size variable width default 0.7
        :param display: str: default 'inline'
        :param justify: str 'space-around'
        :param align: str: 'center'
        :param position: str: default 'absolute'
        :param px: bool : default False
        :return: Dropdown widget'''

        btn = tk.DropDown.new_from_list(lst)
        if px:
            btn.variable_name = 'drp'
            btn.css_height = str(f'{H}px')
            btn.css_width = str(f'{W}px')
            btn.css_left = str(f'{L}px')
            btn.css_top = str(f'{T}px')
            btn.css_font_size = str(f'{fs}px')
        else:
            btn.variable_name = 'btn'
            btn.css_height = str(f'{H}%')
            btn.css_width = str(f'{W}%')
            btn.css_left = str(f'{L}%')
            btn.css_top = str(f'{T}%')
            btn.css_font_size = str(f'{fs}vw')
        btn.css_background_color = bg
        btn.css_color = fg
        btn.css_align_self = align
        btn.css_align_content = align
        btn.css_align_items = align
        btn.css_display = display
        btn.css_justify_content = align
        btn.css_position = position
        btn.css_justify_content = justify
        btn.select_by_value(lst[0])
        btn.onchange.do(command)
        frame.append(btn)
        return btn


    def create_entry(self, frame, H, W, L, T, command=None, bg='white', fg='black', fw='normal', overflow='visible',
                     align='center', justify='space-around', input_type='regular', ff='calibri',
                     display='inline', position='absolute', px=False, fs=0.8, bd_radius='0px',
                     bd_style='None', bd_width='0px', bd_color='black'):

        '''
        Author Aru Raghuvanshi
        :param frame: container object
        :param H: float 0 to 100
        :param W: float 0 to 100
        :param L: float 0 to 100
        :param T: float 0 to 100
        :param command: Function to run on user input
        :param bg: str : label color, css colours or hex codes
        :param fg: str : text color, css colours or hex codes
        :param fw: str : font weight (bold, normal)
        :param ff: str: font family ('calibri')
        :param input_type: str: one of 'regular' or 'password' default: 'regular'
        :param align: str: default 'center'
        :param justify: str: default 'center'
        :param display: str: default 'grid'
        :param bd_style: str : default 'None' (solid, dotted, dashed)
        :param bd_radius: str: default '0px'
        :param position: str: default 'absolute'
        :param px: bool : default False
        :param fs: float: font-size variable width default 0.8
        :param bd_width: str: default '0px'
        :param bd_color: str: default 'black'
        :param overflow: str: default 'visible'
        :return: Entry widget.
        '''

        if input_type == 'password':
            btn = tk.Input(input_type='password')
            btn.attributes['type'] = 'password'
            btn.style['background-color'] = 'lightgray'
            btn.onchange.connect(command)
        elif input_type == 'text':
            btn = tk.TextInput()
        else:
            btn = tk.Input()
            btn.style['background-color'] = 'lightgray'

        if px:
            btn.variable_name = 'drp'
            btn.css_height = str(f'{H}px')
            btn.css_width = str(f'{W}px')
            btn.css_left = str(f'{L}px')
            btn.css_top = str(f'{T}px')
            btn.css_font_size = str(f'{fs}px')
        else:
            btn.variable_name = 'btn'
            btn.css_height = str(f'{H}%')
            btn.css_width = str(f'{W}%')
            btn.css_left = str(f'{L}%')
            btn.css_top = str(f'{T}%')
            btn.css_font_size = str(f'{fs}vw')

        btn.css_border_radius = bd_radius
        btn.css_border_style = bd_style
        btn.css_border_width = bd_width
        btn.css_border_color = bd_color
        btn.css_background_color = bg
        btn.css_color = fg
        btn.css_align_self = align
        btn.css_align_content = align
        btn.css_align_items = align
        btn.css_display = display
        btn.css_justify_content = align
        btn.css_position = position
        btn.css_justify_content = justify
        btn.css_overflow = overflow
        btn.css_font_weight = fw
        btn.css_font_family = ff
        btn.onchange.do(command)
        frame.append(btn)
        return btn


    def create_input_dialogue(self, frame, H, W, L, T, title='ttl', message='desc',
                             command=None, bg='navyblue', fg='white', fs=0.8,
                             align='center', justify='space-around',
                             display='inline', position='absolute', px=False):

        '''Creates input dialogue and returns the input dialogue widget'''

        btn = tk.InputDialog(title=title, message=message)
        btn.confirm_value.do(command)

        if px:
            btn.variable_name = 'drp'
            btn.css_height = str(f'{H}px')
            btn.css_width = str(f'{W}px')
            btn.css_left = str(f'{L}px')
            btn.css_top = str(f'{T}px')
        else:
            btn.variable_name = 'btn'
            btn.css_height = str(f'{H}%')
            btn.css_width = str(f'{W}%')
            btn.css_left = str(f'{L}%')
            btn.css_top = str(f'{T}%')
            btn.css_font_size = str(f'{fs}vw')
        btn.css_background_color = bg
        btn.css_color = fg
        btn.css_align_self = align
        btn.css_align_content = align
        btn.css_align_items = align
        btn.css_display = display
        btn.css_justify_content = align
        btn.css_position = position
        btn.css_justify_content = justify
        frame.append(btn)
        return btn


    def create_date_picker(self, frame, H, W, L, T, command=None, bg='white', fg='black', overflow='visble',
                           align='center', justify='space-around', fs=0.7, bd_width='0px',
                           margin='0px', bd_color='black',
                           display='inline-flex', position='absolute', px=False, bd_style='none', bd_radius='0px'):

        '''Author Aru Raghuvanshi
        :param frame: container object
        :param H: float 0 to 100
        :param W: float 0 to 100
        :param L: float 0 to 100
        :param T: float 0 to 100
        :param command : function to run on button press
        :param bg: str : label color, css colours or hex codes
        :param fg: str : text color, css colours or hex codes
        :param align: str: default 'center'
        :param justify: str: default 'space-around'
        :param display: str: default 'inline-flex'
        :param bd_style: str : default 'None' (solid, dotted, dashed)
        :param bd_radius: str: default '0px'
        :param position: str: default 'absolute'
        :param px: bool : default False
        :param fs: float: font-size variable width default 0.7
        :param margin: str: default '0px'
        :param bd_width: str: default '0px'
        :param bd_color: str: default 'black'
        :param overflow: str: default 'visible'
        :return: Date Picker widget'''

        def utc2local():
            tzInfo = pytz.timezone('Asia/Kolkata')
            dttm = datetime.now(tz=tzInfo)
            dttm = dttm.strftime('%d-%m-%Y %H:%M:%S')
            dttm = str(dttm)[:16]
            dt = dttm.split(' ')[0]
            tm = dttm.split(' ')[1]
            # C.pr('date', dt, 'y')
            # C.pr('time', tm, 'y')
            return dt, tm

        date, tm = utc2local()
        btn = tk.Date(default_value=date)
        if px:
            btn.variable_name = 'btn'
            btn.css_height = str(f'{H}px')
            btn.css_width = str(f'{W}px')
            btn.css_left = str(f'{L}px')
            btn.css_top = str(f'{T}px')
            btn.css_top = str(f'{fs}px')
        else:
            btn.variable_name = 'btn'
            btn.css_height = str(f'{H}%')
            btn.css_width = str(f'{W}%')
            btn.css_left = str(f'{L}%')
            btn.css_top = str(f'{T}%')
            btn.css_top = str(f'{fs}vw')
        btn.css_overflow = overflow
        btn.css_background_color = bg
        btn.css_color = fg
        btn.css_align_self = align
        btn.css_align_content = align
        btn.css_align_items = align
        btn.css_display = display
        btn.css_justify_content = align
        btn.css_position = position
        btn.css_justify_content = justify
        btn.css_border_style = bd_style
        btn.css_border_width = bd_width
        btn.css_border_radius = bd_radius
        btn.css_border_color = bd_color
        btn.css_margin = margin
        btn.onchange.do(command)
        frame.append(btn)
        return btn


    def create_downloader(self, frame, H, W, L, T, text, file, bg='whitesmoke', fg='black', ff='calibri',
                          align='center', justify='space-around', fs=0.8, bd_radius='0px', fw='normal',
                          display='inline', position='absolute', px=False):

        '''Creates downloader and returns the downloader widget'''

        btn = tk.FileDownloader(text=text, filename=file)

        if px:
            btn.variable_name = 'upl'
            btn.css_height = str(f'{H}px')
            btn.css_width = str(f'{W}px')
            btn.css_left = str(f'{L}px')
            btn.css_top = str(f'{T}px')
        else:
            btn.variable_name = 'btn'
            btn.css_height = str(f'{H}%')
            btn.css_width = str(f'{W}%')
            btn.css_left = str(f'{L}%')
            btn.css_top = str(f'{T}%')
            btn.css_font_size = str(f'{fs}vw')
        btn.css_font_family = ff
        btn.css_font_weight = fw
        btn.css_background_color = bg
        btn.css_color = fg
        btn.css_align_self = align
        btn.css_align_content = align
        btn.css_align_items = align
        btn.css_display = display
        btn.css_justify_content = align
        btn.css_position = position
        btn.css_justify_content = justify
        btn.css_border_radius = bd_radius
        frame.append(btn, key='file_downloader')
        return btn


    def create_label_checkbox(self, frame, H, W, L, T, text, command=None, val=False, bd_radius='0px',
                              bg='whitesmoke', fg='black', justify='space-around', fs=0.7,
                              ff='calibri', fw='normal', display='flex', position='absolute', px=False):

        '''Author Aru Raghuvanshi
        :param frame: container object
        :param H: float 0 to 100
        :param W: float 0 to 100
        :param L: float 0 to 100
        :param T: float 0 to 100
        :param text : Text on Checkbox Label
        :param command : function to run on button press
        :param bg: str : label color, css colours or hex codes
        :param fg: str : text color, css colours or hex codes
        :param justify: str: default 'space-around'
        :param display: str: default 'flex'
        :param position: str: default 'absolute'
        :param px: bool : default False
        :param fs: float: font-size variable width default 0.7
        :return: Label Checkbox widget'''

        btn = tk.CheckBoxLabel(text, val)

        if px:
            btn.variable_name = 'upl'
            btn.css_height = str(f'{H}px')
            btn.css_width = str(f'{W}px')
            btn.css_left = str(f'{L}px')
            btn.css_top = str(f'{T}px')
            btn.css_font_size = str(f'{fs}px')
        else:
            btn.variable_name = 'btn'
            btn.css_height = str(f'{H}%')
            btn.css_width = str(f'{W}%')
            btn.css_left = str(f'{L}%')
            btn.css_top = str(f'{T}%')
            btn.css_font_size = str(f'{fs}vw')
        btn.css_background_color = bg
        btn.css_color = fg
        btn.css_align_self = 'auto'
        btn.css_align_content = 'stretch'
        btn.css_align_items = 'center'
        btn.css_display = display
        btn.css_border_radius = bd_radius
        btn.css_position = position
        btn.css_font_weight = fw
        btn.css_font_family = ff
        btn.css_justify_content = justify
        btn.onchange.do(command)
        frame.append(btn)
        return btn


    def create_slider(self, frame, H, W, L, T, max, min, command=None, step=1, px=False, fs=0.8,
                      bg='whitesmoke', bd_radius='0px', bd_style='none', bd_width='0px', bd_color='black',
                      position='absolute'):

        '''
         Author Aru Raghuvanshi
        :param frame: container object
        :param H: float 0 to 100
        :param W: float 0 to 100
        :param L: float 0 to 100
        :param T: float 0 to 100
        :param command : function to run on button press
        :param bd_style: str : default 'None' (solid, dotted, dashed)
        :param bd_radius: str: default '0px'
        :param bd_color: str : default 'black'
        :param bd_width: str: default '0px'
        :param bg: str : label color, css colours or hex codes
        :param position: str: default 'absolute'
        :param px: bool : default False
        :param fs: float: font-size variable width default 0.8
        :return: Slider Widget widget'''

        btn = tk.Slider(default_value=0, min=min, max=max, step=step)

        if px:
            btn.variable_name = 'sld'
            btn.css_height = str(f'{H}px')
            btn.css_width = str(f'{W}px')
            btn.css_left = str(f'{L}px')
            btn.css_top = str(f'{T}px')
            btn.css_font_size = str(f'{fs}px')
        else:
            btn.variable_name = 'btn'
            btn.css_height = str(f'{H}%')
            btn.css_width = str(f'{W}%')
            btn.css_left = str(f'{L}%')
            btn.css_top = str(f'{T}%')
            btn.css_font_size = str(f'{fs}vw')
        btn.css_position = position
        btn.css_background_color = bg
        btn.css_border_style = bd_style
        btn.css_border_width = bd_width
        btn.css_border_radius = bd_radius
        btn.css_border_color = bd_color
        btn.onchange.do(command)
        frame.append(btn)
        return btn


    def create_spinbox(self, frame, H, W, L, T, max, min, command=None, step=1, px=False, fs=0.8,
                      bg='whitesmoke', bd_radius='0px', bd_style='none', bd_width='0px', bd_color='black',
                      position='absolute', allow_editing=True):

        '''
         Author Aru Raghuvanshi
        :param frame: container object
        :param H: float 0 to 100
        :param W: float 0 to 100
        :param L: float 0 to 100
        :param T: float 0 to 100
        :param command : function to run on button press
        :param bd_style: str : default 'None' (solid, dotted, dashed)
        :param bd_radius: str: default '0px'
        :param bd_color: str : default 'black'
        :param bd_width: str: default '0px'
        :param bg: str : label color, css colours or hex codes
        :param position: str: default 'absolute'
        :param px: bool : default False
        :param fs: float: font-size variable width default 0.8
        :param allow_editing: bool : default True (Change values manually)
        :return: Slider Widget widget'''

        btn = tk.SpinBox(default_value=0, min_value=min, max_value=max, step=step, allow_editing=allow_editing)

        if px:
            btn.variable_name = 'spn'
            btn.css_height = str(f'{H}px')
            btn.css_width = str(f'{W}px')
            btn.css_left = str(f'{L}px')
            btn.css_top = str(f'{T}px')
            btn.css_font_size = str(f'{fs}px')
        else:
            btn.variable_name = 'btn'
            btn.css_height = str(f'{H}%')
            btn.css_width = str(f'{W}%')
            btn.css_left = str(f'{L}%')
            btn.css_top = str(f'{T}%')
            btn.css_font_size = str(f'{fs}vw')
        btn.css_position = position
        btn.css_background_color = bg
        btn.css_border_style = bd_style
        btn.css_border_width = bd_width
        btn.css_border_radius = bd_radius
        btn.css_border_color = bd_color
        btn.onchange.do(command)
        frame.append(btn)
        return btn


    def show_html(self, frame, htmlcontent, H, W, L, T, w=100, h=100, margin='4px',
                  border='1px solid black'):
        '''

        Author Aru Raghuvanshi
        :param frame: container object
        :param htmlcontent: str: path to html file
        :param H: float 0 to 100
        :param W: float 0 to 100
        :param L: float 0 to 100
        :param T: float 0 to 100
        :param w : float 0 to 100 default 100 (width of image in container)
        :param h : float 0 to 100 default 100 (width of image in container)
        :param margin: str: default '4px'
        :return: HTML in a container
        '''
        mc = gui.create_container(frame, H, W, L, T)

        frame = tk.Widget(_type='iframe', width=w, height=h, margin=margin)
        frame.attributes['src'] = htmlcontent
        frame.attributes['width'] = f'{w}%'
        frame.attributes['height'] = f'{h}%'
        frame.style['border'] = border

        mc.add_child('frame', frame)
        return frame


    def show_plotly(self, frame, htmlcontent, H, W, L, T, w=100, h=100, margin='0px',
                    border='1px solid black'):

        '''
        Author Aru Raghuvanshi
        :param frame: container object
        :param htmlcontent: str: path to html plotly file
        :param H: float 0 to 100
        :param W: float 0 to 100
        :param L: float 0 to 100
        :param T: float 0 to 100
        :param w : float 0 to 100 default 100 (width of image in container)
        :param h : float 0 to 100 default 100 (width of image in container)
        :param margin: str: default '0px'
        :return: plotly chart in a container
        '''
        mc = gui.create_container(frame, H, W, L, T)

        res = tk.load_resource(htmlcontent)
        btn = tk.Widget(_type='iframe', margin=margin)
        btn.attributes['src'] = res
        btn.attributes['width'] = f'{w}%'
        btn.attributes['height'] = f'{h}%'
        btn.style['border'] = border

        mc.add_child('frame', btn)
        # window.append(main_container)
        # returning the root widget
        return frame


# ------------------------------------ CALLERS -------------------------------------------------------------- ]


    def label(self, frame, H, W, L, T, text, bg='whitesmoke', fg='black', fw='normal', ff='calibri',
              align='center', justify='center', display='grid', bd_style='None', bd_radius='0px',
              position='absolute', px=False, fs=0.7, margin='0px', bd_width='0px', overflow='auto'):

        '''Author: Aru Raghuvanshi
        Use this to create label that can be deleted like a container.
        Creates label and returns the container'''

        frm = self.create_container(frame, H, W, L, T, bg=bg, bd_radius=bd_radius, overflow='visible')

        lbl = self.create_label(frm, 90, 99, 0, 0, text=text, bg=bg, fg=fg, fw=fw, ff=ff, overflow=overflow,
                                align=align, justify=justify, display=display, bd_style=bd_style, bd_radius=bd_radius,
                                position=position, px=px, fs=fs, margin=margin, bd_width=bd_width)
        frm.append(lbl)
        return frm, lbl


    def labels(self, frame, H1, W1, L1, T1, H2, W2, L2, T2, text, text2, ff='calibri', hover='', hover2='',
                     bg='white', fg='black', bg2='white', fg2='black', fs=0.75, fs2=0.75, bd_radius='0px',
                     bd_radius2='0px', fw1='normal', fw2='normal', align1='center', align2='center',
                     justify1='center', justify2='center', bd_width='0px', bd_width2='0px', ta='center',
                     bd_color='black', bd_color2='black', bd_style='none', bd_style2='none', ta2='center'):
        '''
        Author: Aru Raghuvanshi
        This will create labels side by side.
        :return: two label widgets
        '''
        l1 = self.create_label(frame, H1, W1, L1, T1, bd_radius=bd_radius, ff=ff, justify=justify1,
                              text=text, bg=bg, fg=fg, fs=fs, fw=fw1, align=align1, bd_width=bd_width,
                               bd_color=bd_color, bd_style=bd_style, ta=ta, hover=hover)
        l2 = self.create_label(frame, H2, W2, L2, T2, bd_radius=bd_radius2, ff=ff, justify=justify2,
                              text=text2, bg=bg2, fg=fg2, fs=fs2, fw=fw2, align=align2, bd_width=bd_width2,
                               bd_color=bd_color2, bd_style=bd_style2, ta=ta2, hover=hover2)
        return l1, l2


    def button(self, frame, H, W, L, T, command=None, text='.', bg='navyblue', fg='white', fw='normal',
               align='center', justify='space-around', fs=0.8, bd_width='0px', ff='calibri',
               display='inline', position='absolute', px=False, bd_style='None', bd_radius='0px', bd_color='white'):

        '''Creates button and returns the container'''

        frm = self.create_container(frame, H, W, L, T, bg=bg, bd_radius=bd_radius)
        btn = self.create_button(frm, 99, 100, 0, 0, command=command, text=text, bg=bg, fg=fg, fw=fw, ff=ff,
                                 align=align, justify=justify, display=display, bd_style=bd_style, bd_radius=bd_radius,
                                 position=position, px=px, fs=fs, bd_width=bd_width, bd_color=bd_color)

        frm.append(btn)
        return frm


    def table(self, frame, df, H, W, L, T, header, bg='seashell', fg='black', overflow='auto',
              align_self='center', align_content='center', align_items='center', margin='2px',
              justify_content='center', fs=0.7, flex_wrap='wrap', bc='black', bgc='whitesmoke',
              display='space-around', position='absolute', px=False, bw='3px', fw='normal', ff='calibri'):

        '''Creates table and returns the container'''

        res = []
        dc = df.T
        for column in dc.columns:
            li = dc[column].tolist()
            res.append(li)

        res.insert(0, header)

        frm = self.create_container(frame, H, W, L, T, bg=bgc, overflow='auto')

        tbl = gui.create_table(frm, res, 99, 99, 0, 0, bg=bg, fg=fg, overflow=overflow,
                             align_self=align_self, align_content=align_content, align_items=align_items, margin=margin,
                             justify_content=justify_content, fs=fs, flex_wrap=flex_wrap, bd_color=bc,
                             display=display, position=position, px=px, bd_width=bw, fw=fw, ff=ff)
        frm.append(tbl)
        return frm


    def dropdown(self, frame, lst, H, W, L, T, command=None,
                       bg='white', fg='black', fs=0.7, bgc='whitesmoke'):

        '''Creates dropdown and returns the container'''

        frm = self.create_container(frame, H, W, L, T, bg=bgc)

        d = self.create_dropdown(frm, lst, 99, 99, 0, 0,
                                 fg=fg, bg=bg, command=command, fs=fs)
        frm.append(d)
        return frm


    def entry(self, frame, H, W, L, T, command=None,
                    bg='white', fg='black', fs=0.7, bgc='whitesmoke',
                    bd_radius='0px', bw='0px'):

        '''Creates entry field and returns the container'''

        frm = self.create_container(frame, H, W, L, T, bg=bgc, overflow='visible')

        e = self.create_entry(frm, 99, 99, 1, 1, command=command, fs=fs,
                              fg=fg, bg=bg, bd_width=bw, bd_radius=bd_radius)

        frm.append(e)
        return frm




    def date(self, frame, H, W, L, T, command=None,
                   bg='white', fg='white', bgc='whitesmoke', fs=0.8,
                   bd_radius='0px'):

        '''Creates date picker and returns the container'''

        frm = self.create_container(frame, H, W, L, T, bg=bgc, overflow='visible')

        d = gui.create_date_picker(frm, 98, 99, 0, 0, command=command, bg=bg, fg=fg,
                             bd_radius=bd_radius, fs=fs, align='center', justify='space-between')
        frm.append(d)
        return frm


    def checkbox(self, frame, H, W, L, T, text, ff='calibri', command=None,
                 bg='white', fg='black',fs=0.8, bd_radius='0px', bgc='whitesmoke'):

        '''Creates label checkbox and returns the container'''

        frm = self.create_container(frame, H, W, L, T, bg=bgc, overflow='visible')

        c = self.create_label_checkbox(frm, 99, 99, 0, 0, ff=ff, text=text, bg=bg,
                                       fg=fg, command=command, fs=fs, bd_radius=bd_radius)
        frm.append(c)
        return frm


    def downloader(self, frame, H, W, L, T, text, file, ff='calibri', bgc='azure',
                 bg='white', fg='black', fs=0.8, bd_radius='0px'):

        '''Creates downloader and returns the container'''

        frm = self.create_container(frame, H, W, L, T, bg=bgc)

        d = self.create_downloader(frame, 99, 99, 0, 0, text, file, bg=bg, fg=fg, fs=fs,
                                   ff=ff, bd_radius=bd_radius)
        frm.append(d)
        return frm


    def listview(self, frame, H, W, L, T, lst, ff='calibri', command=None,
                 bg='whitesmoke', fg='black', fs=0.8, bd_radius='0px', bgc='whitesmoke'):

        '''Creates listview and returns the container'''

        frm = self.create_container(frame, H, W, L, T, bg=bgc, overflow='auto')

        c = self.create_listview(frm, lst, 80, 100, 0, 0, ff=ff, bg=bg,
                                       fg=fg, command=command, fs=fs, bd_radius=bd_radius)
        frm.append(c)
        return frm


    def autolabels(self, frm, lst1, lst2, H, L, T, L2, n, bg='lavender', bg2='oldlace',
                      fg='black', fg2='black', align1='left', align2='left', justify1='left',
                      justify2='left'):

        '''
        :param frm: frame or container holding the labels
        :param lst1: list for lhs
        :param lst2: list for rhs
        :param H: Height of Labels
        :param L: Left of lhs Labels
        :param T: Height of Labels
        :param L2: Left of rhs labels (spacing between lhs and rhs)
        :param n: Multiplier for vertical spacing between labels
        :param bg: color of lhs labels
        :param bg2: color of rhs labels
        :param fg: font color of lhs labels
        :param fg2: color of rhs labels
        :param align1: text align of lhs labels
        :param align2: text align of rhs labels
        :param justify1: text align of lhs labels
        :param justify2: text align of rhs labels
        :return: Frame, labels

        Coloring based on conditions can be done thru this example:
        frame, lbl, lbr = gui.autolabels(self.frame_info, lst1, lst2, H, L, T, L2, n)

        lbr[3].css_color = 'salmon'  # Change right side color on 3rd index
        lbl[2].css_color = 'yellowgreen'    # Change left side color on 2nd index

        '''
        lbll, lblr = [],[]
        if len(lst1) != len(lst2):
            gui.prt('\t - Autolabels Lists lst1 and lst2 need to be of same length', 'v')
            lbl1, lbl2 = None, None
            frm = None
            return frm, lbl1, lbl2

        else:
            for (i, x), y in zip(enumerate(lst1), lst2):
                gui.prt(f'\t - Autolabel info: {i}: {x}, {y}', 'c')
                lbl1, lbl2 = gui.labels(frm, H, len(str(x)), L, T + (i * n), H, len(str(y)),
                         L2, T + (i * n), text=str(x),
                         align1=align1, justify1=justify1, text2=str(y), bg=bg, fg=fg, fg2=fg2,
                         align2=align2, justify2=justify2, bg2=bg2)

                lbll.append(lbl1)
                lblr.append(lbl2)

            for l, r in zip(range(len(lbll)), range(len(lblr))):
                gui.pr(f'\t - label1 {l}:', lbll[l].text, 'c')
                gui.pr(f'\t - label2 {r}', lblr[r].text, 'c')

            return frm, lbll, lblr


    def string_to_dt(self, date_string, date_format='%Y-%m-%d'):
        '''
        :param date_string: str: incoming date string in format set by date_format
        :param date_format: str: expected format of incoming date
        :return: datetime obj with timestamp 00:00:00 if not specified in format
        '''
        from datetime import datetime
        dobj = datetime.strptime(date_string, date_format)
        return dobj


    def dt_to_string(self, dobj, format='%Y-%m-%d'):
        '''

        :param dobj: datetime obj
        :param format: str: expected format of returned date
        :return: str date in format set
        '''
        from datetime import datetime
        formatted_date = dobj.strftime(format)
        return formatted_date


    def prt(self, text, c='b', w='normal'):
        '''
        Author: Aru Raghuvanshi
        Use this function to debug and print statements in different colours
        :param text: str
        :param c: str: one of [b, g, r, v, y, c, w]
        :param w: str:fontweight: one of ['normal', b, s, u, i] (normal, bold, strikethru, underline, italics)
        :return: none
        '''
        if c == 'b':
            print(f'\033[0;94m{text}\033[0m')
        elif c == 'g':
            print(f'\033[0;92m{text}\033[0m')
        elif c == 'r':
            print(f'\033[0;91m{text}\033[0m')
        elif c == 'v':
            print(f'\033[0;95m{text}\033[0m')
        elif c == 'y':
            print(f'\033[0;93m{text}\033[0m')
        elif c == 'c':
            print(f'\033[0;96m{text}\033[0m')
        elif c == 'w':
            print(f'\033[0;97m{text}\033[0m')
        else:
            pass

        if w == 'b':
            print(f'\033[1;94m{text}\033[0m')
        elif w == 'g':
            print(f'\033[1;92m{text}\033[0m')
        elif w == 'r':
            print(f'\033[1;91m{text}\033[0m')
        elif w == 'v':
            print(f'\033[1;95m{text}\033[0m')
        elif w == 'y':
            print(f'\033[1;93m{text}\033[0m')
        elif w == 'c':
            print(f'\033[1;96m{text}\033[0m')
        elif w == 'w':
            print(f'\033[1;97m{text}\033[0m')
        elif w == 'u':
            print(f'\033[0;4m{text}\033[0m')
        elif w == 's':
            print(f'\033[0;9m{text}\033[0m')
        elif w == 'i':
            print(f'\033[0;3m{text}\033[0m')

        else:
            pass


    def pr(self, t1, t2, c='b', w='normal'):
        self.prt(f'{t1}: {t2}', c, w)



gui = GUI()