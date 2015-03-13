#!/usr/bin/env python
import cgi, os
import cgitb; cgitb.enable()
import hashlib
import datetime

#   Copyright (C) Stephen Reese http://www.rsreese.com
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.


try: # Windows needs stdio set for binary mode.
    import msvcrt
    import uuid
    msvcrt.setmode (0, os.O_BINARY) # stdin  = 0
    msvcrt.setmode (1, os.O_BINARY) # stdout = 1
except ImportError:
    pass

form = cgi.FieldStorage()

# Generator to buffer file chunks
def fbuffer(f, chunk_size=10000):
   while True:
      chunk = f.read(chunk_size)
      if not chunk: break
      yield chunk

# A nested FieldStorage instance holds the file
fileitem = form['file']

# Test if the file was uploaded
if fileitem.filename:

   # strip leading path from file name to avoid directory traversal attacks
   fn = os.path.basename(fileitem.filename)
  
   # Internet Explorer will attempt to provide full path for filename fix
   fn = fn.split('\\')[-1]
 
   # This path must be writable by the web server in order to upload the file.
   path = '/var/www/dropbox/'
   filepath = path + fn

   # Open the file for writing 
   f = open(filepath , 'wb', 10000)

   h = hashlib.sha256()
   datalength = 0

   # Read the file in chunks
   for chunk in fbuffer(fileitem.file):
      f.write(chunk)
      h.update(chunk)
      datalength += len(chunk)
   hexdigest = h.hexdigest()
   f.close()

   # Include date in filename, increment version and append hash value
   count = 0
   tmp_fn = filepath + "_" + datetime.datetime.now().strftime("%Y-%m-%d") + ".v" + str(count) + "_" + hexdigest
   while os.path.isfile(tmp_fn):
      count += 1
      tmp_fn = filepath + "_" + datetime.datetime.now().strftime("%Y-%m-%d") + ".v" + str(count) + "_" + hexdigest

   # Rename the file
   os.rename(filepath, tmp_fn)

   # Get the new filename for the users viewing pleasure
   displaypath, tmp_split = os.path.split(tmp_fn)

   message = 'The file "' + fn + '" was uploaded successfully with a SHA256 hash value of ' + hexdigest + '.<br> Copy this <a href="/dropbox/' + tmp_split + '">link</a> to share.<br> Click <a href="/dropbox/">here</a> to go back and upload another file.'

else:
   message = 'No file was uploaded'

print """\
Content-Type: text/html\n
<html><body>
<p>%s</p>
</body></html>
""" % (message,)
