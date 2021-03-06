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
# Draggable Delta: [Shift] + [MMB-Drag] = lo step, [MMB-Drag] = mid, [Alt] + [MMB-Drag] = Hi
# Also [Ctrl] + [LMB-Click] resets to default.

from PySide import QtGui, QtCore
import re

class PSelectableLabel( QtGui.QLabel ):
    # I can probably do this at a 'container' level, so may not need to subclass this.
    def __init__( self, text=None, parent=None, f=0 ):
        super( PSelectableLabel, self ).__init__( text, parent, f )
        # ui Grouping
        self.group = None
        
        
class PIntWidget( QtGui.QSpinBox ):

    def __init__( self, parent_app, default, opts=None ):
        super( PIntWidget, self ).__init__( parent_app )
        self.default = default
        self.min = 0
        self.max = 99
        self.step_lo  = 1
        self.step_mid = 5
        self.step_hi  = 10
        self.step_scale = 16.
        # adapt for special use
        self.recv_cast = None
        self.emit_cast = None
        self.load_cast = None
        self.save_cast = None        
        # take the opts
        if( not opts is None ):
            for k, v in opts.iteritems():
                setattr( self, k, v )
        # take any updates to the range
        self.setRange( self.min, self.max )
        # Spinner
        self._mousing = False
        # initalize to Default
        self.setValue( self.default )
        self._last_reason = None
        self._my_lab = None
        self.editingFinished.connect( self._done )
        
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

    def _done( self ):
        # test for membership of selection
        parent = self.parent()
        val = self.value()
        this = self._my_lab
        if( this in parent._selected ):
            for lab in parent._selected:
                if self == lab: continue
                widget = lab.buddy()
                widget.setValue( val )
        # self.valueChanged.emit( val )
        
    # TODO: Could the following be done in an event Filter? ##########################
    def mousePressEvent( self, event ):
        super( PIntWidget, self ).mousePressEvent( event )
        if( event.button() & QtCore.Qt.MiddleButton ):
            self._mousing = True
            self._start_pos = event.pos()
            self.setCursor( QtCore.Qt.SizeVerCursor )
            self._startVal = self.value()

    def mouseMoveEvent( self, event ):
        if not self._mousing:
            return
            
        mods = QtGui.QApplication.keyboardModifiers()
        
        delta = self.step_mid
        if( mods & QtCore.Qt.ShiftModifier ):
            delta = self.step_lo
        elif( mods & QtCore.Qt.AltModifier ):
            delta = self.step_hi
        # TODO: Do this nicely
        change = ( event.pos().y() - self._start_pos.y() )
        val = self._startVal + int( -1. * (change/self.step_scale) * delta )
        #self.setValue( val )

    def mouseReleaseEvent( self, event ):
        super( PIntWidget, self ).mouseReleaseEvent( event )
        mods = QtGui.QApplication.keyboardModifiers()
        if( mods & QtCore.Qt.ControlModifier ):
            self.setValue( self.default )
        self._mousing = False
        self.unsetCursor()
        self.editingFinished.emit()
        
    def focusInEvent( self, event ):
        self._last_reason = event.reason()
        super( PIntWidget, self ).focusInEvent( event )
    # mouse event over-rides ##########################################################
        
        
class PMathValidator( QtGui.QValidator ):
    """
        Accept Scientific notation in the lineEdit.
        Also interprets basic expressions ( +=, -=, /=, *=) followed by a value
        which may also be in scientific notation
    """
    def __init__( self ):
        self._floatOK = re.compile( r"(([+\-*\\]\=)?([+-]?\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)" )
        
    def _test( self, text ):
        matched = self._floatOK.search( text )
        if matched: #Guard for Non-Matching
            return (matched.groups()[ 0 ] == text)
        else:
            return False
    
    def validate( self, text, pos ):
        if( self._test( text ) ):
            return self.State.Acceptable
        elif( (text=="") or (text[ pos-1 ] in 'e.-+/*=') ):
            return self.State.Intermediate
            
        return self.State.Invalid
        
    def valueFromText( self, text, previous=0. ):
        matched = self._floatOK.search( text )
        match, expression, mantissa, _, exponent = matched.groups()
        value = previous
        if( not expression is None ):
            mantissa = 1  if mantissa == None else mantissa
            exponent = "" if exponent == None else exponent
            change = float( mantissa + exponent ) #rebuild sci notation
            if( expression == "+=" ):
                value += change
            elif( expression == "-=" ):
                value -= change
            elif( expression == "*=" ):
                value *= change
            elif( expression == "/=" ):
                value /= change
        else:
            value = float( match )
        return value
        
    def fixup( self, text ):
        matched = self._floatOK.search( text )
        if matched: #Guard for Non-Matching
            return matched.groups()[ 0 ]
        else:
            return ""
        
        
