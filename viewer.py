# import full tkinter module
import tkinter as tk  # renaming tkinter to tk for ease and efficiency
from tkinter import *  # this is importing all (*) modules from the tkinter package
from datetime import *
import time  # for the timing to refresh the live values
from tkinter import filedialog as fd
import default

#boot_slave = gpiozero.LED(17)  # only enable when Pi running
#slave_status = gpiozero.Button(18)   # only enable when Pi running

class Settings:

    default_appearance = {'heading_font' : 'bahnschrift 15 bold',
                        'normal_font' : 'bahnschrift 11',
                        'foreground' : '#CACED0',
                        'background' : '#395161'}
                        

    baud_rates = [9600, 19200, 38400, 57600, 115200]
    parity = ['E', 'N']


    def __init__(self, *args, **kwargs):
        ''' Determines if a new appearance dictionary has been passed. If not, default
            class dictionary of appearance values is to be used. '''
        if 'new_appearance' in kwargs:
            self._tkinter_appearance(kwargs['new_appearance'])
        else:
            self._tkinter_appearance(Settings.default_appearance)
    
    def _tkinter_appearance(self, appearance):
        ''' Define the fonts, font colours and background colour. '''
        self.heading_font = appearance['heading_font']
        self.normal_font = appearance['normal_font']
        self.foreground = appearance['foreground']
        self.background = appearance['background']
    
    def get_tkinter_appearance(self):
        ''' Get the current appearance values. '''
        pass

    def set_tkinter_appearance(self, fg, bg):
        ''' Change the appearance values for font, fg and/or background. 
            Below can be modified to include different heading and body fonts. '''
        appearance = {'heading_font' : Settings.default_appearance['heading_font'],
                      'normal_font' : Settings.default_appearance['normal_font'],
                      'foreground' : fg,
                      'background' : bg}
        self._tkinter_appearance(appearance)

    
    def __folder_path_definition(self):
        ''' This method allows for super users to define where the folder paths reside.
            This must be done each time, otherwise the .csv file which is within the 
            python program root folder will be utilised. '''
        pass

