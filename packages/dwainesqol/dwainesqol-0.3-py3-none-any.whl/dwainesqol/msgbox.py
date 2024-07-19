class msgbox:

    def __init__(self, title, message,type):
        self.message = message
        self.title = title
        self.type = type

    def msgbox(self):
        
        
        import ctypes 


        if type == "MB_OK":
            type = 0x0
        
        elif type == "MB_OKCXL":
            type = 0x01

        elif type == "MB_YESNOCXL":
            type = 0x03
        
        elif type == "MB_YESNO":
            type = 0x04

        elif type == "MB_HELP":
            type = 0x4000

        elif type == "ICON_EXCLAIM":
            type = 0x30

        elif type == "ICON_INFO":
            type = 0x40

        elif type == "ICON_STOP":
            type = 0x10

        
        ctypes.windll.user32.MessageBoxW(0,self.message,self.title,self.type)
