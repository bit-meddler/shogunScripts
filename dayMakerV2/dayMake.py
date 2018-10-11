from PySide import QtGui, QtCore
import sys
import os
import datetime
import ConfigParser
import platform

import enfTool
import utils
from QProperties import PPopUp

class ManagedProps( object ):

    def __init__( self, properties ):
        self.__properties = properties
        
    def acceptDict( self, update ):
        for k, v in update.iteritems():
            setattr( self, k, v )
            
    def genericConfLoader( self, path, tasks, force_defaults=False ):
        update = {}
        parser = ConfigParser.RawConfigParser()
        if( os.path.isfile( path ) and (not force_defaults) ):
            parser.read( path )
            for section, keys in tasks:
                for attr in keys:
                    default, opts = None, None
                    if( attr in self.__properties ):
                        default, opts = self.__properties[ attr ][3], self.__properties[ attr ][4]
                    try:
                        val = parser.get( section, attr )
                    except( ConfigParser.NoOptionError, ConfigParser.NoSectionError ):
                        val = default
                    if( not opts is None ):
                        if( "load_cast" in opts ):
                            val = opts[ "load_cast" ]( val )
                    update[ attr ] = val
        else:
            # Load Defaults
            if( force_defaults ):
                print( "Ignoring '{}'.".format( os.path.basename( path ) ) )
            else:
                print( "Config file '{}' missing.".format( os.path.basename( path ) ) )
            for section, keys in tasks:
                print( "Loading defaults for [{}]".format( section ) )
                for attr in keys:
                    default = ""
                    if( attr in self.__properties ):
                        default = self.__properties[ attr ][3]
                    update[ attr ] = default
        # execute
        self.acceptDict( update )
        
    def genericConfSaver( self, path, task ):
        parser = ConfigParser.RawConfigParser()
        for section, keys in tasks:
            # safty for new cfg file
            if( not parser.has_section( section ) ):
                parser.add_section( section )
            for attr in keys:
                opts = None
                if( attr in self.__properties ):
                    opts = self.__properties[ attr ][4]
                if( not opts is None ):
                    # has opts
                    if( "save_cast" in opts ):
                        cast = opts[ "save_cast" ]
                        parser.set( section, attr, cast( getattr( self, attr ) ) )
                        continue
                # fall through if no cast or opts        
                parser.set( section, attr, getattr( self, attr ) )
                
        utils.mkdirs( path )
        fh = open( path, "w" )
        parser.write( fh )
        fh.close()
        
        
