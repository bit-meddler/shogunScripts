# Experimental, Self configuring properties.
# UI based on 'Type' and a dict of 'Type-options'
# Types: int, float, string, bool, vec3, Xchoice, Mchoice
# Type Options: min, max, step_lo, step_mid, step_hi, validator, load_cast, save_cast, recev_cast, emit-cast. choices, preview*
#   *preview : a display of the result of user's changes to a setting.  I'm thinking Regexs.
# read/write casting, unified access, Maya-Like dragging could be acheved with custome Widgets
# = { "key" : ( "Label", "ToolTip Text", "Type", "Default", {"Type-Options":None} ) } # no opts should be None

# Maya widget states to emulate: 'Has Keys', 'Key Frame', 'Locked', 'Ready'
# https://knowledge.autodesk.com/support/maya/downloads/caas/CloudHelp/cloudhelp/2017/ENU/Maya/files/GUID-4C954FB2-8B6A-4BBD-9695-DF432616D0D2-htm.html#GUID-4C954FB2-8B6A-4BBD-9695-DF432616D0D2__WS17956D7ADBC6E736-4CE538CA117AE30C631-7FF9
#
# Maya Attribute changes to copy
# https://knowledge.autodesk.com/support/maya/downloads/caas/CloudHelp/cloudhelp/2017/ENU/Maya/files/GUID-6F862011-4578-40A0-9902-786CA2A44AE5-htm.html
# [Return]: Lose Focus, [Enter] Keep Focus.
# Draggable Delta: [Shift] + [MMB-Drag] = lo step, [MMB-Drag] = mid, [Ctrl] + [MMB-Drag] = Hi
# Also [Ctrl] + [LMB-Click] resets to default.

from PySide import QtGui, QtCore


class PIntWidget( QtGui.QSpinBox ):

    def __init__( self, parent_app, default, opts=None ):
        super( PIntWidget, self ).__init__( parent_app )
        self.default = default
        self.min = 0
        self.max = 99
        self.step_lo  = 1
        self.step_mid = 5
        self.step_hi  = 10
        # adapt for special use
        self.recv_cast = None
        self.emit_cast = None
        self.load_cast = None
        self.save_cast = None
        
        if( not opts is None ):
            # take the opts
            for k, v in opts.iteritems():
                setattr( self, k, v )
        self.setRange( self.min, self.max )
        
    def getPValue( self ):
        if( self.emit_cast is None ):
            return self.value()
        else:
            return self.emit_cast( self.value() )
            
    def setPValue( self, val ):
        if( self.recv_cast is None ):
            self.setValue( val )
        else:
            self.setValue( self.recv_cast( val ) )


class PFloatWidget( QtGui.QLineEdit ):

    def __init__( self, parent_app, default, opts=None ):
        super( PFloatWidget, self ).__init__( parent_app )
        self.default = default
        self.min = -1e-99
        self.max = 1e99
        self.step_lo  = 1
        self.step_mid = 10
        self.step_hi  = 1000
        # adapt for special use
        self.recv_cast = None
        self.emit_cast = None
        self.load_cast = None
        self.save_cast = None
        
        if( not opts is None ):
            # take the opts
            for k, v in opts.iteritems():
                setattr( self, k, v )
        #self.setRange( self.min, self.max )
        
    def getPValue( self ):
        fVal = float( self.text() )
        if( self.emit_cast is None ):
            return float( fVal )
        else:
            return self.emit_cast( fVal )
            
    def setPValue( self, val ):
        sVal = str( val )
        if( self.recv_cast is None ):
            self.setText( sVal )
        else:
            self.setText( self.recv_cast( sVal ) )


class PStringWidget( QtGui.QLineEdit ):
    
    def __init__( self, parent_app, default, opts=None ):
        super( PStringWidget, self ).__init__( parent_app )
        self.default = default
        # validator
        self.validator = None
        # adapt for special use
        self.recv_cast = None
        self.emit_cast = None
        self.load_cast = None
        self.save_cast = None
        
        if( not opts is None ):
            # take the opts
            for k, v in opts.iteritems():
                setattr( self, k, v )
        if( not self.validator is None ):
            val = QtGui.QRegExpValidator( QtCore.QRegExp( self.validator ) )
            self.setValidator( val )
            
    def getPValue( self ):
        if( self.emit_cast is None ):
            return self.text()
        else:
            return self.emit_cast( self.text() )
            
    def setPValue( self, val ):
        if( self.recv_cast is None ):
            self.setText( val )
        else:
            self.setText( self.recv_cast( val ) )
    
    
class PXChoiceWidget( QtGui.QComboBox ):
    def __init__( self, parent_app, default, opts=None ):
        super( PXChoiceWidget, self ).__init__( parent_app )
        self.default = default
        # choice list
        self.choices = []
        # adapt for special use
        self.recv_cast = None
        self.emit_cast = None
        self.load_cast = None
        self.save_cast = None
        
        if( not opts is None ):
            # take the opts
            for k, v in opts.iteritems():
                setattr( self, k, v )
        # setup
        for choice in self.choices:
            self.addItem( choice )
        if( not default is None ):
				self.setCurrentIndex( self.findText( default ) )
                
    def getPValue( self ):
        idx = self.currentIndex()
        if( self.emit_cast is None ):
            return self.itemText( idx )
        else:
            return self.emit_cast( self.itemText( idx ) )
            
    def setPValue( self, val ):
        if( self.recv_cast is None ):
            idx = self.findText( val )
        else:
            idx = self.findText( self.recv_cast( val ) )
        if( idx < 0 ):
            idx = 0
        self.setCurrentIndex( idx )

        
