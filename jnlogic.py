from os.path import basename, dirname, realpath

class File:

    def __init__(self, path):
        self.file_path = path
        self.file_name = basename(path)
        self.dir_name = dirname(path)
        self.saved = False
        self.modified = False
