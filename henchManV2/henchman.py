# -*- coding: ascii -*-
from PySide import QtGui, QtCore
import sys
import os
import datetime
import ConfigParser
from functools import partial


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
        grid_1  = QtGui.QGridLayout()
        anon = QtGui.QLabel( r"Current Client \ Project \ Day ", self )
        grid_1.addWidget( anon, 0, 0, 1, 11 )
        self.day_path = QtGui.QLineEdit( r"blar\blar\blar", self )
        self.day_path.setReadOnly( True )
        grid_1.addWidget( self.day_path, 1, 0, 1, 11 )       
        
        hbox = QtGui.QHBoxLayout()
        self.day_select_but = QtGui.QPushButton( "Update Day", self )
        hbox.addWidget( self.day_select_but )
        self.day_make_but = QtGui.QPushButton( "Launch Day Tool", self )
        hbox.addWidget( self.day_make_but )
        self.day_fresh_but = QtGui.QPushButton( "Refresh Day", self )
        hbox.addWidget( self.day_fresh_but )
        
        hbox.setContentsMargins( 0, 0, 0, 0 )
        
        anon = QtGui.QWidget()
        anon.setContentsMargins( 0, 0, 0, 0 )
        anon.setLayout( hbox )
        grid_1.addWidget( anon, 2, 0, 1, 11 )
        
        hbox = QtGui.QHBoxLayout()
        # TODO, Auto Gen based on globals "sessions"
        self.ses_cal_but = QtGui.QPushButton( "CAL", self )
        hbox.addWidget( self.ses_cal_but )
        self.ses_rom_but = QtGui.QPushButton( "ROM", self )
        hbox.addWidget( self.ses_rom_but )
        self.ses_am_but = QtGui.QPushButton( "AM", self )
        hbox.addWidget( self.ses_am_but )
        self.ses_pm_but = QtGui.QPushButton( "PM", self )
        hbox.addWidget( self.ses_pm_but )
        hbox.setContentsMargins( 0, 0, 0, 0 )
        
        anon = QtGui.QWidget()
        anon.setLayout( hbox )
        anon.setContentsMargins( 0, 0, 0, 0 )
        grid_1.addWidget( anon, 3, 0, 1, 11 )
        grp_1.setLayout( grid_1 )

        # Metadata ###############################################################
        grp_2 = QtGui.QGroupBox( "Day Metadata" )
        grid_2  = QtGui.QGridLayout()
        self.gen_date_but = QtGui.QPushButton( "Date Code", self )
        grid_2.addWidget( self.gen_date_but, 0, 0, 1, 1 )
        self.date_code = QtGui.QLineEdit( "", self )
        grid_2.addWidget( self.date_code, 0, 1, 1, 1 )
        self.gen_time_but = QtGui.QPushButton( "Time Code", self )
        grid_2.addWidget( self.gen_time_but, 0, 3, 1, 1 )
        self.time_code = QtGui.QLineEdit( "", self )
        grid_2.addWidget( self.time_code, 0, 4, 1, 1 )
        grp_2.setLayout( grid_2 )
        
        # Metadata ###############################################################
        grp_3 = QtGui.QGroupBox( "Calibration Helpers" )
        grid_3  = QtGui.QGridLayout()
        self.cal_wand_but = QtGui.QPushButton( "Wand", self )
        grid_3.addWidget( self.cal_wand_but, 0, 0, 1, 1 )
        self.cal_orig_but = QtGui.QPushButton( "Orig", self )
        grid_3.addWidget( self.cal_orig_but, 0, 1, 1, 1 )
        self.cal_floor_but = QtGui.QPushButton( "Floor", self )
        grid_3.addWidget( self.cal_floor_but, 0, 2, 1, 1 )
        self.cal_bing_but = QtGui.QPushButton( "Bings", self )
        grid_3.addWidget( self.cal_bing_but, 0, 3, 1, 1 )
        self.save_wand_but = QtGui.QPushButton( "Save Wand", self )
        grid_3.addWidget( self.save_wand_but, 1, 0, 1, 1 )
        self.save_orig_but = QtGui.QPushButton( "Save Orig", self )
        grid_3.addWidget( self.save_orig_but, 1, 1, 1, 1 )
        self.save_floor_but = QtGui.QPushButton( "Save Floor", self )
        grid_3.addWidget( self.save_floor_but, 1, 2, 1, 1 )
        self.save_bing_but = QtGui.QPushButton( "Save Bings", self )
        grid_3.addWidget( self.save_bing_but, 1, 3, 1, 1 )
        
        grp_3.setLayout( grid_3 )
        
        # Metadata ###############################################################
        grp_4 = QtGui.QGroupBox( "ROM Slater" )
        grid_4  = QtGui.QGridLayout()
        anon = QtGui.QLabel( r"Performer Name", self )
        grid_4.addWidget( anon, 0, 1, 1, 2 )
        anon = QtGui.QLabel( r"Patch Colour", self )
        grid_4.addWidget( anon, 0, 3, 1, 1 )
        self.slate_gen_but = QtGui.QPushButton( "Publish", self )
        grid_4.addWidget( self.slate_gen_but, 1, 0, 1, 1 )
        self.performer_name = QtGui.QLineEdit( "Andy Serkis", self )
        self.performer_name.setToolTip( "<First> <Last>, no initals" )
        self.performer_name.setValidator(
            QtGui.QRegExpValidator( QtCore.QRegExp( "[A-Za-z ]+" ) )
        )
        grid_4.addWidget( self.performer_name, 1, 1, 1, 2 )
        self.performer_patch = QtGui.QComboBox( self )
        self.performer_patch.addItems( ["Red","Green","Blue","Yellow","Pink","Lime","White"] ) 
        grid_4.addWidget( self.performer_patch, 1, 3, 1, 1 )
        anon = QtGui.QLabel( r"Slate Format", self )
        grid_4.addWidget( anon, 2, 0, 1, 1 )
        self.slate_format = QtGui.QLineEdit( "", self )
        self.slate_format.setToolTip( "Generated, Ask someone who knows" )
        self.slate_format.setReadOnly( True )
        grid_4.addWidget( self.slate_format, 2, 1, 1, 3 )
        anon = QtGui.QLabel( r"Slate", self )
        grid_4.addWidget( anon, 3, 0, 1, 1 )
        self.slate_result = QtGui.QLineEdit( "", self )
        grid_4.addWidget( self.slate_result, 3, 1, 1, 3 )
        
        grp_4.setLayout( grid_4 )
        
        radio_gp = QtGui.QButtonGroup( self )
        self.slate_simp_rb = QtGui.QRadioButton( "Simple" )
        radio_gp.addButton( self.slate_simp_rb )
        grid_4.addWidget( self.slate_simp_rb, 4, 0, 1, 1 )
        self.slate_vicon_rb = QtGui.QRadioButton( "Vicon" )
        radio_gp.addButton( self.slate_vicon_rb )
        grid_4.addWidget( self.slate_vicon_rb, 4, 1, 1, 1 )
        self.slate_giant_rb = QtGui.QRadioButton( "Giant" )
        radio_gp.addButton( self.slate_giant_rb )
        grid_4.addWidget( self.slate_giant_rb, 4, 2, 1, 1 )
        self.slate_pipe_rb = QtGui.QRadioButton( "Pipeline" )
        radio_gp.addButton( self.slate_pipe_rb )
        grid_4.addWidget( self.slate_pipe_rb, 4, 3, 1, 1 )
        
        self.rom_snap_but = QtGui.QPushButton( "Snap", self )
        grid_4.addWidget( self.rom_snap_but, 5, 0, 1, 1 )
        self.rom_body_but = QtGui.QPushButton( "Body", self )
        grid_4.addWidget( self.rom_body_but, 5, 1, 1, 1 )
        self.rom_face_but = QtGui.QPushButton( "Face", self )
        grid_4.addWidget( self.rom_face_but, 5, 2, 1, 1 )
        self.rom_prop_but = QtGui.QPushButton( "Prop", self )
        grid_4.addWidget( self.rom_prop_but, 5, 3, 1, 1 )
        
        # Assemble UI ############################################################
        tmp_vbox = QtGui.QVBoxLayout()
        tmp_vbox.addWidget( grp_1 )
        tmp_vbox.addWidget( grp_2 )
        tmp_vbox.addWidget( grp_3 )
        tmp_vbox.addWidget( grp_4 )
        tmp_vbox.addStretch( 1 )
        anon = QtGui.QWidget()
        anon.setLayout( tmp_vbox )
        
        self.setCentralWidget( anon )
        
        # Setup Events ###########################################################
        # self.day_path
        
        self.day_select_but.clicked.connect( self._selectDir )
        # self.day_make_but
        # self.day_fresh_but
        
        self.ses_cal_but.clicked.connect( partial( self.setSession, "CAL" ) )
        self.ses_rom_but.clicked.connect( partial( self.setSession, "ROM" ) )
        self.ses_am_but.clicked.connect( partial( self.setSession, "AM" ) )
        self.ses_pm_but.clicked.connect( partial( self.setSession, "PM" ) )
        
        self.gen_date_but.clicked.connect( self._genDate )
        self.gen_time_but.clicked.connect( self._genTime )
        
        self.cal_wand_but.clicked.connect( partial( self._slateCal, "Wand" ) )
        self.cal_orig_but.clicked.connect( partial( self._slateCal, "Orig" ) )
        self.cal_floor_but.clicked.connect( partial( self._slateCal, "Floor" ) )
        self.cal_bing_but.clicked.connect( partial( self._slateCal, "Survey" ) )
        
        self.save_wand_but.clicked.connect( partial( self._saveCal, "Wand" ) )
        self.save_orig_but.clicked.connect( partial( self._saveCal, "Orig" ) )
        self.save_floor_but.clicked.connect( partial( self._saveCal, "Floor" ) )
        self.save_bing_but.clicked.connect( partial( self._saveCal, "Survey" ) )
        
        
        self.rom_snap_but.clicked.connect( partial( self._generateSlate, "Snap" ) )
        self.rom_body_but.clicked.connect( partial( self._generateSlate, "Body" ) )
        self.rom_face_but.clicked.connect( partial( self._generateSlate, "Face" ) )
        self.rom_prop_but.clicked.connect( partial( self._generateSlate, "Prop" ) )

        self.slate_gen_but.clicked.connect( self._publish )
        
        self.slate_simp_rb.toggled.connect( self._setSlate )
        self.slate_vicon_rb.toggled.connect( self._setSlate )
        self.slate_giant_rb.toggled.connect( self._setSlate )
        self.slate_pipe_rb.toggled.connect( self._setSlate )
        
        # inital state
        self._genDate()
        self._genTime()
        self.slate_vicon_rb.setChecked( True )
        
    def _selectDir( self ):
        # get last PROJECT from cfg
        prj_path = r"C:\ViconData\WETA\EarthVsSoup"
        selected = QtGui.QFileDialog.getExistingDirectory(
                dir=prj_path,
                caption="Select Capture Day",
                options=QtGui.QFileDialog.ShowDirsOnly
        )
        # Sanity Check ?
        
        print( "selected_directory: {}'".format( selected ) )
        # publish to cfg
        self.day_path.setText( selected )
    
    def _slateCal( self, mode ):
        time = self.unUck( self.time_code.text() )
        slate = "{}_{}_calibration_01".format( time[:4], mode )
        self.setSession( "CAL" )
        print( "vicon -setSlate '{}'".format( slate ) )
        
    def _saveCal( self, mode ):
        time = self.unUck( self.time_code.text() )
        slate = "{}_{}_cal_01".format( time[:4], mode )
        print( "vicon -exportCal '{}'".format( slate ) )
        
    def unUck( self, unicode_shit ):
        return unicode_shit.encode( 'ascii', 'ignore' )
        
    def _genDate( self ):
        now = datetime.datetime.now()
        self.date_code.setText( now.strftime( "%y%m%d" ) )
        
    def _timeText( self ):
        now = datetime.datetime.now()
        return now.strftime( "%H%M%S" )
        
    def _genTime( self ):
        self.time_code.setText( self._timeText() )
        
    def setSession( self, session ):
        path = self.unUck( self.day_path.text() )
        print( "vicon -setSession '{}'".format( os.path.join( path, session ) ) )
        
    def _generateSlate( self, mode ):
        # clean and sanity check performer name
        performer = self.unUck( self.performer_name.text() )
        performer = performer.split()
        num = len( performer )
        if( num < 2 ) :
            if( mode == "Prop" ):
                performer.append( "Prop" )
            else:
                performer.append( "__" )
        elif( num > 2):
            new = []
            new.append( performer[0] )
            new.append( performer[-1] )
            performer = new
            
        # get, but don't change the time
        if( int( self._timeText() ) > 120000 ):
            merid = "pm"
        else:
            merid = "am"
            
        patch = self.unUck( self.performer_patch.currentText() )
        
        # assemble metadata
        meta = {
            "datecode": self.unUck( self.date_code.text() ),
            "Performer_first": performer[0],
            "performer_first": performer[0].lower(),
            "Performer_second": performer[1],
            "performer_second": performer[1].lower(),
            "Mode" : mode,
            "mode" : mode.lower(),
            "merid": merid,
            "suffix": 1,
            "patch" : patch,
        }
        slate = self.unUck( self.slate_format.text() )
        slate = slate.format( **meta )
        self.slate_result.setText( slate )
        
    def _publish( self ):
        slate = self.unUck( self.slate_result.text() )
        patch = self.unUck( self.performer_patch.currentText() )
        self.setSession( "ROM" )
        print( "vicon -setSlate '{}'".format( slate ) )
        print( "vicon -setDesc '{}'".format( patch ) )
        
    def _setSlate( self ):
        format = ""
        if( self.slate_simp_rb.isChecked() ):
            format = "{datecode}_{Performer_first}_{Mode}_{suffix:0>2}"
        elif( self.slate_vicon_rb.isChecked() ):
            format = "{datecode}_{Performer_first}{Performer_second[0]}_{Mode}_ROM_{merid}_{suffix:0>2}"
        elif( self.slate_giant_rb.isChecked() ):
            format = "{performer_first[0]}{performer_second[0]}{performer_second[1]}_" + \
                     "{datecode}{merid}_{performer_first}_{performer_second}_{suffix:0>2}.{mode}"
        elif( self.slate_pipe_rb.isChecked() ):
        
            format = "{Performer_first}_{Mode}_ROM_{suffix:0>2}"
        self.slate_format.setText( format )
        
        
    def run( self ):
        self.show()
        #self._generate.setFocus()
        self._parent_app.exec_()
        
        
if __name__ == "__main__":
    _app = QtGui.QApplication( sys.argv )
    ui_test = Henchman( _app )
    ui_test.run()