class PFloatWidget( QtGui.QDoubleSpinBox ):

    def __init__( self, parent_app, default, opts=None ):
        super( PFloatWidget, self ).__init__( parent_app )
        self._mousing = False
        self.default = default
        self.min = -1e-99
        self.max = 1e99
        self.step_lo  = 1.
        self.step_mid = 10.
        self.step_hi  = 1000.
        self.step_scale = 16.
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
        self.validator = PMathValidator()
        self.setDecimals( 5 )
        self._last_reason = None
        self._my_lab = None
        self.editingFinished.connect( self._done )
        
    def getPValue( self ):
        fVal = float( self.value() )
        if( self.emit_cast is None ):
            return fVal
        else:
            return self.emit_cast( fVal )
            
    def setPValue( self, val ):
        sVal = float( val )
        if( self.recv_cast is None ):
            self.setValue( sVal )
        else:
            self.setValue( self.recv_cast( sVal ) )
            
    def _done( self ):
        # test for membership of selection
        parent = self.parent()
        val = self.value()
        this = self._my_lab
        if( this in parent._selected ):
            for lab in parent._selected:
                if self == lab: continue
                widget = lab.buddy()
                widget.setValue( val )
                
    def validate( self, text, position ):
        if( self._mousing ): # Skip validation while dialing
            return self.validator.State.Intermediate
            
        return self.validator.validate( text, position )

    def fixup( self, text ):
        return self.validator.fixup( text )

    def valueFromText( self, text ):
        return self.validator.valueFromText( text, self._startVal )

    def setValue( self, val ):
        #print "setting", val
        self._startVal = val
        super( PFloatWidget, self ).setValue( val )
        
    # TODO: Could the following be done in an event Filter? ##########################
    def mousePressEvent( self, event ):
        super( PFloatWidget, self ).mousePressEvent( event )
        if( event.button() & QtCore.Qt.MiddleButton ):
            self._mousing = True
            self._start_pos = event.pos()
            self.setCursor( QtCore.Qt.SizeVerCursor )
            self._startVal = self.value()

    def mouseMoveEvent( self, event ):
        if not self._mousing:
            return
            
        mods = QtGui.QApplication.keyboardModifiers()
        
        delta = self.step_mid
        if( mods & QtCore.Qt.ShiftModifier ):
            delta = self.step_lo
        elif( mods & QtCore.Qt.AltModifier ):
            delta = self.step_hi
        # TODO: Do this nicely
        change = ( event.pos().y() - self._start_pos.y() )
        val = self._startVal + int( -1. * (change/self.step_scale) * delta )
        #self.setValue( val )
        self.lineEdit().setText( str( val ) )
        
    def mouseReleaseEvent( self, event ):
        super( PFloatWidget, self ).mouseReleaseEvent( event )
        mods = QtGui.QApplication.keyboardModifiers()
        if( mods & QtCore.Qt.ControlModifier ):
            self.setValue( self.default )
        self._mousing = False
        self.unsetCursor()
        self.editingFinished.emit()
        
    def focusInEvent( self, event ):
        self._last_reason = event.reason()
        super( PFloatWidget, self ).focusInEvent( event )
    # mouse event over-rides ##########################################################     
     
        
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
            
        self._last_reason = None
        self._my_lab = None
        
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
            
    def focusInEvent( self, event ):
        self._last_reason = event.reason()
        super( PStringWidget, self ).focusInEvent( event )
    
    
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
                
        self._last_reason = None
        self._my_lab = None
        
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
        
    def focusInEvent( self, event ):
        self._last_reason = event.reason()
        super( PXChoiceWidget, self ).focusInEvent( event )
        
        
KNOWN_P_WIDGETS = ( PXChoiceWidget, PStringWidget, PFloatWidget, PIntWidget )

