from PySide import QtGui, QtCore
import sys
import os
import datetime
import ConfigParser
import platform

import enfTool


def _passThru( x ):
    return x

    
class DayBuild( QtGui.QMainWindow ):

    _CFG_FILENAME =   "dayBuild.cfg"
    _CFG_SECTION  =   "SYSTEM"
    _PRJ_SECTION  =   "DAYSETTINGS"
    _SAVED_ATTERS = ( "vicon_root", "current_client", "current_project",
                      "day_format", "datecode_format", "day_validation" )
    _PRJ_ATTERS   = ( "current_location", "current_stage", "day_format",
                      "datecode_format", "last_desc", "_sessions" )
    _DEFAULTS     = {
        "vicon_root"      : "C:\\ViconDB\\",
        "current_client"  : "Framestore",
        "current_project" : "Gravity",
        "day_format"      : "{daycode}_{location}{stage}_{dayname}_{suffix:0>2}",
        "datecode_format" : "%y%m%d",
        "day_validation"  : "[A-Za-z0-9_]+",
        "_sessions"       : ( "CAL", "ROM", "AM", "PM" ),
        "current_location": "A",
        "current_stage"   : 1,
        "last_desc"       : "CaptureDay",
    }
    _READ_CASTS   = {
        "vicon_root"      : _passThru,
        "current_client"  : _passThru,
        "current_project" : _passThru,
        "day_format"      : _passThru,
        "datecode_format" : _passThru,
        "day_validation"  : _passThru,
        "_sessions"       : lambda x: tuple( x.split( "," ) ),
        "current_location": _passThru,
        "current_stage"   : int,
        "last_desc"       : _passThru,
    }
    _WRITE_CASTS  = {
        "vicon_root"      : _passThru,
        "current_client"  : _passThru,
        "current_project" : _passThru,
        "day_format"      : _passThru,
        "datecode_format" : _passThru,
        "day_validation"  : _passThru,
        "_sessions"       : lambda x: ",".join( x ),
        "current_location": _passThru,
        "current_stage"   : str,
        "last_desc"       : _passThru,
    }
    

    def __init__( self, parent_app, clean_start=False ):
        super( DayBuild, self ).__init__()
        
        self._local_data = os.getenv( "LOCALAPPDATA" )# Multiplatform?
        self._config = ConfigParser.RawConfigParser()
        self._config.add_section( self._CFG_SECTION )
        self._cfg_fqp = os.path.join( self._local_data, self._CFG_FILENAME )
        self._parent_app = parent_app
        self.clean_start  = clean_start # TODO: don't load cfg
        
        self._loadAppCfg()
        self._initDate()
        self._buildUI()
    
    
    def _initDate( self ):
        now = datetime.datetime.now()
        self.datecode = now.strftime( self.datecode_format )
        
        
    def _updateClientList( self ):
        self.client_list  = enfTool.scanDB( self.vicon_root )
        
        
    def _updateProjectList( self ):
        self.project_list = enfTool.scanProjects(self.vicon_root+self.current_client+os.path.sep)
        
        
    def _genericConfLoader( self, parser, path, keys, section ):
        if( os.path.isfile( path ) ):
            parser.read( path )            
            for attr in keys:
                try:
                    val = self._READ_CASTS[ attr ]( parser.get( section, attr ) )
                except ConfigParser.NoOptionError:
                    val = self._DEFAULTS[ attr ]
                setattr( self, attr, val )
        else:
            # Load Defaults
            print( "Loading Defaults" )
            for attr in keys:
                setattr( self, attr, self._DEFAULTS[ attr ] )
                
                
    def _genericConfSaver( self, parser, path, keys, section ):
        # safty for new
        if( not parser.has_section( section ) ):
            parser.add_section( section )
        for attr in keys:
            parser.set( section, attr, self._WRITE_CASTS[attr]( getattr( self, attr ) ) )
        if( not os.path.isfile( path ) ):
            os.mkdir( os.path.dirname( path ) )
        fh = open( path, "w" )
        parser.write( fh )
        fh.close()
        
        
    def _loadProjectSettings( self ):
        # TODO: find a placce to save out Project settings per host
        #hostname = platform.uname()[1]
        prj_path = self.vicon_root + self.prj_path + os.sep
        self._settings_path = enfTool.getProjectSettings( prj_path )
        self._prjconf = ConfigParser.RawConfigParser()
        self._genericConfLoader( self._prjconf, self._settings_path, self._PRJ_ATTERS, self._PRJ_SECTION )
        
    
    def _saveProjectSettings( self ):
        self._genericConfSaver( self._prjconf, self._settings_path, self._PRJ_ATTERS, self._PRJ_SECTION )
        
        
    def _loadAppCfg( self ):
        self._genericConfLoader( self._config, self._cfg_fqp, self._SAVED_ATTERS, self._CFG_SECTION )
        # update list data
        self._updateClientList()
        self._updateProjectList()
        # set UI
        try:
            self.client_idx = self.client_list.index( self.current_client )
        except ValueError:
            self.client_idx = 0
        try:
            self.project_idx = self.project_list.index( self.current_project )
        except ValueError:
            self.project_idx = 0


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
        self._loadProjectSettings()
        self._session_name.setText( self.last_desc )
        self._setStage()
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
        # /hack
        self.client_idx = self._clients_combo.currentIndex()
        self.current_client = self._clients_combo.itemText( self.client_idx )
        self.project_idx = 0
        self._updateProjectList()
        self.current_project = self.project_list[ self.project_idx ]
        self._updateCpUi()
        # Hack to dodge Recursion error
        self._clients_combo.currentIndexChanged.connect( self._clientChangeCB )
        # /hack
        
    def _setStage( self ):
        loc_idx = self._location.findText( self.current_location )
        self._location.setCurrentIndex( loc_idx )
        self._stage.setValue( self.current_stage )
        
        
    def _stageCB( self ):
        self.current_location = self._location.itemText( self._location.currentIndex() )
        self.current_stage = self._stage.value()
        
        
    def generate( self ):
        prj_path = self.vicon_root + self.prj_path + os.sep
        dayname = self._session_name.text()
        self.last_desc = dayname
        suffix = enfTool.biggestSuffix( prj_path, dayname ) + 1
        meta_data = {
            "daycode" : self._date_code.text(),
            "location": self.current_location,
            "stage"   : self.current_stage,
            "dayname" : dayname,
            "suffix"  : suffix
        }
        day_code = self.day_format.format( **meta_data )
        print( "enfTool -createDay -prj '{}' -day '{}'".format( prj_path, day_code ) )
        for session in self._sessions:
            print( "enfTool -createSession -prj '{}' -day '{}' -ses '{}'".format( prj_path, day_code, session ) )
        self._saveProjectSettings()

        
    def _launchPrjSettings( self ):
        print( "Project Settings" )


    def _launchSysSettings( self ):
        print( "System Settings" )

     
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
        anon = QtGui.QRegExpValidator( QtCore.QRegExp( self.day_validation ) )
        self._session_name.setValidator( anon )
        tmp_cd_grid.addWidget( self._session_name, 2, 1, 1, 4 )
        
        self._date_lock = QtGui.QCheckBox( "Unlock Datecode", self )
        self._date_lock.setCheckState( QtCore.Qt.Unchecked )
        tmp_cd_grid.addWidget( self._date_lock, 3, 0, 1, 2 )
        
        self._generate = QtGui.QPushButton( "&Generate Day", self )
        tmp_cd_grid.addWidget( self._generate, 3, 3, 1, 1 )
        
        tmp_cd_grp.setLayout( tmp_cd_grid )
        
        # Add Menu Bar #############################################################
        self._menuBar = QtGui.QMenuBar( self )
        self._menuBar.setNativeMenuBar( False ) # Hack to Exit
        file_m = self._menuBar.addMenu( '&File' )
        settings_m = self._menuBar.addMenu( '&Settings' )
        
        exit_itm = QtGui.QAction( 'E&xit', self )        
        exit_itm.triggered.connect( QtGui.qApp.quit )
        file_m.addAction( exit_itm )

        proj_itm = QtGui.QAction( '&Project', self )        
        proj_itm.triggered.connect( self._launchPrjSettings )
        settings_m.addAction( proj_itm )
        
        sys_itm = QtGui.QAction( '&System', self )        
        sys_itm.triggered.connect( self._launchSysSettings )
        settings_m.addAction( sys_itm )
        
        # Assemble UI ###############################################################
        tmp_vbox = QtGui.QVBoxLayout()
        tmp_vbox.addWidget( self._menuBar )
        tmp_vbox.addWidget( tmp_sp_grp )
        tmp_vbox.addWidget( tmp_cd_grp )
        tmp_vbox.addStretch( 1 )
        
        # Hack to get working menu bar
        qw = QtGui.QWidget()
        qw.setLayout( tmp_vbox )
        self.setCentralWidget( qw )
        
        # generate comboBox items
        self._updateCpUi()
        self._projectLockCB()
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
        self._generate.setFocus()
        
    def run( self ):
        self.show()
        #self._generate.setFocus()
        self._parent_app.exec_()
        
        
if __name__ == "__main__":
    _app = QtGui.QApplication( sys.argv )
    ui_test = DayBuild( _app )
    ui_test.run()
