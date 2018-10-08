from PySide import QtGui, QtCore
import sys
import os
import datetime
import ConfigParser

class Henchman( QtGui.QMainWindow ):

    def __init__( self, parent_app, clean_start=False ):
        super( Henchman, self ).__init__()
        self._parent_app = parent_app

        self._buildUI()

        
    def _buildUI( self ):
        self.setWindowTitle( "Henchman - V2.0.1" )
        boxWidth = 100
        
        anon = None
        
        # Set Capture Target #####################################################
        grp_1 = QtGui.QGroupBox( "Set Capture Targets" )
        grid  = QtGui.QGridLayout()
        
        grp_1.setLayout( grid )

        # Metadata ###############################################################
        grp_2 = QtGui.QGroupBox( "Day Metadata" )
        grid  = QtGui.QGridLayout()
        
        grp_2.setLayout( grid )
        
        # Metadata ###############################################################
        grp_3 = QtGui.QGroupBox( "Offline Cal Staler" )
        grid  = QtGui.QGridLayout()
        
        grp_3.setLayout( grid )
        
        # Metadata ###############################################################
        grp_4 = QtGui.QGroupBox( "ROM Slater" )
        grid  = QtGui.QGridLayout()
        
        grp_4.setLayout( grid )


        # Assemble UI ############################################################
        tmp_vbox = QtGui.QVBoxLayout()
        tmp_vbox.addWidget( grp_1 )
        tmp_vbox.addWidget( grp_2 )
        tmp_vbox.addWidget( grp_3 )
        tmp_vbox.addWidget( grp_4 )
        tmp_vbox.addStretch( 1 )
        
        self.setLayout( tmp_vbox )
        
    def run( self ):
        self.show()
        #self._generate.setFocus()
        self._parent_app.exec_()
        
        
if __name__ == "__main__":
    _app = QtGui.QApplication( sys.argv )
    ui_test = Henchman( _app )
    ui_test.run()