class PPane( QtGui.QWidget ):

    def __init__( self, parent_app, obj, prop_dict, prop_order, title ):
        super( PPane, self ).__init__()
        self._parent_app = parent_app
        self._obj_ref = obj
        self._pd_ref = prop_dict
        self._prop_order = prop_order
        self._selected = []
        self._pending = []
        self._last_selected = None
        self._dragging = False
        self._register = {}
        # Prep UI
        self.setWindowTitle( title )
        # TODO: Should I explicity add a scroll-bar?
        tmp_grid = QtGui.QGridLayout()
        # prop_order, Assemble!
        # TODO: Need some way of grouping PSLs, so int->int->!float + Exclude nonsense options
        row = 0
        for key in self._prop_order:
            if( not key in self._pd_ref ):
                continue
            lbl, tip, p_type, default, opts = self._pd_ref[ key ]
            # Label
            lab = PSelectableLabel( lbl, self )
            lab.setContentsMargins( 3, 3, 3, 3 )
            if( not opts is None ):
                if( "group" in opts ):
                    lab.group = opts[ "group" ]
                
            tmp_grid.addWidget( lab, row, 0, 1, 1 )
            # input cases
            widget = None
            if( p_type is None ):
                continue
            elif( p_type == "string" ):
                widget = PStringWidget( self, default, opts )
                widget.setPValue( getattr( self._obj_ref, key ) )
            elif( p_type == "int" ):
                widget = PIntWidget( self, default, opts )
                widget.setPValue( getattr( self._obj_ref, key ) )
            elif( p_type == "float" ):
                widget = PFloatWidget( self, default, opts )
                widget.setPValue( getattr( self._obj_ref, key ) )
            elif( p_type == "Xchoice" ):
                widget = PXChoiceWidget( self, default, opts )
                widget.setPValue( getattr( self._obj_ref, key ) )
            # done switching
            # Sanity Check
            if( widget is None ):
                continue
            widget.setToolTip( tip )
            lab.setBuddy( widget )
            widget._my_lab = lab
            tmp_grid.addWidget( widget, row, 1, 1, 1 )
            self._register[ key ] = widget
            row += 1
        # Finalize
        tmp_grid.setContentsMargins( 2, 1, 2, 1 )
        QtGui.qApp.focusChanged.connect( self._fccb )
        self.setLayout( tmp_grid )
        self.setContentsMargins( 1, 1, 1, 1 )
        self._tweakStyle()
        
    def _tweakStyle( self ):
        # states: QPalette.Disabled, QPalette.Active, QPalette.Inactive, QPalette.Normal
        light = QtGui.QPalette().color( QtGui.QPalette.Active, QtGui.QPalette.Light ).name()
        mid = QtGui.QPalette().color( QtGui.QPalette.Active, QtGui.QPalette.Midlight ).name()
        dark = QtGui.QPalette().color( QtGui.QPalette.Active, QtGui.QPalette.Dark ).lighter(110).name()
        window = QtGui.QPalette().color( QtGui.QPalette.Active, QtGui.QPalette.Window ).name()
        highlight = QtGui.QPalette().color( QtGui.QPalette.Active, QtGui.QPalette.Highlight ).name()
        lighthigh = QtGui.QPalette().color( QtGui.QPalette.Active, QtGui.QPalette.Highlight ).lighter().name()
        self._style_highlight = "background-color: {}".format( highlight )
        self._style_normal = "background-color: {}".format( window ) # none
        self._style_light = "background-color: {}".format( mid )
        self._style_selected = "background-color: {}".format( dark )
        self._style_was_highlighted = "background-color: {}".format( lighthigh )
        
    def _publish( self ):
        ret = {}
        for prop in self._prop_order:
            if( not prop in self._register ):
                continue
            ret[ prop ] = self._register[ prop ].getPValue()
        return ret
        
    def _clearLabSelection( self ):
        for prop in self._selected:
            prop.setStyleSheet( self._style_normal )
        self._selected = []
        
    def _softLightPending( self ):
        for prop in self._pending:
            if( prop != self._last_selected ):
                prop.setStyleSheet( self._style_was_highlighted )
            
    def mousePressEvent( self, event ):
        recever = self.childAt( event.pos() )
        invert = bool( QtGui.QApplication.keyboardModifiers() & QtCore.Qt.ControlModifier )
        if( (event.button() & QtCore.Qt.LeftButton) and
            (type( recever ) == PSelectableLabel)
        ):
            if( recever.group == None ):
                return
            if( invert ):
                recever.setStyleSheet( self._style_highlight )
            else:
                self._clearLabSelection()
                recever.setStyleSheet( self._style_highlight )
            self._dragging = True
            self._pending  = [ recever ]
            self._last_selected = recever
        super( PPane, self ).mousePressEvent( event )
            
    def mouseMoveEvent( self, event ):
        recever = self.childAt( event.pos() )
        if( (type( recever ) == PSelectableLabel) and
            (not recever in self._pending) and
            (self._dragging)
        ):
            if( recever.group == None ):
                return
            self._last_selected = recever
            recever.setStyleSheet( self._style_highlight )
            self._pending.append( recever )
            self._softLightPending()
        super( PPane, self ).mouseMoveEvent( event )

    def mouseReleaseEvent( self, event ):
        recever = self.childAt( event.pos() )
        if( (event.button() & QtCore.Qt.LeftButton) and
            (type( recever ) == PSelectableLabel)
        ):
            invert = bool( QtGui.QApplication.keyboardModifiers() & QtCore.Qt.ControlModifier )
            self._dragging = False
            # toggle select...
            for prop in self._pending:
                if( (prop in self._selected) and invert ):
                    # deselect case
                    self._selected.remove( prop )
                    prop.setStyleSheet( self._style_normal )
                else:
                    self._selected.append( prop )
            self._pending = []
            for prop in self._selected:
                prop.setStyleSheet( self._style_selected )
                
            num_sel = len( self._selected )
            if( num_sel > 0 ):
                self._selected[-1].buddy().setFocus( QtCore.Qt.OtherFocusReason )
            if( num_sel == 1 ):
                self._selected[0].setStyleSheet( self._style_normal )
                
        super( PPane, self ).mouseReleaseEvent( event )
        
    def _fccb( self, old, new ):
        if( type( new ) in KNOWN_P_WIDGETS ):

            if( new._last_reason == QtCore.Qt.FocusReason.OtherFocusReason ):
                return
            if( new._my_lab in self._selected ):
                # Allow focus change with selected Properties
                return
            # Deselect
            self._clearLabSelection()
            
            
