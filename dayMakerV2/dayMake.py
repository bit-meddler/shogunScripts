from PySide import QtGui, QtCore
import sys


class DayBuild( QtGui.QWidget ):

    def __init__( self, parent_app ):
        super( DayBuild, self ).__init__()
        self._parent_app = parent_app
        self._loadLastSettings()
        self._buildUI()
        
        
    def _loadLastSettings( self ):
        # TODO: Load from ini file
        self.current_client  = "Framestore"
        self.current_project = "Gravity"
        self.cp_map = {
            "Framestore" : ( "Gravity", "Jungle Book" ),
            "Weta" : ( "Apes", "Tintin", "LotR" ),
            "dNeg" : ( "John Carter", "Avengers" ),
        }
        self.client_list  = sorted( self.cp_map.keys() )
        self.client_idx   = self.client_list.index( self.current_client )
        self.project_list = sorted( self.cp_map[ self.current_client ] )
        self.project_idx  = self.project_list.index( self.current_project )

        
    def _updateCpUi( self ):
        self.clients.clear() 
        self.projects.clear()
        self.clients.addItems( self.client_list )
        self.clients.setCurrentIndex( self.client_idx )
        self.projects.addItems( self.project_list )
        self.projects.setCurrentIndex( self.project_idx )

        
    def _buildUI( self ):
        self.setWindowTitle( "Make my Day - V2.0.1" )
        self.boxWidth = 100
        
        # Layout gropup
        self.vbox = QtGui.QVBoxLayout()

        # Select Project Section #################################################
        self.sp_grp = QtGui.QGroupBox( "Select Project" )
        self.sp_grid = QtGui.QGridLayout()
        
        self.sp_cli_lbl = QtGui.QLabel( "Client", self )
        self.sp_grid.addWidget( self.sp_cli_lbl, 0, 0, 1, 2 )
        
        self.clients = QtGui.QComboBox( self )
        self.clients.setMinimumWidth( self.boxWidth )
        self.sp_grid.addWidget( self.clients, 0, 2, 1, 3 )
        
        self.prj_lbl = QtGui.QLabel( "Project", self )
        self.sp_grid.addWidget( self.prj_lbl, 1, 0, 1, 2 )

        self.projects = QtGui.QComboBox( self )
        self.projects.setMinimumWidth( self.boxWidth )
        self.sp_grid.addWidget( self.projects, 1, 2, 1, 3 )
        
        self.prj_lock = QtGui.QCheckBox( "Locked", self )
        self.prj_lock.setCheckState( QtCore.Qt.Checked )
        self.sp_grid.addWidget( self.prj_lock, 1, 6 )
        
        self.prj_path = QtGui.QLineEdit( "Path", self )
        self.prj_path.setReadOnly( True )
        self.sp_grid.addWidget( self.prj_path, 2, 0, 1, 7 )
        
        self.prj_pick_bt = QtGui.QPushButton( "I Chose YOU!", self )
        self.sp_grid.addWidget( self.prj_pick_bt, 3, 0, 1, 3 )
        
        self.prj_update_bt = QtGui.QPushButton( "Update Henchman", self )
        self.sp_grid.addWidget( self.prj_update_bt, 3, 4, 1, 3 )
        
        self.sp_grp.setLayout( self.sp_grid )

        # Create day #############################################################
        self.cd_grp = QtGui.QGroupBox( "Create Day" )
        self.cd_grid = QtGui.QGridLayout()
        
        self.cd_date_lbl = QtGui.QLabel( "Datecode", self )
        self.cd_grid.addWidget( self.cd_date_lbl, 0, 0, 1, 1 )
        
        self.cd_date = QtGui.QLineEdit( "123456", self )
        self.cd_date.setMaximumWidth( 75 )
        self.cd_date.setReadOnly( True )
        self.cd_grid.addWidget( self.cd_date, 1, 0, 1, 1 )
        
        self.cd_stageId_lbl = QtGui.QLabel( "Stage ID:", self )
        self.cd_grid.addWidget( self.cd_stageId_lbl, 1, 1, 1, 1 )
        
        self.cd_loc_lbl = QtGui.QLabel( "Location", self )
        self.cd_grid.addWidget( self.cd_loc_lbl, 0, 2, 1, 1 )
        
        self.cd_stage_lbl = QtGui.QLabel( "Stage", self )
        self.cd_grid.addWidget( self.cd_stage_lbl, 0, 3, 1, 1 )
        
        self.cd_loc = QtGui.QComboBox( self )
        self.cd_loc.addItems( list( "ABCDEFGH" ) ) 
        self.cd_grid.addWidget( self.cd_loc, 1, 2, 1, 1 )
        
        self.cd_stg = QtGui.QSpinBox( self )
        self.cd_stg.setMinimum(  1 )
        self.cd_stg.setMaximum( 99 )
        self.cd_grid.addWidget( self.cd_stg, 1, 3, 1, 1 )
        
        self.date_lock = QtGui.QCheckBox( "Unlock Datecode", self )
        self.date_lock.setCheckState( QtCore.Qt.Unchecked )
        self.cd_grid.addWidget( self.date_lock, 2, 0, 1, 2 )
        
        self.gen_bt = QtGui.QPushButton( "Generate", self )
        self.cd_grid.addWidget( self.gen_bt, 2, 3, 1, 1 )
        
        self.cd_grp.setLayout( self.cd_grid )

        # Assemble UI ###############################################################
        self.vbox.addWidget( self.sp_grp )
        self.vbox.addWidget( self.cd_grp )
        self.vbox.addStretch( 1 )
        self.setLayout( self.vbox ) 
        
        # generate comboBox items
        self._updateCpUi()
        

        
    def run( self ):
        self.show()
        self._parent_app.exec_()
        
        
if __name__ == "__main__":
    print( sys.argv )
    _app = QtGui.QApplication( sys.argv )
    
    ui_test = DayBuild( _app )
    ui_test.run()