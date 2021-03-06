"""
Tool to work with Vicon created "enf" files, which are just inis really.

"""
import sys
import os
import datetime
import ConfigParser
import re
from glob import glob

import utils

_MATCH_LAST_DIGITS = re.compile( '.*?([0-9]+)$', re.I )
DEFAULT_GLOBALS_DIR = "000000_globals"

            
def _absENFscan( path, error, search=None ):
    if not os.path.isdir( path ):
        print( error )
        #exit()
    # List dirs with an enf in them
    if( search is None ):
        search = os.path.join( path, "*", "*.enf" )
    dirs = glob( search )
    return map( lambda x: os.path.basename( os.path.dirname( x ) ), dirs )
    
def scanDB( path ):
    error = "PATH needs to be to an existing directory, leading to the root of the Vicon datastructure."
    return _absENFscan( path, error )

def scanProjects( path ):
    error = "PATH needs to be to an existing directory, leading to a Vicon 'Database'."
    search = os.path.join( path, "*", "*Project*.enf" )
    return _absENFscan( path, error, search )
    
def scanDays( path ):
    error = "PATH needs to be to an existing directory, Leading to a Vicon 'Project'."
    search = os.path.join( path, "*", "*Capture Day*.enf" )
    return _absENFscan( path, error, search )
    
def matchDays( path, descriptor ):
    error = "PATH needs to be to an existing directory, Leading to a Vicon 'Project'.\n" + \
            "TEXT is a descriptor to match in existing days"
    search = os.path.join( path, "*", "*" + descriptor + "*Capture Day*.enf" )
    return _absENFscan( path, error, search )
    
def biggestSuffix( path, descriptor ):
    candidates = matchDays( path, descriptor )
    if( len( candidates ) < 1 ):
        return 0
    serials = [ -1 for _ in candidates ]
    for i in range( len( serials ) ):
        res = _MATCH_LAST_DIGITS.search( candidates[i] )
        if res:
            serials[i] = int( res.group(1) )
    return max( serials ) 

def getProjectSettings( path ):
    error = "PATH needs to be to an existing directory, Leading to a Vicon 'Project'."
    search = os.path.join( path, "000000*", "" )
    res = _absENFscan( path, error, search )
    if( len( res ) != 1 ):
        print( "Error! no globals found")
        global_folder = DEFAULT_GLOBALS_DIR
    else:
        global_folder = res[0]
    return os.path.join( path, global_folder )

def _makeENF( type, name, root_path ):
    ses_info = False
    reference = ""
    parent = ""
    has_child = ""
    tag = ""

    if( type == "PROJECT" ): 
        reference = ""
        parent = ""
        has_child = "FALSE"
        ses_info = True
        tag = "Project 1"
    elif( type == "CAPTURE_DAY" ): 	
        reference = ""
        parent = "Project 1"
        has_child = "FALSE"
        ses_info = False
        tag = "Capture day 1"
    elif( type == "SESSION" ): 
        reference = ""
        parent = "Capture day 1"
        has_child = "FALSE"
        ses_info = True
        tag = "Session 1"

    if( ses_info ):
        creation_datetime = datetime.datetime.now().strftime( "%Y,%m,%d,%H,%M,%S" )

    # mkdir
    folder = os.path.join( root_path, name )
    os.mkdir( folder )
    
    # assemble ini file
    config = ConfigParser.RawConfigParser()
    # node info
    section = "Node Information"
    config.add_section( section )
    config.set( section, "TYPE", type )
    config.set( section, "REFERENCE", reference )
    config.set( section, "PARENT", parent )
    config.set( section, "NAME", name )
    config.set( section, "HASCHILD", has_child )
    # session Info when needed
    if( ses_info ):
        section = "SESSION_INFO"
        config.add_section( section )
        config.set( section, "CREATIONDATEANDTIME", creation_datetime )
        
    # Output
    enfPath = os.path.join( folder, (name + "." + tag + ".enf") )
    fh = open( enfPath, "w" )
    config.write( fh )
    fh.close()

def createProject( path, prj ):
    _makeENF( "PROJECT", prj, path )
    # make globals
    utils.mkdirs( os.path.join( path, DEFAULT_GLOBALS_DIR ) )
    
