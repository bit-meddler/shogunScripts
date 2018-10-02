from PySide import QtGui, QtCore
import sys
import os
import datetime
import ConfigParser

import enfTool


class DayBuild( QtGui.QWidget ):

    _SAVED_ATTERS = ( 'vicon_root', 'current_client', 'current_project',
                      'day_format', 'datecode_format' )
    _CFG_SECTION  = "SYSTEM"
    _CFG_FILENAME = "dayBuild.cfg"
    _PRJ_SECTION  = "DAYSETTINGS"
    _PRJ_ATTERS   = ( "current_location", "current_stage", "day_format", "datecode_format" )
    _PRJ_CASTS    = ( str, int, str, str )
    
    
    def __init__( self, parent_app ):
        super( DayBuild, self ).__init__()
        self._local_data = os.getenv( "LOCALAPPDATA" )
        self._config = ConfigParser.RawConfigParser()
        self._config.add_section( self._CFG_SECTION )
        self._cfg_fqp = os.path.join( self._local_data, self._CFG_FILENAME )
        self._parent_app = parent_app
        self._loadAppCfg()
        self._initDate()
        self._buildUI()
        
        
    def _updateCpMap( self ):
        # Bodge for UI testing
        self.cp_map = {
            "Framestore" : ( "Gravity", "Jungle Book" ),
            "Weta" : ( "Apes", "Tintin", "LotR" ),
            "dNeg" : ( "John Carter", "Avengers" ),
        }
    
    
    def _initDate( self ):
        now = datetime.datetime.now()
        self.datecode = now.strftime( self.datecode_format )
        
        
    def _updateClientList( self ):
        self.client_list  = enfTool.scanDB( self.vicon_root )
        
        
    def _updateProjectList( self ):
        self.project_list = enfTool.scanProjects(
            self.vicon_root + self.current_client + os.path.sep
        )
        
    
    def _getProjectSettings( self ):
        # TODO: Load from ini file
        prj_path = self.vicon_root + self.prj_path + os.sep
        settings_path = enfTool.getProjectSettings( prj_path )
        if( os.path.isfile( settings_path ) ):
            prjconf = ConfigParser.RawConfigParser()
            prjconf.read( settings_path )
            for attr, cast in zip( self._PRJ_ATTERS, self._PRJ_CASTS ):
                val = prjconf.get( self._PRJ_SECTION, attr )
                setattr( self, attr, cast( val ) )
            ses = prjconf.get( self._PRJ_SECTION, "sessions" )
            self._sessions = tuple( ses.split( "," ) )
        else:
            # defaults
            self._sessions        = ( "CAL", "ROM", "AM", "PM" )
            self.current_location = "A"
            self.current_stage    = 1
            self.day_format       = "{daycode}_{location}{stage}_{dayname}"
            self.datecode_format  = "%y%m%d"
    
    
    def _loadAppCfg( self ):
        if( os.path.isfile( self._cfg_fqp ) ):
            self._config.read( self._cfg_fqp )            
            for attr in self._SAVED_ATTERS:
                val = self._config.get( self._CFG_SECTION, attr )
                setattr( self, attr, val )
        else:
            # Defaults
            self.vicon_root      = "C:\\ViconData\\"
            self.current_client  = "Framestore"
            self.current_project = "Gravity"
            self.day_format      = "{daycode}_{location}{stage}_{dayname}"
            self.datecode_format = "%y%m%d"
            
        # update list data
        self._updateCpMap()
        self._updateClientList()
        self._updateProjectList()
        # set UI
        self.client_idx  = self.client_list.index(  self.current_client  )
        self.project_idx = self.project_list.index( self.current_project )

        
    def _saveAppCfg( self ):
        for attr in self._SAVED_ATTERS:
            self._config.set( self._CFG_SECTION, attr, getattr( self, attr ) )
        fh = open( self._cfg_fqp, "w" )
        self._config.write( fh )
        fh.close()
            
        
    def _updatePath( self ):
        self.project_idx = self._project_combo.currentIndex()
        self.current_project = self._project_combo.itemText( self.project_idx )
        # Compose 
        self.prj_path = "{}{}{}".format( self.current_client, os.path.sep, self.current_project )
        self._project_path.setText( self.prj_path )
        # Get Project Settings
        self._getProjectSettings()
        self._saveAppCfg()
        
    
    def _updateCpUi( self ):
        # Sanity test
        if( ( len( self.client_list ) == 0 ) or ( len( self.project_list ) == 0 ) ):
            return
        # update combos
        self._clients_combo.clear() 
        self._project_combo.clear()
        self._clients_combo.addItems( self.client_list  )
        self._project_combo.addItems( self.project_list )
        self._clients_combo.setCurrentIndex( self.client_idx  )
        self._project_combo.setCurrentIndex( self.project_idx )
        # Look at client/project current stage?
        
        
    def _projectLockCB( self ):
        lock = not self._project_lock.isChecked()
        self._new_prj.setEnabled( lock )
        self._clients_combo.setEnabled( lock )
        self._project_combo.setEnabled( lock )
        if not lock: # When applying lock, update
            self._updatePath()
        
        
    def _chooseCP( self, innerCall=False ):
        # get selected project
        self._project_lock.setCheckState( QtCore.Qt.Checked )
        
        
    def _dateLockCB( self ):
        lock = not self._date_lock.isChecked()
        self._date_code.setReadOnly( lock )
    
    
    def _clientChangeCB( self ):
        # Hack to dodge Recursion error
        self._clients_combo.currentIndexChanged.disconnect()
        
        self.client_idx = self._clients_combo.currentIndex()
        self.current_client = self._clients_combo.itemText( self.client_idx )
        
        # TODO: update client's last used project from client globals
        self.project_idx = 0
        
        self._updateProjectList()
        self.current_project = self.project_list[ self.project_idx ]
        self._updateCpUi()
        # Hack to dodge Recursion error
        self._clients_combo.currentIndexChanged.connect( self._clientChangeCB )
        
        
    def _setStage( self ):
        loc_idx = self._location.findText( self.current_location )
        self._location.setCurrentIndex( loc_idx )
        self._stage.setValue( self.current_stage )
        
        
    def _stageCB( self ):
        self.current_location = self._location.itemText( self._location.currentIndex() )
        self.current_stage = self._stage.value()
        
        
    def generate( self ):
        prj_path = self.vicon_root + self.prj_path + os.sep
        print( "enfTool -scanDays -prj '{}'".format( prj_path ) )
        # TODO: determine highest suffix of 'session_name' in list of days
        meta_data = {
            "daycode" : self._date_code.text(),
            "location": self.current_location,
            "stage"   : self.current_stage,
            "dayname" : self._session_name.text()
        }
        day_code = self.day_format.format( **meta_data )
        print( "enfTool -createDay -prj '{}' -day '{}'".format( prj_path, day_code ) )
        for session in self._sessions:
            print( "enfTool -createSession -prj '{}' -day '{}' -ses '{}'".format( prj_path, day_code, session ) )
        
        
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
        tmp_sp_grid.addWidget( self._project_lock, 1, 6 )
        
        self._project_path = QtGui.QLineEdit( "Path", self )
        self._project_path.setReadOnly( True )
        tmp_sp_grid.addWidget( self._project_path, 2, 0, 1, 7 )
        
        self._choose = QtGui.QPushButton( "I &Chose YOU!", self )
        self._choose.setMinimumWidth( 110 )
        self._choose.setAutoRepeat( False )
        tmp_sp_grid.addWidget( self._choose, 3, 0, 1, 3 )
        
        anon = QtGui.QPushButton( "&Update Henchman", self )
        tmp_sp_grid.addWidget( anon, 3, 4, 1, 3 )
        
        tmp_sp_grp.setLayout( tmp_sp_grid )

        # Create day #############################################################
        tmp_cd_grp  = QtGui.QGroupBox( "Create Day" )
        tmp_cd_grid = QtGui.QGridLayout()
        
        anon = QtGui.QLabel( "Datecode", self )
        tmp_cd_grid.addWidget( anon, 0, 0, 1, 1 )
        
        self._date_code = QtGui.QLineEdit( self.datecode, self )
        self._date_code.setMaximumWidth( 75 )
        self._date_code.setReadOnly( True )
        tmp_cd_grid.addWidget( self._date_code, 1, 0, 1, 1 )
        
        anon = QtGui.QLabel( "Stage ID:", self )
        anon.setAlignment( QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter )
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
        
        anon = QtGui.QLabel( "Description", self )
        anon.setAlignment( QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter )
        tmp_cd_grid.addWidget( anon, 2, 0, 1, 1 )
        
        self._session_name = QtGui.QLineEdit( "CaptureDay", self )
        self._session_name.setReadOnly( False )
        tmp_cd_grid.addWidget( self._session_name, 2, 1, 1, 4 )
        
        self._date_lock = QtGui.QCheckBox( "Unlock Datecode", self )
        self._date_lock.setCheckState( QtCore.Qt.Unchecked )
        tmp_cd_grid.addWidget( self._date_lock, 3, 0, 1, 2 )
        
        self._generate = QtGui.QPushButton( "&Generate Day", self )
        tmp_cd_grid.addWidget( self._generate, 3, 3, 1, 1 )
        
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
        # self._dateLockCB()
        # self._updatePath()
        self._setStage()
        self._stageCB()
        
        # attach CBs
        self._choose.clicked.connect( self._chooseCP )
        self._generate.clicked.connect( self.generate )
        self._project_lock.stateChanged.connect( self._projectLockCB )
        self._date_lock.stateChanged.connect( self._dateLockCB )
        self._clients_combo.currentIndexChanged.connect( self._clientChangeCB )
        self._location.currentIndexChanged.connect( self._stageCB )
        self._stage.valueChanged.connect( self._stageCB )
        
        
    def run( self ):
        self.show()
        self._generate.setFocus()
        self._parent_app.exec_()
        
        
if __name__ == "__main__":
    _app = QtGui.QApplication( sys.argv )
    ui_test = DayBuild( _app )
    ui_test.run()