from PySide import QtGui, QtCore
import sys


class Simple( QtGui.QWidget ):

    def __init__( self, parent_app ):
        super( Simple, self ).__init__()
        
        self._parent_app = parent_app
        
        self.setMinimumSize( 350, 300 )
        self.setWindowTitle( "Testing pySide" )
        
        # try a dropdown
        self.prj_lbl = QtGui.QLabel( "Project", self )
        self.prj_lbl.move( 5, 5 )
        
        self.project_names = [ "Apes", "Tintin", "LotR" ]
        
        self.projects = QtGui.QComboBox( self )
        self.projects.addItems( self.project_names )
        self.projects.setMinimumWidth( 200 )
        self.projects.move( 50, 5 )
        
        self.new_prj_lbl = QtGui.QLabel( "Project:", self )
        self.new_prj_lbl.move( 5, 30 )

        self.new_prj = QtGui.QLabel( 'egg', self )
        self.new_prj.move( 110, 75 )
                
        self.recipient = QtGui.QLineEdit( self )
        self.recipient.setPlaceholderText( "set project name" )
        self.recipient.setMinimumWidth( 200 )
        self.recipient.move( 50, 30 )

        self.build_button = QtGui.QPushButton( "Build Project", self)
        self.build_button.setMinimumWidth( 145 )
        self.build_button.move( 5, 75 )

        
    def run( self ):
        self.show()
        self._parent_app.exec_()
        
        
if __name__ == "__main__":
    print( sys.argv )
    _app = QtGui.QApplication( sys.argv )
    
    ui_test = Simple( _app )
    ui_test.run()