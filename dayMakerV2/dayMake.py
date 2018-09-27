from PySide import QtGui, QtCore
import sys


class DayBuild( QtGui.QWidget ):

    def __init__( self, parent_app ):
        super( DayBuild, self ).__init__()
        self._parent_app = parent_app
        self._loadLastSettings()
        self._buildUI()
        
        
    def _updateCpMap( self ):
        # Scan Folder structure?
        self.cp_map = {
            "Framestore" : ( "Gravity", "Jungle Book" ),
            "Weta" : ( "Apes", "Tintin", "LotR" ),
            "dNeg" : ( "John Carter", "Avengers" ),
        }
    
    
    def _loadLastSettings( self ):
        # TODO: Load from ini file
        self.current_client   = "Framestore"
        self.current_project  = "Gravity"
        self.current_location = "A"
        self.current_stage    = 1
        # update map
        self._updateCpMap()
        # set UI
        self.client_list  = sorted( self.cp_map.keys() )
        self.client_idx   = self.client_list.index( self.current_client )
        self.project_list = sorted( self.cp_map[ self.current_client ] )
        self.project_idx  = self.project_list.index( self.current_project )

        
    def _updateCpUi( self ):
        # update combos
        self._clients_combo.clear() 
        self._project_combo.clear()
        self._clients_combo.addItems( self.client_list )
        self._project_combo.addItems( self.project_list )
        self._clients_combo.setCurrentIndex( self.client_idx )
        self._project_combo.setCurrentIndex( self.project_idx )
        # Look at client/project current stage?
        
    def _projectLockCB( self ):
        lock = not self._project_lock.isChecked()
        self._new_prj.setEnabled( lock )
        self._clients_combo.setEnabled( lock )
        self._project_combo.setEnabled( lock )
        
        
    def _dateLockCB( self ):
        lock = not self._date_lock.isChecked()
        self._date_code.setReadOnly( lock )
    
    
    def _buildUI( self ):
        self.setWindowTitle( "Make my Day - V2.0.1" )
        boxWidth = 100
        
        anon = None
        
        # Select Project Section #################################################
        tmp_sp_grp  = QtGui.QGroupBox( "Select Project" )
        tmp_sp_grid = QtGui.QGridLayout()
        
        anon = QtGui.QLabel( "Client", self )
        tmp_sp_grid.addWidget( anon, 0, 0, 1, 2 )
        
        self._clients_combo = QtGui.QComboBox( self )
        self._clients_combo.setMinimumWidth( boxWidth )
        tmp_sp_grid.addWidget( self._clients_combo, 0, 2, 1, 3 )
        
        self._new_prj = QtGui.QPushButton( "New Project", self )
        tmp_sp_grid.addWidget( self._new_prj, 0, 5, 1, 2 )
        
        anon = QtGui.QLabel( "Project", self )
        tmp_sp_grid.addWidget( anon, 1, 0, 1, 2 )

        self._project_combo = QtGui.QComboBox( self )
        self._project_combo.setMinimumWidth( boxWidth )
        tmp_sp_grid.addWidget( self._project_combo, 1, 2, 1, 3 )
        
        self._project_lock = QtGui.QCheckBox( "Locked", self )
        self._project_lock.setCheckState( QtCore.Qt.Checked )
        self._project_lock.stateChanged.connect( self._projectLockCB )
        tmp_sp_grid.addWidget( self._project_lock, 1, 6 )
        
        self._project_path = QtGui.QLineEdit( "Path", self )
        self._project_path.setReadOnly( True )
        tmp_sp_grid.addWidget( self._project_path, 2, 0, 1, 7 )
        
        anon = QtGui.QPushButton( "I &Chose YOU!", self )
        anon.setMinimumWidth( 110 )
        tmp_sp_grid.addWidget( anon, 3, 0, 1, 3 )
        
        anon = QtGui.QPushButton( "&Update Henchman", self )
        tmp_sp_grid.addWidget( anon, 3, 4, 1, 3 )
        
        tmp_sp_grp.setLayout( tmp_sp_grid )

        # Create day #############################################################
        tmp_cd_grp  = QtGui.QGroupBox( "Create Day" )
        tmp_cd_grid = QtGui.QGridLayout()
        
        anon = QtGui.QLabel( "Datecode", self )
        tmp_cd_grid.addWidget( anon, 0, 0, 1, 1 )
        
        self._date_code = QtGui.QLineEdit( "123456", self )
        self._date_code.setMaximumWidth( 75 )
        tmp_cd_grid.addWidget( self._date_code, 1, 0, 1, 1 )
        
        anon = QtGui.QLabel( "Stage ID:", self )
        tmp_cd_grid.addWidget( anon, 1, 1, 1, 1 )
        
        anon = QtGui.QLabel( "Location", self )
        tmp_cd_grid.addWidget( anon, 0, 2, 1, 1 )
        
        anon = QtGui.QLabel( "Stage", self )
        tmp_cd_grid.addWidget( anon, 0, 3, 1, 1 )
        
        self._location = QtGui.QComboBox( self )
        self._location.addItems( list( "ABCDEFGH" ) ) 
        tmp_cd_grid.addWidget( self._location, 1, 2, 1, 1 )
        
        self._stage = QtGui.QSpinBox( self )
        self._stage.setRange( 1, 99 )
        tmp_cd_grid.addWidget( self._stage, 1, 3, 1, 1 )
        
        self._date_lock = QtGui.QCheckBox( "Unlock Datecode", self )
        self._date_lock.setCheckState( QtCore.Qt.Unchecked )
        self._date_lock.stateChanged.connect( self._dateLockCB )
        tmp_cd_grid.addWidget( self._date_lock, 2, 0, 1, 2 )
        
        self._generate = QtGui.QPushButton( "&Generate Day", self )
        tmp_cd_grid.addWidget( self._generate, 2, 3, 1, 1 )
        
        tmp_cd_grp.setLayout( tmp_cd_grid )

        # Assemble UI ###############################################################
        tmp_vbox = QtGui.QVBoxLayout()
        tmp_vbox.addWidget( tmp_sp_grp )
        tmp_vbox.addWidget( tmp_cd_grp )
        tmp_vbox.addStretch( 1 )
        self.setLayout( tmp_vbox ) 
        
        # generate comboBox items
        self._updateCpUi()
        self._projectLockCB()
        self._dateLockCB()

        
    def run( self ):
        self.show()
        self._generate.setFocus()
        self._parent_app.exec_()
        
        
if __name__ == "__main__":
    print( sys.argv )
    _app = QtGui.QApplication( sys.argv )
    
    ui_test = DayBuild( _app )
    ui_test.run()