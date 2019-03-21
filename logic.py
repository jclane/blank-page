from os.path import basename, dirname, realpath
from datetime import datetime


class CustomDateTime:
    
    def __init__(self, dt_obj=datetime.now()):
        self.dt_obj = dt_obj
        self.date = str(self.dt_obj.month) + "/" + str(self.dt_obj.day) + "/" + str(self.dt_obj.year)
        self.time = datetime.strftime(datetime.strptime(str(self.dt_obj.hour)+":"+str(self.dt_obj.minute), "%H:%M"), "%I:%M %p")
        
    def __str__(self):
        return self.date + " " + str(self.time)
    
    def get_date(self):
        return self.date
        
    def get_time(self):
        return str(self.time)

class File:

    def __init__(self, path):
        self.file_path = path
        self.file_name = basename(path).split(".")[0]
        self.dir_name = dirname(path)
        self.file_ext = basename(path).split(".")[1]
        self.saved = False
        self.modified = False