class DBlogic( object ):
    _CFG_FILENAME =   "dayBuild.cfg"
    _CFG_SECTION  =   "SYSTEM"
    _PRJ_SECTION  =   "DAYSETTINGS"
    _SAVED_ATTERS = ( "vicon_root", "current_client", "current_project",
                      "day_format", "datecode_format", "day_validation" )
    _PRJ_ATTERS   = ( "system_fps", "current_location", "prj_rom_fmt", "prj_cal_session", "prj_rom_session", "current_stage", "day_format", "datecode_format", "last_desc", "_sessions" )
    _SYS_ATTERS   = ( "vicon_root", "system_fps", "_sessions",
                      "day_format", "datecode_format", "day_validation" )
    _PROPERTIES   = {
        "vicon_root" : (
            "Vicon Root",
            "Path to the location of the Vicon Database.",
            "string",
            "C:\\ViconDB\\",
             None ),
        "prj_rom_fmt" : (
            "ROM Slate Format",
            "Python format string of the prefered ROM slate for this project. Keys: Performer_first, Performer_second, datecode, suffix, Mode, merid.",
            "string",
            "{datecode}_{Performer_first}{Performer_second[0]}_{Mode}_ROM_{merid}_{suffix:0>2}",
             None ),
        "prj_rom_session" : (
            "ROM Session folder",
            "Folder that ROMs are saved into per shooting day.",
            "string",
            "ROM",
             None ),
        "prj_cal_session" : (
            "Calibration folder",
            "Folder that System Calibrations are saved into per shooting day.",
            "string",
            "CAL",
             None ),
        "datecode_format" : (
            "Date Code Format",
            "Format of Date code, like timesfmt. %y, %m, %d are zero padded.",
            "string",
            "%y%m%d",
            {"validator":"[A-Za-z%]+"} ),
        "day_format" : (
            "Capture Day Format",
             "Format of 'capture day' string.  This is a python format block using {}'s to enclose keys.  Currently supported keys are: daycode, location, stage, dayname, and suffix.",
             "string",
             "{daycode}_{location}{stage}_{dayname}{suffix:0>2}",
              None ), # TODO: Elaborate validator
        "day_validation" : (
            "Day Validation RegEx",
            "A RegEx to Validate allowable capture day names.",
            "string",
            "[A-Za-z0-9_]+",
             None ),
        "_sessions" : (
            "Sessions",
            "Comma Separated list of Sessions a Capture day typically requires",
            "string",
            ( "CAL", "ROM", "AM", "PM" ),
            { "emit_cast" : lambda x: tuple( x.split( "," ) ),
              "recv_cast" : lambda x: ",".join( x ),
              "load_cast" : lambda x: tuple( x.split( "," ) ),
              "save_cast" : lambda x: ",".join( x ),
              "validator" : "[A-Za-z#\-_,]+"
            } ),
        "current_location" : (
            "Studio Location",
            "Location Code for the studio.  Ealing is usually 'A', others are alocated in sequence.  If you don't know, ask someone who does.",
            "Xchoice",
            "A",
            {"choices": list( "ABCDEFGH" )} ),
        "system_fps" : (
            "Framerate",
            "Project Frame rate",
            "Xchoice",
            "119.88",
            { "choices"   : [ "100", "119.88", "125", "149.85", "150" ],
              "emit_cast" : float,
              "recv_cast" : str,
              "load_cast" : float,
              "save_cast" : str,
            } ),
        "current_stage" : (
            "Stage Number",
            "Code number for this setup.  On Location the baseroom (+ ROM Volume) is usually 1.  If you don't know, ask someone who does.",
            "int",
            1,
            { "min"       :   1,
              "max"       :  10,
              "load_cast" : int,
              "save_cast" : str,
            } ),
        # Properties with no UI Hookup?
        "current_client" : (
            None,
            None,
            "string",
            "",
            None ),
        "current_project" : (
            None,
            None,
            "string",
            "",
            None ),
    }
    
    def __init__( self, ui, clean_start=False ):
        super( DBlogic, self ).__init__()
        self._local_data = os.getenv( "LOCALAPPDATA" )# Multiplatform?
        self._config = ConfigParser.RawConfigParser()
        self._ui_ref = ui
        self._config.add_section( self._CFG_SECTION )
        self._cfg_fqp = os.path.join( self._local_data, self._CFG_FILENAME )
        self.clean_start  = clean_start # TODO: don't load cfg
        self._loadAppCfg()
        self._initDate()
        
    def _initDate( self ):
        now = datetime.datetime.now()
        self.datecode = now.strftime( self.datecode_format )
        
    def _updateClientList( self ):
        # print( "enfTool --scanDB -p {}".format( self.vicon_root ) )
        self.client_list  = enfTool.scanDB( self.vicon_root )
        
    def _updateProjectList( self ):
        prj_path = self.vicon_root + self.current_client + os.path.sep
        # print( "enfTool --scanProjects -p {}".format( prj_path ) )
        self.project_list = enfTool.scanProjects( prj_path )

    def acceptDict( self, update ):
        for k, v in update.iteritems():
            setattr( self, k, v )
            
    def acceptDictUI( self, update ):
        self.acceptDict( update )
        # request UI refreash
        self._initDate()
        self._ui_ref._setStage()
        self._ui_ref._dayUpdate()
            
    def _genericConfLoader( self, parser, path, keys, section ):
        update = {}
        if( os.path.isfile( path ) ):
            parser.read( path )            
            for attr in keys:
                default, opts = None, None
                if( attr in self._PROPERTIES ):
                    default, opts = self._PROPERTIES[ attr ][3], self._PROPERTIES[ attr ][4]
                try:
                    val = parser.get( section, attr )
                except ConfigParser.NoOptionError:
                    val = default
                if( not opts is None ):
                    if( "load_cast" in opts ):
                        val = opts[ "load_cast" ]( val )
                update[ attr ] = val
        else:
            # Load Defaults
            print( "Config file '{}' missing, Loading Defaults".format( os.path.basename( path ) ) )
            for attr in keys:
                default = ""
                if( attr in self._PROPERTIES ):
                    default = self._PROPERTIES[ attr ][3]
                update[ attr ] = default
        # execute
        self.acceptDict( update )
        
    def _genericConfSaver( self, parser, path, keys, section ):
        # safty for new
        if( not parser.has_section( section ) ):
            parser.add_section( section )
        for attr in keys:
            opts = None
            if( attr in self._PROPERTIES ):
                opts = self._PROPERTIES[ attr ][4]
            if( not opts is None ):
                # has opts
                if( "save_cast" in opts ):
                    cast = opts[ "save_cast" ]
                    parser.set( section, attr, cast( getattr( self, attr ) ) )
                    continue
            # fall through is no cast or opts        
            parser.set( section, attr, getattr( self, attr ) )
                
        enfTool.mkdirs( path )
        fh = open( path, "w" )
        parser.write( fh )
        fh.close()
        
    def _loadProjectSettings( self ):
        # print( "enfTool --getProjectSettings -p {}".format( prj_path ) )
        # TODO: find a placce to save out Project settings per host
        #hostname = platform.uname()[1]
        prj_path = self.vicon_root + self.prj_path + os.sep
        prj_globals = enfTool.getProjectSettings( prj_path )
        self._settings_path = os.path.join( prj_globals, "settings.ini" )
        self._prjconf = ConfigParser.RawConfigParser()
        self._genericConfLoader( self._prjconf, self._settings_path, self._PRJ_ATTERS, self._PRJ_SECTION )
        
    def _saveProjectSettings( self ):
        self._genericConfSaver( self._prjconf, self._settings_path, self._PRJ_ATTERS, self._PRJ_SECTION )
        
    def _loadAppCfg( self ):
        self._genericConfLoader( self._config, self._cfg_fqp, self._SAVED_ATTERS, self._CFG_SECTION )
        # update list data
        self._updateClientList()
        self._updateProjectList()

    def _saveAppCfg( self ):
        for attr in self._SAVED_ATTERS:
            self._config.set( self._CFG_SECTION, attr, getattr( self, attr ) )
        fh = open( self._cfg_fqp, "w" )
        self._config.write( fh )
        fh.close()

    def generate( self, dayname, daycode ):
        # print( "enfTool --biggestSuffix -p {} -t {}".format( prj_path, dayname ) )
        prj_path = self.vicon_root + self.prj_path + os.sep
        self.last_desc = dayname
        suffix = enfTool.biggestSuffix( prj_path, dayname ) + 1
        meta_data = {
            "daycode" : daycode,
            "location": self.current_location,
            "stage"   : self.current_stage,
            "dayname" : dayname,
            "suffix"  : suffix
        }
        day_code = self.day_format.format( **meta_data )
        #print( "enfTool -createDay -path '{}' -day '{}'".format( prj_path, day_code ) )
        enfTool.createDay( prj_path, day_code )
        
        day_path = os.path.join( prj_path, day_code )
        for session in self._sessions:
            #print( "enfTool -createSession -path '{}' -ses '{}'".format( day_path, session ) )
            enfTool.createSession( day_path, session )
        self._saveProjectSettings()
        # publish to Henchman?

    def newProject( self, name ):
        print( "enfTool -createProject -path '{}' -prj '{}'".format( self.vicon_root, name ) )
        self._updateProjectList()
        self._ui_ref.project_idx = self.project_list.index( name )
        self._ui_ref._updateCpUi()
        self._ui_ref._updatePath()
        
        
