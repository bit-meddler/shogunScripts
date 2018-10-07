# Experimental, Self configuring properties.
# UI based on 'Type' and a dict of 'Type-options'
# Types: int, float, string, bool, vec3, Xchoice, Mchoice
# Type Options: min, max, step_lo, step_mid, step_hi, validator, read_cast, write_cast, choices, preview*
#   *preview : a display of the result of user's changes to a setting.  I'm thinking Regexs.
# read/write casting, unified access, Maya-Like dragging could be acheved with custome Widgets
# = { "key" : ( "Label", "ToolTip Text", "Type", "Default", {"Type-Options":None} ) } # no opts should be None
from PySide import QtGui, QtCore


class PIntWidget( QtGui.QSpinBox ):

    def __init__( self, parent_app, default, opts=None ):
        super( PIntWidget, self ).__init__( parent_app )
        self.default = default
        self.min = 0
        self.max = 99
        # TODO: Interactive Events
        # Draggable like Maya: [Shift] + [MMB-Drag] = lo step, [MMB-Drag] = mid, [Ctrl] + [MMB-Drag] = Hi
        # Also [Ctrl] + [LMB-Click] resets to default.
        self.step_lo = 1
        self.step_mid = 5
        self.step_hi = 10
        # adapt for special use
        self.read_cast = None
        self.write_cast = None
        if( not opts is None ):
            # take the opts
            for k, v in opts.iteritems():
                setattr( self, k, v )
        self.setRange( self.min, self.max )
        
    def getPValue( self ):
        if( self.write_cast is None ):
            return self.value()
        else:
            return self.write_cast( self.value() )
            
    def setPValue( self, val ):
        if( self.read_cast is None ):
            self.setValue( val )
        else:
            self.setValue( self.read_cast( val ) )


class PStringWidget( QtGui.QLineEdit ):
    
    def __init__( self, parent_app, default, opts=None ):
        super( PStringWidget, self ).__init__( parent_app )
        self.default = default
        # validator
        self.validator = None
        # adapt for special use
        self.read_cast = None
        self.write_cast = None
        if( not opts is None ):
            # take the opts
            for k, v in opts.iteritems():
                setattr( self, k, v )
        if( not self.validator is None ):
            val = QtGui.QRegExpValidator( QtCore.QRegExp( self.validator ) )
            self.setValidator( val )
            
    def getPValue( self ):
        if( self.write_cast is None ):
            return self.text()
        else:
            return self.write_cast( self.text() )
            
    def setPValue( self, val ):
        if( self.read_cast is None ):
            self.setText( val )
        else:
            self.setText( self.read_cast( val ) )
    
    
class PXChoiceWidget( QtGui.QComboBox ):
    def __init__( self, parent_app, default, opts=None ):
        super( PXChoiceWidget, self ).__init__( parent_app )
        self.default = default
        # choice list
        self.choices = []
        # adapt for special use
        self.read_cast = None
        self.write_cast = None
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
        if( self.write_cast is None ):
            return self.itemText( idx )
        else:
            return self.write_cast( self.itemText( idx ) )
            
    def setPValue( self, val ):
        if( self.read_cast is None ):
            idx = self.findText( val )
        else:
            idx = self.findText( self.read_cast( val ) )
        if( idx < 0 ):
            idx = 0
        self.setCurrentIndex( idx )

        
class PPane( QtGui.QWidget ):

    def __init__( self, parent_app, prop_dict, properties, title ):
        super( PPane, self ).__init__()
        self._parent_app = parent_app
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
                anon.setPValue( default )
            elif( p_type == "int" ):
                anon = PIntWidget( self, default, opts )
                anon.setPValue( default )
            elif( p_type == "Xchoice" ):
                anon = PXChoiceWidget( self, default, opts )
                anon.setPValue( default )
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

    def __init__( self, parent_app, update_func ):
        super( PPopUp, self ).__init__()
        self._parent_app  = parent_app
        self._update_func = update_func
        self._pw = None
        self.title = None
        
    def setProps( self, prop_dict, properties, title ):
        self._pw = PPane( self._parent_app, prop_dict, properties, title )
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
        print vals
        self._update_func( vals )
        self.close()
        
