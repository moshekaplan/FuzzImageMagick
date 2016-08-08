#!/usr/bin/env python

"""\
Script for submitting ImageMagick bugs

Attempts to convert a file with ImageMagick. If the file crashes ImageMagick,
the script creates a new Launchpad issue with the crash output and uploads
the crash file.

Copyright (c) 2016 Moshe Kaplan

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import sys
import subprocess
from launchpadlib.launchpad import Launchpad

cachedir = "/home/user/.launchpadlib/cache/"

# Some per-system values:
IMAGEMAGICK_DIR = "/home/user/Desktop/ImageMagick"
IMAGEMAGICK_BIN = "magick"

bug_description_header = "This bug was found while fuzzing ImageMagick with afl-fuzz\n\n"
bug_description_version = "Tested on ImageMagick git commit %s\n\n"
bug_description_command = "Command: magick %s /dev/null\n\n"


def get_git_commit():
    cmd = "cd %s && git rev-parse HEAD" % IMAGEMAGICK_DIR
    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return out


def test_file(filename):
    cmd = IMAGEMAGICK_BIN + ' "%s" /dev/null' % filename
    print "running: " + cmd
    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    print "program output:"
    print err
    return err


def submit_bug(filename, output):
    # These errors are boring
    if "ERROR: AddressSanitizer failed to allocate" in output:
        "overly-large call to malloc failed; skipped"
        return
    try:
        err_location_line = [line for line in output.split('\n') if 'ImageMagick' in line][0]
        err_location = err_location_line.split("ImageMagick/", 1)[1]

        err_info_line = [line for line in output.split('\n') if 'ERROR: AddressSanitizer:' in line][0]
        err_type = err_info_line.split("ERROR: AddressSanitizer: ", 1)[1].split(' ', 1)[0]
    except Exception, e:
        print "error processing output"
        print e
        return

    bug_filename = filename.rsplit('/', 1)[-1]

    if "WRITE of size" in output:
        err_type = "out-of-bounds write"
    if "READ of size" in output:
        err_type = "out-of-bounds read"

    bug_title = "%s in %s" % (err_type, err_location)

    git_commit = get_git_commit()
    if not git_commit:
        git_commit = "<unknown>"

    bug_description = bug_description_header + (bug_description_version % git_commit) + (bug_description_command % bug_filename) + output
    bug_comment = "input file to trigger crash"
    bug_filecontents = open(filename, 'rb').read()

    print bug_title

    submit = raw_input("Submit bug?\n")
    if submit.lower()[0] != "y":
        print "Skipped"
        return

    launchpad = Launchpad.login_with('ImageMagick_bug_submitter', 'production')
    imagemagick_distribution = launchpad.distributions['ubuntu/+source/imagemagick']

    bug = launchpad.bugs.createBug(description=bug_description,
                                   title=bug_title,
                                   security_related=True,
                                   target=imagemagick_distribution)

    bug.addAttachment(comment=bug_comment,
                      filename=bug_filename,
                      data=bug_filecontents)


def main():

    if len(sys.argv) < 2:
        print "USAGE: python %s filename" % (sys.argv[0])
        sys.exit(1)

    filename = sys.argv[1]

    output = test_file(filename)

    if output:
        submit_bug(filename, output)


if __name__ == '__main__':
    main()

