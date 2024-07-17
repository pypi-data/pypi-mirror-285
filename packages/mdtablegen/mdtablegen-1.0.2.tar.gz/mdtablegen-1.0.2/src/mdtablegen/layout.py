
import collections

class ColumnLayout:
    def __init__(self, lPad=' ', rPad=' ', width=30):
        self.lPad = lPad
        self.rPad = rPad
        self.width = width

class TableLayout:
    def __init__(self):
        self.brStr = '<br>'
        self.colDivStr = '|'
        self.cols = collections.OrderedDict()


