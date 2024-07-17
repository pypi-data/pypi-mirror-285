
class RenderedRow:
    def __init__(self, tableLayout, data):
        self._tableLayout = tableLayout
        self._data = data
        
    def __getitem__(self, colKey):
        if colKey not in self._tableLayout.cols:
            raise Exception('No colum with key %s' % repr(colKey))

        return self._data[colKey]['orig']

    def getDataForLine(self, colKey, lineIdx):
        if colKey not in self._tableLayout.cols:
            raise Exception('No colum with key %s' % repr(colKey))
        
        if lineIdx > len(self._data[colKey]['wrapped'])-1:
            return ''
        else:
            return self._data[colKey]['wrapped'][lineIdx]
    
    def getDataStrForLine(self, colKey, lineIdx):
        if colKey not in self._tableLayout.cols:
            raise Exception('No colum with key %s' % repr(colKey))
        
        s = self.getDataForLine(colKey, lineIdx)
        
        if lineIdx < len(self._data[colKey]['wrapped'])-1:
            s = s + self._tableLayout.brStr
        
        lPad = self._tableLayout.cols[colKey].lPad
        rPad = self._tableLayout.cols[colKey].rPad
        
        fs = '%s%%-%ds%s' % (
            lPad,
            self._tableLayout.cols[colKey].width - len(lPad) - len(rPad),
            rPad
        )
        
        rv = fs % s        
        assert len(rv) == self._tableLayout.cols[colKey].width
        return rv
    
    def getRowLine(self, lineIdx):
        spans = []
        for colKey in self._tableLayout.cols.keys():
            spans.append( self.getDataStrForLine(colKey, lineIdx) )
        return '%s%s%s' % (
            self._tableLayout.colDivStr,
            self._tableLayout.colDivStr.join(spans),
            self._tableLayout.colDivStr
        )

    @property
    def lines(self):
        rv = []
        for i in range(self.numLines):
            rv.append( self.getRowLine(i) )
        return rv
    
    @property
    def numLines(self):
        nl=0
        for colKey in self._data.keys():
            if len(self._data[colKey]['wrapped']) > nl:
                nl = len(self._data[colKey]['wrapped'])
        return nl
