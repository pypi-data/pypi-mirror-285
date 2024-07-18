class msgbox:

    def __init__(self, title, message,typeOfBox):
        self.message = message
        self.title = title
        self.typeOfBox = typeOfBox


        import ctypes 


        if typeOfBox == "MB_OK":
            typeOfBox = 0x0
        
        elif typeOfBox == "MB_OKCXL":
            typeOfBox = 0x01

        elif typeOfBox == "MB_YESNOCXL":
            typeOfBox = 0x03
        
        elif typeOfBox == "MB_YESNO":
            typeOfBox = 0x04

        elif type == "MB_HELP":
            stypeOfBox= 0x4000

        elif type == "ICON_EXCLAIM":
            typeOfBox = 0x30

        elif type == "ICON_INFO":
            typeOfBox = 0x40

        elif type == "ICON_STOP":
            typeOfBox = 0x10

            
        ctypes.windll.user32.MessageBoxW(0,message,title,typeOfBox)