def createDay( path, day ):
    _makeENF( "CAPTURE_DAY", day, path )
    
def createSession( path, ses ):
    _makeENF( "SESSION", ses, path )
    # update project enf with childs += 1 ?
    
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    actions = parser.add_mutually_exclusive_group( required=True )
    actions.add_argument( "--scanDB",
                          action="store_true",
                          help="PATH to Vicon 'Root' to scan for 'Databases'"
    )
    actions.add_argument( "--scanProjects",
                          action="store_true",
                          help="PATH to Vicon 'Database' to scan for 'Projects'"
    )
    actions.add_argument( "--scanDays",
                          action="store_true",
                          help="PATH to Vicon 'Project' to scan for 'Days'"
    )
    actions.add_argument( "--matchDays",
                          action="store_true",
                          help="PATH to Vicon 'Project' to match TEXT in"
    )
    actions.add_argument( "--biggestSuffix",
                          action="store_true",
                          help="PATH to Vicon 'Project' to match TEXT in and find biggest suffix"
    )
    actions.add_argument( "--getProjectSettings",
                          action="store_true",
                          help="PATH to Vicon 'Project' to load settings for"
    )
    actions.add_argument( "--createProject",
                          action="store_true",
                          help="PATH to Vicon 'Database' to create 'PROJECT' in"
    )
    actions.add_argument( "--createDay",
                          action="store_true",
                          help="PATH to Vicon 'Project' to create 'DAY' in"
    )
    actions.add_argument( "--createSession",
                          action="store_true",
                          help="PATH to Vicon 'Day' to create 'SESSION' in"
    )
    parser.add_argument( "-p", "--path", help="PATH to Node being acted on" )
    parser.add_argument( "-j", "--project", help="Project to be acted on" )
    parser.add_argument( "-d", "--day", help="DAY to be acted on" )
    parser.add_argument( "-s", "--session", help="SESSION to be acted on" )
    parser.add_argument( "-t", "--text", help="TEXT to match existing scaning Project" )
    args = parser.parse_args()
    if( args.scanDB ):
        if( args.path is None ):
            print( "scanDB requires the path paramiter" )
            exit()
        else:
            print( scanDB( args.path ) )
    elif( args.scanProjects ):
        if( args.path is None ):
            print( "scanProjects requires the path paramiter" )
            exit()
        else:
            print scanProjects( args.path )
    elif( args.scanDays ):
        if( args.path is None ):
            print( "scanDays requires the path paramiter" )
            exit()
        else:
            print scanDays( args.path )
    elif( args.getProjectSettings ):
        if( args.path is None ):
            print( "getProjectSettings requires the path paramiter" )
            exit()
        else:
            print getProjectSettings( args.path )
    elif( args.matchDays ):
        if( args.path is None ):
            print( "matchDays requires the path paramiter" )
            exit()
        if( args.text is None ):
            print( "matchDays requires the text paramiter" )
            exit()
        else:
            print matchDays( args.path, args.text )
    elif( args.biggestSuffix ):
        if( args.path is None ):
            print( "biggestSuffix requires the path paramiter" )
            exit()
        if( args.text is None ):
            print( "biggestSuffix requires the text paramiter" )
            exit()
        else:
            print biggestSuffix( args.path, args.text )
    elif( args.createProject ):
        if( args.path is None ):
            print( "createProject requires the path paramiter" )
            exit()
        if( args.project is None ):
            print( "createProject requires the project paramiter" )
            exit()
        else:
            createProject( args.path, args.project )
    elif( args.createDay ):
        if( args.path is None ):
            print( "createDay requires the path paramiter" )
            exit()
        if( args.day is None ):
            print( "createDay requires the day paramiter" )
            exit()
        else:
            createDay( args.path, args.day )
    elif( args.createSession ):
        if( args.path is None ):
            print( "createSession requires the path paramiter" )
            exit()
        if( args.session is None ):
            print( "createSession requires the session paramiter" )
            exit()
        else:
            createSession( args.path, args.session )
    else:
        print( "pleaase choose and action" )