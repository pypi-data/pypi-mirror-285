import remi.gui as tk
from datetime import datetime
import pytz

class Creator:

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
                     overflow='auto', ta='center', hover=''):

        '''
        Creates Label and returns the Label Widget

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
        lbl.css_align_content = align
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
        frame.append(lbl)
        return lbl


    def create_button(self, frame, H, W, L, T, command=None, text='.', bg='navyblue', fg='white', fw='normal',
                      align='center', justify='space-around', fs=0.8, bd_width='0px', ff='calibri', bd_color='black',
                      display='inline', position='absolute', px=False, bd_style='none', bd_radius='0px', bidx=None,
                      overflow='auto', ta='center', hover=''):

        '''
        Creates buttons and returns the button widget
        # Bd Style = Solid dotted dashed none
        # fw: font-weight 'bold, normal
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
        btn.onclick.do(command)
        frame.append(btn)
        # print(f'Button clicked at: {self.tm}')
        return btn


    def create_uploader(self, frame, H, W, L, T, filename=None, bg='navyblue', fg='white',
                        align='center', justify='space-around', command_succ=None, command_fail=None,
                        display='inline', position='absolute', px=False):

        '''Creates uploader and returns the uploader widget'''

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
        frame.append(btn)
        btn.onsuccess.do(command_succ)
        btn.onfailed.do(command_fail)
        return btn


    def create_container(self, frame, H, W, L, T, bg='whitesmoke', fg='black', bd_radius='0px', bd_style='None',
                         align='center', justify='space-around', overflow='auto', bw='0px', fs=0.8,
                         display='space-around', position='absolute', px=False):

        '''Creates container and returns the container widget'''

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
        btn.css_border_width = bw
        btn.css_border_style = bd_style
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
                     justify_content='center', fs=0.8, flex_wrap='wrap', bc='black',
                     display='space-around', position='absolute', px=False, bw='3px', fw='normal', ff='calibri'):

        '''Creates table and returns the table widget'''

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
        btn.css_border_color = bc
        btn.css_border_width = bw
        btn.css_font_weight = fw
        btn.css_font_family = ff
        btn.css_margin = margin
        frame.append(btn)
        return btn



    def create_image(self, frame, imagepath, H, W, L, T, h=100, w=100, bg='navyblue', fg='white',
                     align='center', justify='space-around', command=None,
                     display='inline', position='absolute', px=False):

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

        '''Creates listview and returns the listview widget'''

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

        '''Creates progress bar and returns the progress widget'''

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

        '''Creates dropdwn menu and returns the dropdown menu widget'''

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
                     align='center', justify='space-around', input_type='regular', bw='1px', ff='calibri',
                     display='inline', position='absolute', px=False, fs=0.8, bd_radius='0px'):

        '''
        Creates entry field and returns the entry field widget.
         input_type are either 'password', 'regular' or 'text'.
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

        btn.css_border_width = bw
        btn.css_border_radius = bd_radius
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
                           align='center', justify='space-around', fs=0.7, bd_width='0px', margin='0px', bd_color='black',
                           display='inline-flex', position='absolute', px=False, bd_style='none', bd_radius='0px'):

        '''Creates date picker and returns the date picker widget'''

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

        '''Creates label checkbox and returns the label checkbox widget'''

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



    def show_html(self, frame, htmlcontent, H, W, L, T, w=750, h=500, margin='4px'):

        # main_container = tk.VBox(width=W, height=H, style={'margin': '0px auto'})
        mc = C.create_container(frame, H, W, L, T)

        # htmlcontent = "https://www.meteo.it/"

        frame = tk.Widget(_type='iframe', width=w, height=h, margin=margin)
        frame.attributes['src'] = htmlcontent
        frame.attributes['width'] = '90%'
        frame.attributes['height'] = '90%'
        frame.style['border'] = '1px solid black'

        mc.add_child('frame', frame)
        # window.append(main_container)
        # returning the root widget
        return frame


    def show_plotly(self, frame, htmlcontent, H, W, L, T, w=100, h=100, margin='0px',
                    border='1px solid black'):

        mc = C.create_container(frame, H, W, L, T)

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

        '''Creates label and returns the container'''

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

        tbl = C.create_table(frm, res, 99, 99, 0, 0, bg=bg, fg=fg, overflow=overflow,
                             align_self=align_self, align_content=align_content, align_items=align_items, margin=margin,
                             justify_content=justify_content, fs=fs, flex_wrap=flex_wrap, bc=bc,
                             display=display, position=position, px=px, bw=bw, fw=fw, ff=ff)
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
                              fg=fg, bg=bg, bw=bw, bd_radius=bd_radius)

        frm.append(e)
        return frm




    def date(self, frame, H, W, L, T, command=None,
                   bg='white', fg='white', bgc='whitesmoke', fs=0.8,
                   bd_radius='0px'):

        '''Creates date picker and returns the container'''

        frm = self.create_container(frame, H, W, L, T, bg=bgc, overflow='visible')

        d = C.create_date_picker(frm, 98, 99, 0, 0, command=command, bg=bg, fg=fg,
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
        frame, lbl, lbr = C.autolabels(self.frame_info, lst1, lst2, H, L, T, L2, n)

        lbr[3].css_color = 'salmon'  # Change right side color on 3rd index
        lbl[2].css_color = 'yellowgreen'    # Change left side color on 2nd index

        '''
        lbll, lblr = [],[]
        if len(lst1) != len(lst2):
            C.prt('\t - Autolabels Lists lst1 and lst2 need to be of same length', 'v')
            lbl1, lbl2 = None, None
            frm = None
            return frm, lbl1, lbl2

        else:
            for (i, x), y in zip(enumerate(lst1), lst2):
                C.prt(f'\t - Autolabel info: {i}: {x}, {y}', 'c')
                lbl1, lbl2 = C.labels(frm, H, len(str(x)), L, T + (i * n), H, len(str(y)),
                         L2, T + (i * n), text=str(x),
                         align1=align1, justify1=justify1, text2=str(y), bg=bg, fg=fg, fg2=fg2,
                         align2=align2, justify2=justify2, bg2=bg2)

                lbll.append(lbl1)
                lblr.append(lbl2)

            for l, r in zip(range(len(lbll)), range(len(lblr))):
                C.pr(f'\t - label1 {l}:', lbll[l].text, 'c')
                C.pr(f'\t - label2 {r}', lblr[r].text, 'c')

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