class PPopUp( QtGui.QDialog ):

    def __init__( self, parent_app, obj, update_func ):
        super( PPopUp, self ).__init__()
        self._parent_app  = parent_app
        self._obj_ref     = obj
        self._update_func = update_func
        self._pw = None
        self.title = None
        
    def setProps( self, prop_dict, prop_order, title ):
        self._pw = PPane( self._parent_app, self._obj_ref, prop_dict, prop_order, title )
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
        #update self._logic_ref with self._pw.prop_order
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
              "group": "xform",
            } ],
        "t_y" : [
            "Translate Y",
            "",
            "float",
            1,
            { "min" :  1,
              "max" : 10,
              "group": "xform",
            } ],
        "t_z" : [
            "Translate Z",
            "",
            "float",
            1,
            { "min" :  1,
              "max" : 10,
              "group": "xform",
            } ],
         "r_x" : [
            "Rotate X",
            "",
            "int",
            1,
            { "min" :  1,
              "max" : 10,
              "group": "xform",
            } ],
        "r_y" : [
            "Rotate Y",
            "",
            "int",
            1,
            { "min" :  1,
              "max" : 10,
              "group": "xform",
            } ],
        "r_z" : [
            "Rotate Z",
            "",
            "int",
            1,
            { "min" :  1,
              "max" : 10,
              "group": "xform",
            } ],
        "s_x" : [
            "Scale X",
            "",
            "int",
            1,
            { "min" :    1,
              "max" : 1000,
              "group": "xform",
            } ],
        "s_y" : [
            "Scale Y",
            "",
            "int",
            2,
            { "min" :    1,
              "max" : 1000,
              "group": "xform",
            } ],
        "s_z" : [
            "Scale Z",
            "",
            "int",
            3,
            { "min" :    1,
              "max" : 1000,
              "group": "xform",
            } ],
    }
    prop_order = [ 't_x', 't_y', 't_z', 'r_x', 'r_y', 'r_z', 's_x', 's_y', 's_z' ]
    class Dum( object ): pass
    X = Dum()
    for attr in prop_order:
        setattr( X, attr, 1 )
    app = QtGui.QApplication( sys.argv )
    pp = PPane( app, X, props, prop_order, "Test" )
    pp.show()
    sys.exit( app.exec_() )