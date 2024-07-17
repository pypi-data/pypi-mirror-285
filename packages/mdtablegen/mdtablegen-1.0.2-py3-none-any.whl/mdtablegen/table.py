
import collections
from mdtablegen.layout import TableLayout, ColumnLayout
from mdtablegen.rowfactory import RowFactory
from mdtablegen.divfactory import DividerFactory

class NoSuchColumnError(Exception):
    def __self__(self, key):
        self.key = key
    def __str__(self):
        return 'No column with key %s' % repr(self.key)

class MarkdownColumn:
    def __init__(self, key):
        self._key = key
        self.lPad = ' '
        self.rPad = ' '
        self.title = ''
        self.maxWidth = None
    
    @property
    def key(self):
        return self._key


class MarkdownTable:
    def __init__(self):
        self.cols = collections.OrderedDict()
        self._entries = []
        self.brStr = '<br>'
        self.colDivStr = '|'
        self.startDiv = None
        self.headerDiv = None
        self.rowDiv = None
        self.endDiv = None
    
    def addRow(self, data):
        self._entries.append({
            'type': 'single',
            'data': data
        })
    
    def addCol(self, key, title=None, maxWidth=None, rPad=' ', lPad=' '):
        self.cols[key] = MarkdownColumn(key)
        self.cols[key].maxWidth = maxWidth
        self.cols[key].rPad = rPad
        self.cols[key].lPad = lPad
        if title is None:
            self.cols[key].title = key
        else:
            self.cols[key].title = title
    
    def iterRowData(self):
        for entry in self._entries:
            if entry['type']=='single':
                effRowData = {}
                for colKey in self.cols.keys():
                    if colKey in entry['data']:
                        effRowData[colKey] = entry['data'][colKey]
                    else:
                        effRowData[colKey] = ''
                yield effRowData
            else:
                raise NotImplementedError(entry['type'])                
    
    def calcColWidths(self):
        colWidths = {}
        for colKey in self.cols.keys():
            #colWidths[colKey] = 0
            colWidths[colKey] = (
                len(self.cols[colKey].title) +
                len(self.cols[colKey].lPad) +
                len(self.cols[colKey].rPad)
            )
        
        for rd in self.iterRowData():
            for colKey in self.cols.keys():
                
                paddedCellWidth = (
                    len(rd[colKey]) + 
                    len(self.cols[colKey].lPad) +
                    len(self.cols[colKey].rPad)
                )
                
                if paddedCellWidth > colWidths[colKey]:
                    if (
                        self.cols[colKey].maxWidth is not None and 
                        paddedCellWidth > self.cols[colKey].maxWidth
                    ):
                        colWidths[colKey] = self.cols[colKey].maxWidth
                    else:
                        colWidths[colKey] = paddedCellWidth
        return colWidths

    def render(self):
        tl = TableLayout()
        tl.brStr = self.brStr
        tl.colDivStr = self.colDivStr
        
        colWidths = self.calcColWidths()
        
        for colKey in self.cols.keys():
            tl.cols[colKey] = ColumnLayout(
                width = colWidths[colKey],
                lPad = self.cols[colKey].lPad,
                rPad = self.cols[colKey].rPad
            )
        
        df = DividerFactory(tl)
        
        if self.startDiv is not None:
            yield df.getSimpleDivider(self.startDiv)
        
        hf = RowFactory(tl, allowWrap=False)
        for colKey in self.cols.keys():
            hf[colKey] = self.cols[colKey].title
        for line in hf.nextRow().lines:
            yield line
        
        if self.headerDiv is not None:
            yield df.getSimpleDivider(self.headerDiv)
        
        rf = RowFactory(tl)
        
        for rd in self.iterRowData():
            rf.setData(rd)
            
            for line in rf.nextRow().lines:
                yield line
            
            if self.rowDiv is not None:
                yield df.getSimpleDivider(self.rowDiv)

            
