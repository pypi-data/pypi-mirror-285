
import textwrap
from mdtablegen.render import RenderedRow

class RowFactory:
    def __init__(self, tableLayout, allowWrap=True):
        self._tableLayout = tableLayout
        self.allowWrap = allowWrap
        self.reset()
    
    def reset(self):
        self._data = {}
        for colKey in self._tableLayout.cols.keys():
            self._data[colKey] = {
                'orig': '',
                'wrapped': []
            }
    
    @property
    def brStr(self):
        if self.allowWrap:
            return self._tableLayout.brStr
        else:
            return ''
    
    def __setitem__(self, colKey, value):
        if colKey not in self._tableLayout.cols:
            raise Exception('No colum with key %s' % repr(colKey))
        
        self._data[colKey]['orig'] = value

        if len(value) > self.getMaxFieldDataLen(colKey):
            if not self.allowWrap:
                raise Exception('data %s is too long for column %s (allowWrap=False, max=%d)' % (
                    repr(value), colKey, self.getMaxFieldDataLen(colKey)
                ))
            self._data[colKey]['wrapped'] = textwrap.wrap(
                value,
                width = self.getMaxFieldDataLen(colKey) - len(self.brStr),
                initial_indent='', subsequent_indent=''
            )
        else:
            self._data[colKey]['wrapped'] = [value]
    
    def __getitem__(self, colKey):
        if colKey not in self._tableLayout.cols:
            raise Exception('No colum with key %s' % repr(colKey))

        return self._data[colKey]['orig']

    def setData(self, data):
        for colKey in self._tableLayout.cols.keys():
            self[colKey] = data.get(colKey, '')

    def getMaxFieldDataLen(self, colKey):
        l = self._tableLayout.cols[colKey].width
        #l = l - len(self.brStr)
        l = l - len(self._tableLayout.cols[colKey].lPad)
        l = l - len(self._tableLayout.cols[colKey].rPad)
        return l
    
    def nextRow(self):
        rr = RenderedRow(self._tableLayout, self._data)
        self.reset()
        return rr
        