class DayBuild( QtGui.QMainWindow ):

    def __init__( self, parent_app, clean_start=False ):
        super( DayBuild, self ).__init__()
        self._parent_app = parent_app
        # Initiate Logic - Load Sys
        self.logic = DBlogic( self )
        # run once??
        try:
            self.client_idx = self.logic.client_list.index( self.logic.current_client )
        except ValueError:
            self.client_idx = 0
        try:
            self.project_idx = self.logic.project_list.index( self.logic.current_project )
        except ValueError:
            self.project_idx = 0
        # Build UI
        self._buildUI()

    def _updatePath( self ):
        self.project_idx = self._project_combo.currentIndex()
        self.logic.current_project = self._project_combo.itemText( self.project_idx )
        # Compose 
        self.logic.prj_path = "{}{}{}".format( self.logic.current_client, os.path.sep, self.logic.current_project )
        self._project_path.setText( self.logic.prj_path )
        # Get Project Settings
        self.logic._loadProjectSettings()
        self._session_name.setText( self.logic.last_desc )
        self._setStage()
        self.logic._saveAppCfg()
    
    def _updateCpUi( self ):
        # Sanity test
        if( ( len( self.logic.client_list ) == 0 ) or ( len( self.logic.project_list ) == 0 ) ):
            return
        # update combos
        self._clients_combo.clear() 
        self._project_combo.clear()
        self._clients_combo.addItems( self.logic.client_list  )
        self._project_combo.addItems( self.logic.project_list )
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
        
    def generate( self ):
        self.logic.generate( self._session_name.text(), self._date_code.text() )
        
    def _chooseCP( self, innerCall=False ):
        # get selected project
        self._project_lock.setCheckState( QtCore.Qt.Checked )
        
    def _dayUpdate( self ):
        self._date_code.setText( self.logic.datecode )
        
    def _dateLockCB( self ):
        lock = not self._date_lock.isChecked()
        self._date_code.setReadOnly( lock )
    
    def _clientChangeCB( self ):
        # Hack to dodge Recursion error
        self._clients_combo.currentIndexChanged.disconnect()
        # hack
        self.client_idx = self._clients_combo.currentIndex()
        self.logic.current_client = self._clients_combo.itemText( self.client_idx )
        self.project_idx = 0
        self.logic._updateProjectList()
        self.logic.current_project = self.logic.project_list[ self.project_idx ]
        self._updateCpUi()
        # Hack to dodge Recursion error
        self._clients_combo.currentIndexChanged.connect( self._clientChangeCB )
        # /hack
        
    def _setStage( self ):
        loc_idx = self._location.findText( self.logic.current_location )
        self._location.setCurrentIndex( loc_idx )
        self._stage.setValue( self.logic.current_stage )
        
    def _stageCB( self ):
        self.logic.current_location = self._location.itemText( self._location.currentIndex() )
        self.logic.current_stage = self._stage.value()
    
    def _launchPrjSettings( self ):
        #print( "Project Settings" )
        self._prjPopup = PPopUp( self._parent_app, self.logic, self._savePrj )
        self._prjPopup.setProps( self.logic._PROPERTIES, self.logic._PRJ_ATTERS, "Project Settings" )
        self._prjPopup.show()
        
    def _launchSysSettings( self ):
        #print( "System Settings" )
        self._prjPopup = PPopUp( self._parent_app, self.logic, self._saveSys )
        self._prjPopup.setProps( self.logic._PROPERTIES, self.logic._SYS_ATTERS, "System Settings" )
        self._prjPopup.show()
        
    def _launchNewProject( self ):
        self.logic.newProject( "TEST" )
        
    def _savePrj( self, update ):
        self.logic.acceptDictUI( update )
        self.logic._saveProjectSettings()
        
    def _saveSys( self, update ):
        self.logic.acceptDictUI( update )
        self.logic._saveAppCfg()
        
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
        
        self._date_code = QtGui.QLineEdit( "", self )
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
        anon = QtGui.QRegExpValidator( QtCore.QRegExp( self.logic.day_validation ) )
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
        self._dayUpdate()
        
        # attach CBs
        self._choose.clicked.connect( self._chooseCP )
        self._generate.clicked.connect( self.generate )
        self._new_prj.clicked.connect( self._launchNewProject )
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