class Viewer():

    operation_modes = {'1: Single Vehicle Air Leakage' : 1,
                        '2: Static Unit Braking' : 2,
                        '3: Load Simulation' : 3}

    def __init__(self, master, settings):
        self.master = master #assign master parameter an attribute
        self.master.title('NAY DPMAS - Digital Pressure Monitoring & Application System')
        width_height = str(master.winfo_screenwidth()) + "x" + str(master.winfo_screenheight())
        self.master.geometry(width_height)
        #self.master.attributes('-fullscreen', True)  # makes window fullscreen if True
        self.fMain = Frame(self.master) #create our upper frame attribute, with master as the toplevel widget
        self.fMain.configure(bg=settings.background)
        self.fMain.pack(fill="both", expand=YES)
        self.user_input()
        self._other_widgets()

    def user_input(self):
        # Can improve the below by adding fixed text labels etc to a list/dictionary.
        # Then iterating through each one and giving same bg, fg settings.
        self.user_name = StringVar()
        self.unit_number = StringVar()
        self.project = StringVar()
        self.operation_mode = StringVar()  # Define the utilisation e.g. Brakes, Air Leakage, Load Testing.
        fSelections = Frame(self.fMain)
        fSelections.configure(bg=settings.background)
        fSelections.pack(pady=200)
        lSelections = Label(fSelections, text='Enter Data:', bg=settings.background, fg='white', font=settings.heading_font).grid(row=0, column=0, columnspan=2, sticky=W)


        Label(fSelections, text='Name:', bg=settings.background, fg='white', font=settings.normal_font).grid(row=1, column=0, sticky=E)
        eUser_Name = Entry(fSelections, textvariable=self.user_name).grid(row=1, column=1, sticky=W)
        Label(fSelections, text='Operation Mode:', bg=settings.background, fg='white', font=settings.normal_font).grid(row=2, column=0, sticky=E)
        oOperation_mode = OptionMenu(fSelections, self.operation_mode, *Viewer.operation_modes)
        oOperation_mode.grid(row=2, column=1, sticky=W)
        Label(fSelections, text='Project: ', bg=settings.background, fg='white', font=settings.normal_font).grid(row=3, column=0, sticky=E)
        oProject = OptionMenu(fSelections, self.project, *['Class 800/801', 'Class 385', 'ML4'])
        oProject.grid(row=3, column=1, sticky=W)
        Label(fSelections, text='Unit Number:', bg=settings.background, fg='white', font=settings.normal_font).grid(row=4, column=0, sticky=E)
        bConfirm_selection = Button(fSelections, text='Confirm', command=self.__start_application, font=settings.normal_font).grid(row=5, column=0, columnspan=2, ipadx=80)


    def widget_destroyed(self, event):
        ''' Binding which is ran if a window is exited. '''
        self.settings_open = False

    def _settings_window(self):
        try:  # Checks if a window instance is already open, if so, exits method.
            if self.settings_open == True:
                return
        except:
            pass
        self.settings_open = True  # For tracking widget to prevent multiple.
        self.baudrate = StringVar()
        self.baudrate.set(boot.a._serial_config_dict['baudrate'])
        self.parity = StringVar()
        self.parity.set(boot.a._serial_config_dict['parity'])
        self.file_path = StringVar()
        self.fg_bg_list = []
        for i in range(6):
            self.fg_bg_list.append(IntVar())
        wSettings = tk.Toplevel(self.master)
        wSettings.bind("<Destroy>", self.widget_destroyed)  # Binding to track window close.
        wSettings.title('View & Change Settings')
        wSettings.geometry("390x475+75+75")
        wSettings.config(bg=settings.background)
        wSettings.pack_propagate(False)  # Stops the child Frame from resizing the widget
        wSettings.resizable(0,0)  # Removes Maximize button
        fSettings = Frame(wSettings)
        fSettings.configure(bg=settings.background)
        fSettings.pack()
        lSerial_settings = Label(fSettings, text='Serial & Modbus: ', bg=settings.background, fg='white', font=settings.heading_font).grid(row=0, column=0, columnspan=3, sticky=NSEW)
        lBaudrate = Label(fSettings, text='Baudrate: ', bg=settings.background, fg='white', font=settings.normal_font).grid(row=1, column=0, sticky=E)
        lParity = Label(fSettings, text='Parity: ', bg=settings.background, fg='white', font=settings.normal_font).grid(row=2, column=0, sticky=E)
        oBaudrate = OptionMenu(fSettings, self.baudrate, *Settings.baud_rates)
        oBaudrate.grid(row=1, column=1, columnspan=2, sticky=W)
        oParity = OptionMenu(fSettings, self.parity, *Settings.parity)
        oParity.grid(row=2, column=1, columnspan=2, sticky=W)

        lProject_settings = Label(fSettings, text='Project: ', bg=settings.background, fg='white', font=settings.heading_font).grid(row=4, column=0, columnspan=3, sticky=NSEW)
        lUnit_numbers = Label(fSettings, text='Unit Numbers: ', bg=settings.background, fg='white', font=settings.normal_font).grid(row=5, column=0, sticky=E)
        bUnit_numbers = Button(fSettings, text='Choose File', font=settings.normal_font, command=lambda : self.unit_numbers_dialog(fSettings)).grid(row=5, column=1, columnspan=2, sticky=W)
        
        lAppearance_settings = Label(fSettings, text='Appearance (0 - 255):', bg=settings.background, fg='white', font=settings.heading_font).grid(row=7, column=0, columnspan=3)
        lAppearance_fg = Label(fSettings, text='Font\nColour:', bg=settings.background, fg='white', font=settings.normal_font).grid(row=8, rowspan=3, column=0)
        lAppearance_bg = Label(fSettings, text='Background\nColour:', bg=settings.background, fg='white', font=settings.normal_font).grid(row=11, rowspan=3, column=0)
        appearance_lbls = ['R', 'G', 'B', 'R', 'G', 'B']
        appearance_vals = []  # Entry Boxes for RGB values of ForeGround and BackGround
        for index, lbl in enumerate(appearance_lbls):
            self.create_label(fSettings, lbl, False, 'white').grid(row=index + 8, column=1, sticky=E)
            appearance_vals.append(Entry(fSettings, textvariable=self.fg_bg_list[index]).grid(row=index + 8, column=2, sticky=W))

        bConfirm = Button(fSettings, text='Confirm', font=settings.normal_font, command=lambda : self._save_settings(fSettings, wSettings)).grid(row=15, column=0, columnspan=3)
        
        lSuper_user = Label(fSettings, text='Super-User: ', bg=settings.background, fg='yellow', font=settings.heading_font).grid(row=16, column=0, columnspan=3, sticky=NSEW)
        lSerial_config = Label(fSettings, text='Serial Config: ', bg=settings.background, fg='yellow', font=settings.normal_font).grid(row=18, column=0, sticky=W)
        bSerial_config = Button(fSettings, text='Choose File', font=settings.normal_font).grid(row=18, column=1, columnspan=2, sticky=W)
        lRegister_map = Label(fSettings, text='Register Map: ', bg=settings.background, fg='yellow', font=settings.normal_font).grid(row=19, column=0, sticky=W)
        bRegister_map = Button(fSettings, text='Choose File', font=settings.normal_font).grid(row=19, column=1, columnspan=2, sticky=W)

        

    def unit_numbers_dialog(self, frame):
        ''' Open file dialog for selecting specific unit number list. '''
        file_path = fd.askopenfilename()
        lFile = Label(frame, text='File: ', bg=settings.background, fg='white', font=settings.normal_font).grid(row=6, column=0, sticky=E)
        if file_path[-4:] != '.csv':
            lFile_path = Label(frame, text='Invalid File Type Selected!', bg=settings.background, fg='red', font=settings.normal_font).grid(row=6, column=1, columnspan=2)
        else:
            lFile_path = Label(frame, text=file_path[:23] + '...', bg=settings.background, fg=settings.foreground, font=settings.normal_font).grid(row=6, column=1, columnspan=2)

    def _save_settings(self, frame, window):
        ''' Takes the user input font colours and if valid, passes on to set the appearance. '''
        try:
            colours = []
            for i in range(6):
                colours.append(self.fg_bg_list[i].get())
                if (colours[i] - 255) > 0:
                    raise Exception  # Val is negative or over 255
            for index, colour in enumerate(colours):
                colours[index] = "{:0>2}".format(hex(colour)[2:])  # Format the int as a leading 0 padded hex
            fg = '#' + colours[0] + colours[1] + colours[2]
            bg = '#' + colours[3] + colours[4] + colours[5]
            settings.set_tkinter_appearance(fg, bg)
            self.settings_open = False  # Allow for settings to be reopened by setting False.
            window.destroy()  # Destroy passed window (wSettings)
        except:
            self.create_label(frame, 'Invalid Colour!', False, 'red').grid(row=14, column=0, columnspan=3)

    def create_label(self, frame, entry_str, hdg, *opt_colour):
        ''' Method is used to create all labels.
            hdg is bool which isf 1 = heading, if 0 = normal.
            *opt_colour if included over-writes the default font colour. '''
        if len(opt_colour) > 0:
            if hdg == True:
                text = Label(frame, text=entry_str, bg=settings.background, fg=opt_colour, font=settings.heading_font)
            else:
                text = Label(frame, text=entry_str, bg=settings.background, fg=opt_colour, font=settings.normal_font)
        else:
            if hdg == True:
                text = Label(frame, text=entry_str, bg=settings.background, fg=settings.foreground, font=settings.heading_font)
            else:
                text = Label(frame, text=entry_str, bg=settings.background, fg=settings.foreground, font=settings.normal_font)
        return text  # In case wish to assign to namespace for deletion etc.

    def _other_widgets(self):
        fOther_widgets = Frame(self.fMain)
        fOther_widgets.configure(bg=settings.background)
        fOther_widgets.pack()
        bSettings = Button(fOther_widgets, text='Settings', bg=settings.background, fg='white', font=settings.normal_font, command=self._settings_window).pack()
    

    def __start_application(self):
        op_mode = self.operation_mode.get()[0]  # Get only the first value, FIGURE OUT TAKING VALUE OF DICT

boot = default.Default()
settings = Settings()
root = Tk() #create top level widget object (window) of Tk class.

mainapp = Viewer(root, settings) #create instance of class and pass Top widget as 1st parameter (master). As such the root widget becomes "self".

root.mainloop()