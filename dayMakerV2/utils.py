import os
import errno

def mkdirs( path ):
    if( not os.path.isfile( path ) ):
        mkdir_p( os.path.dirname( path ) )

def mkdir_p( path ):
    """https://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python"""
    try:
        os.makedirs( path )
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir( path ):
            pass
        else:
            raise