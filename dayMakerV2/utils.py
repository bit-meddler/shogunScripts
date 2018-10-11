import os

def mkdirs( path ):
    if( not os.path.isfile( path ) ):
        os.mkdir( os.path.dirname( path ) )