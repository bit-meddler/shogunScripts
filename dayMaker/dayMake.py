from PySide import QtGui, QtCore
import sys


class Simple( QtGui.QWidget ):
    def __init__( self ):
        super( Simple, self ).__init__()
        self.setMinimumSize( 350, 300 )
        self.setWindowTitle( "Testing pySide" )
        
        # try a dropdown
        self.prj_lbl = QtGuiQtGuiQLabel( "Project", self )
        self.prj_lbl.move( 5, 5 )
        
        self.project_names = [ "Apes", "Tintin", "LotR" ]
        
        self.projects = QtGuiQComboBox( self )
        self.projects.addItems( self.project_names )
        self.projects.setMinimumWidth( 200 )
        self.projects.move( 50, 5 )
        
        
        
        
if __name__ == "__main__":
    _app = QtCore.QApplication( sys.argv )
    
    