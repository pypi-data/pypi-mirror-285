
class DividerFactory:
    def __init__(self, tableLayout):
        self._tableLayout = tableLayout
    
    def getSimpleDivider(self, hChar='-', junctChar='+'):
        spans = []
        for colKey in self._tableLayout.cols.keys():
            spans.append( hChar * self._tableLayout.cols[colKey].width )
        return junctChar + junctChar.join(spans) + junctChar
                
    