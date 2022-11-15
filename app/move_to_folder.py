import os
import glob
import shutil

docfiles=glob.glob("./**/*.py" , recursive=True)
if docfiles:
    docdir = os.path.join("./package")
    os.makedirs(docdir , exist_ok = True)
    for docfile in docfiles:
        if 'visison' in docfile:
            continue
        if docfile in docdir:
            pass
        else:
            shutil.move(os.path.join(docfile),docdir)
            print("Files Moved")

