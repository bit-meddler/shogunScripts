"""
Tool to work with Vicon created "enf" files, which are just inis really.

"""
import sys
import os
import datetime
import ConfigParser


def scanDB( path ):
    pass

def scanProjects( path ):
    pass
    
def scanDays( path ):
    pass
    
def getProjectSettings( path ):
    pass

def createProject( path, prj ):
    pass
    
def createDay( path, day ):
    pass
    
def createSession( path, ses ):
    pass
    
    
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
    args = parser.parse_args()
    if( args.scanDB ):
        if( args.path is None ):
            print( "scanDB requires the path paramiter" )
            exit()
        else:
            scanDB( args.path )
    elif( args.scanProjects ):
        if( args.path is None ):
            print( "scanProjects requires the path paramiter" )
            exit()
        else:
            scanProjects( args.path )
    elif( args.scanDays ):
        if( args.path is None ):
            print( "scanDays requires the path paramiter" )
            exit()
        else:
            scanDays( args.path )
    elif( args.getProjectSettings ):
        if( args.path is None ):
            print( "getProjectSettings requires the path paramiter" )
            exit()
        else:
            getProjectSettings( args.path )
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