This library wraps the popular Python library "REMI" (https://github.com/rawpython/remi) to make easy UI by simply calling functions with arguments for UI placement. Quick Remi enables building building large UI in the least lines of code using pure Python. No HTML or javascript knowledge required.

USAGE:

pip install quickremi

from quickremi.gui import gui as G

Build Frame or Container
	frame1 = G.create_container(window, H=40, W=45, L=52, T=20, bg='lightblue')

Build Labels
	lbl = G.create_label(frame1, H=50, W=75, L=5, T=2, bg='ivory')

Build Buttons
	btn= G.create_button(frame1, H=10, W=15, L=5, T=20, bg='teal', command=clicked_button)

Use the function help menu to read their respective documentation. 
In all functions, frame, H, W, L, T are positional (mandatory) arguments that determine their position within a container.
Other arguments like background colours, font family, size, font colour, text alignment, justifications, border width, radius, style and border colour etc. are optional and can be changed as per use.

Height, Width, Left and Top are % values by default and hence scale as per the size of the device of display.
The arugment 'fs' (font size) also scales as per the display device.	

Other Widgets in the package:
	- Drop Down
	- List Items
	- Slider
	- Image
	- File Uploader
	- Table
	- Progress Bar
	- Entry Field
	- Date Picker
	- Label Checkbox (Radio Button)	
	- Spinbox

All the above widgets follow the same syntax.
	- Frame, Height, Width, Left, Top, and other kwargs whose documentation is available in the help menu.

Widgets like Drop Down, Slider, List Items, Entry Field have listeners which read the input values entered by user.

Example 1:
For: Drop Down or Entry or Slider etc.

lst = ['Tiger', 'Lion', 'Jaguar']
dd = G.create_dropdown(frame1, lst, 20, 50, 5, 5, command=on_selection)

# Listner function
def on_selection(widget, value):
    # value will now hold the value of the user selection between tiger lion and jaguar.
    print(value)


Example 2:
For List Items, the listener functions in a different way. Following is the example usage.

lst = ['Apple', 'Mango', 'Guava']
lv = G.create_listview(frame1, lst, 20, 50, 5, 5, command=on_value_selection)

# Listener function
def on_value_selection(widget, value):
    # value is the index number. Hence lv[val].get_text() is used to fetch the actual text value.    
    val = lv.children[value].get_text()  
    print(val)


All the other widget operations revolve around these two examples.