class PPane( QtGui.QWidget ):

    def __init__( self, parent_app, obj, prop_dict, properties, title ):
        super( PPane, self ).__init__()
        self._parent_app = parent_app
        self._obj_ref = obj
        self._pd_ref = prop_dict
        self._properties = properties
        self._register = {}
        # Prep UI
        self.setWindowTitle( title )
        # TODO: Should I explicity add a scroll-bar?
        tmp_grid = QtGui.QGridLayout()
        # Properties, Assemble!
        row = 0
        for key in self._properties:
            if( not key in self._pd_ref ):
                continue
            lbl, tip, p_type, default, opts = self._pd_ref[ key ]
            # Label
            anon = QtGui.QLabel( lbl, self )
            tmp_grid.addWidget( anon, row, 0, 1, 1 )
            # input cases
            anon = None
            if( p_type is None ):
                continue
            elif( p_type == "string" ):
                anon = PStringWidget( self, default, opts )
                anon.setPValue( getattr( self._obj_ref, key ) )
            elif( p_type == "int" ):
                anon = PIntWidget( self, default, opts )
                anon.setPValue( getattr( self._obj_ref, key ) )
            elif( p_type == "float" ):
                anon = PFloatWidget( self, default, opts )
                anon.setPValue( getattr( self._obj_ref, key ) )
            elif( p_type == "Xchoice" ):
                anon = PXChoiceWidget( self, default, opts )
                anon.setPValue( getattr( self._obj_ref, key ) )
            # done switching
            # Sanity Check
            if( anon is None ):
                continue
            anon.setToolTip( tip )
            tmp_grid.addWidget( anon, row, 1, 1, 1 )
            self._register[ key ] = anon
            row += 1
        # Finalize
        self.setLayout( tmp_grid )
        
    def _publish( self ):
        ret = {}
        for prop in self._properties:
            if( not prop in self._register ):
                continue
            ret[ prop ] = self._register[ prop ].getPValue()
        return ret


class PPopUp( QtGui.QDialog ):

    def __init__( self, parent_app, obj, update_func ):
        super( PPopUp, self ).__init__()
        self._parent_app  = parent_app
        self._obj_ref     = obj
        self._update_func = update_func
        self._pw = None
        self.title = None
        
    def setProps( self, prop_dict, properties, title ):
        self._pw = PPane( self._parent_app, self._obj_ref, prop_dict, properties, title )
        self.title = title
        self._buildUI()
        
    def _buildUI( self ):
        if( self._pw is None ):
            return
        # Layout UI
        self.setModal( True )
        self.setWindowTitle( self.title )
        vbox = QtGui.QVBoxLayout()
        hbox = QtGui.QHBoxLayout()
        
        vbox.addWidget( self._pw )
    
        apply_but  = QtGui.QPushButton( "Apply and Save" )
        cancel_but = QtGui.QPushButton( "Cancel" )
        hbox.addStretch( 1 )
        hbox.addWidget( apply_but )
        hbox.addWidget( cancel_but )
        
        vbox.addStretch( 1 )
        vbox.addLayout( hbox )
        
        self.setLayout( vbox )
        
        # Hookup Events
        apply_but.clicked.connect( self._apply )
        cancel_but.clicked.connect( self.close )
        
    def _apply( self ):
        #update self._logic_ref with self._pw.properties
        vals = self._pw._publish()
        self._update_func( vals )
        self.close()
        
        
if( __name__ == "__main__" ):
    # Test Props, imitating a Maya Channel Editor.
    import sys
    props = {
        "t_x" : [
            "Translate X",
            "",
            "float",
            1,
            { "min" :  1,
              "max" : 10,
            } ],
        "t_y" : [
            "Translate Y",
            "",
            "float",
            1,
            { "min" :  1,
              "max" : 10,
            } ],
        "t_z" : [
            "Translate Z",
            "",
            "float",
            1,
            { "min" :  1,
              "max" : 10,
            } ],
         "r_x" : [
            "Rotate X",
            "",
            "int",
            1,
            { "min" :  1,
              "max" : 10,
            } ],
        "r_y" : [
            "Rotate Y",
            "",
            "int",
            1,
            { "min" :  1,
              "max" : 10,
            } ],
        "r_z" : [
            "Rotate Z",
            "",
            "int",
            1,
            { "min" :  1,
              "max" : 10,
            } ],
        "s_x" : [
            "Scale X",
            "",
            "int",
            1,
            { "min" :  1,
              "max" : 10,
            } ],
        "s_y" : [
            "Scale Y",
            "",
            "int",
            1,
            { "min" :  1,
              "max" : 10,
            } ],
        "s_z" : [
            "Scale Z",
            "",
            "int",
            1,
            { "min" :  1,
              "max" : 10,
            } ],
    }
    prop_order = [ 't_x', 't_y', 't_z', 'r_x', 'r_y', 'r_z', 's_x', 's_y', 's_z' ]
    X = object()
    for attr in prop_order:
        setattr( X, attr, 1 )
    app = QtGui.QApplication( sys.argv )
    pp = PPane( app, X, props, prop_order, "Test" )
    pp.show()
    sys.exit( app.exec_() )