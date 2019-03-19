from os.path import basename, dirname, realpath

class File:

    def __init__(self, path):
        self.file_path = path
        self.file_name = basename(path).split(".")[0]
        self.dir_name = dirname(path)
        self.file_ext = basename(path).split(".")[1]
        self.saved = False
        self.modified = False
