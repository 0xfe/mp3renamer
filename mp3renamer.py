#!/usr/bin/env python2.7
#
# mp3renamer - A tool for reorganizing audio file directories. Supports most
#              major audio file formats.
#
# Copyright (c) 2011 Mohit Muthanna Cheppudira <mohit@muthanna.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# -----------------------------------------------------------------------------
#
# Requires:
#   Python >= 2.7.
#   Library: mutagen >= 1.12
#
# With macports: sudo port install py27-mutagen
#
# Usage:
#   mp3renamer.py [-h] [--output_script FILE] [--rename_command CMD]
#                      [--mkdir_command CMD] [--nocolor] [--showmap] [--nostats]
#                      [--noscript] [--move]
#                      PATH
#
# positional arguments:
#   PATH                  Path to MP3 root directory.
#
# optional arguments:
#   -h, --help            show this help message and exit
#   --output_script FILE  Name of generated shell script
#   --rename_command CMD  Specify command to rename file (default is 'cp')
#   --mkdir_command CMD   Specify command to create directory (default is 'mkdir
#                         -p')
#   --nocolor             Disable ANSI terminal colors
#   --showmap             Show artist/album/track map
#   --nostats             Show statistics and failures
#   --noscript            Don't generate script (e.g. only see stats)
#   --move                Move files instead of copying them
#
# mp3renamer is a commandline tool that can reorganize your audio file
# collection and sort them by artist/album/title. It works particularly well
# for renaming files in an iTunes databases, (e.g., transferring files out of
# your iPod) where files names are obfuscated.
#
# The braindead way to use this:
#
# 1) Mount your iPod. Enable disk access.
#
# 2) Create a target directory to copy the reorganized music to.
#
#    $ mkdir MyMusic
#    $ cd MyMusic
#
# 3) Generate the copier script from your library.
#
#    $ mp3renamer.py /Volumes/iPod
#
#      Files read: 6223
#      Files successfully processed: 4528
#      Number of artists: 486
#      Number of albums: 803
#      Parse failures: 1294
#         /Volumes/iPod/Old/._F00
#         /Volumes/iPod/Old/._F01
#         /Volumes/iPod/Old/._F02
#         /Volumes/iPod/Old/._F03
#         /Volumes/iPod/Old/._F04
#         /Volumes/iPod/Old/._F05
#         /Volumes/iPod/Old/._F06
#         ...
#      Type determination failures: 401
#         /Volumes/iPod/Old/F00/._AOBU.mp3
#         /Volumes/iPod/Old/F00/._CEGD.mp3
#         /Volumes/iPod/Old/F00/._EAFM.mp3
#         /Volumes/iPod/Old/F00/._NNDJ.mp3
#         /Volumes/iPod/Old/F00/._PMEB.mp3
#         ...
#      Files with missing tags: 260
#         /Volumes/iPod/Old/F00/FRCK.mp3: album
#           Fuel/No Album/01 - Hemorrhage (In My Hands) (Acoustic)
#         /Volumes/iPod/Old/F00/LHMF.mp3: album
#           Gonzalo Rubalcaba/No Album/Agua de Beber
#         /Volumes/iPod/Old/F00/NYQL.mp3: album, title
#           Aebersold/No Album/112_NYQL.mp3
#         /Volumes/iPod/Old/F01/EULK.mp3: album
#           Red Hot Chilli Peppers/No Album/00 - Otherside
#         /Volumes/iPod/Old/F01/GSTH.mp3: title
#           Wes Montgomery/The Best of Wes/210_GSTH.mp3
#
#      Generating shell script: renamer.sh
#
#    This command will generate a a shell script which copies all the audio
#    files from /Volumes/iPod to a clean hierarchy in the current directory. You
#    are free to edit this script should you need to.
#
#    The generated script consists of lots of lines like below for each of your
#    tracks:
#
#      mkdir -p 'Sting/Nothing Like The Sun'
#      cp '/Volumes/iPod/F06/RSGM.mp3' 'Sting/Blah/4 - History Will Teach Us Nothing'
#      cp '/Volumes/iPod/F06/SUGG.mp3' 'Sting/Blah/9 - Rock Steady'
#
#    If you specify --move, files will be moved instead of copied. Alternatively,
#    you can use the --rename_command and mkdir_command flags to provide the exact
#    commands to execute. E.g.
#
#    $  mp3renamer.py ~/Music/Copy/ \
#         --rename_command 'echo cp' --mkdir_command 'echo mkdir'
#
# 4) Run the script in your target directory.
#
#    $ chmod +x renamer.sh
#    $ ./renamer.sh
#
# All done. Send your bugs, comments, or criticisms to mohit@muthanna.com.

import argparse
import codecs
import os
import re
import sys

from operator import itemgetter

from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.m4a import M4A
from mutagen import File

argparser = argparse.ArgumentParser(
    description="Reorganize audio directories by tag information.")
argparser.add_argument(
    "path", metavar="PATH", nargs=1,
    help="Path to MP3 root directory.")
argparser.add_argument(
    "--output_script", metavar="FILE", nargs=1,
    default="renamer.sh", help="Name of generated shell script")
argparser.add_argument(
    "--rename_command", metavar="CMD", nargs=1,
    default=["cp"], help="Specify command to rename file (default is 'cp')")
argparser.add_argument(
    "--mkdir_command", metavar="CMD", nargs=1,
    default=["mkdir -p"],
    help="Specify command to create directory (default is 'mkdir -p')")
argparser.add_argument(
    "--nocolor", action="store_const", const=True,
    default=False, help="Disable ANSI terminal colors")
argparser.add_argument(
    "--showmap", action="store_const", const=True,
    default=False, help="Show artist/album/track map")
argparser.add_argument(
    "--nostats", action="store_const", const=True,
    default=False, help="Show statistics and failures")
argparser.add_argument(
    "--noscript", action="store_const", const=True,
    default=False, help="Don't generate script (e.g. only see stats)")
argparser.add_argument(
    "--move", action="store_const", const=True,
    default=False, help="Move files instead of copying them")

class Colors:
  ESC = "\033["
  PURPLE = ESC + "95m"
  GREEN = ESC + "92m"
  YELLOW = ESC + "93m"
  RESET = ESC + "0m"

class NoColors:
  ESC = ""
  PURPLE = ""
  GREEN = ""
  YELLOW = ""
  RESET = ""

global color_map
color_map = Colors

def log(msg):
  print color_map.GREEN + msg + color_map.RESET

def log_clean(msg):
  print msg

def log_warn(msg):
  print >> sys.stderr, color_map.YELLOW + msg + color_map.RESET

class Stats:
  num_artists = 0
  num_albums = 0
  files_read = 0
  renamed_files = 0
  parse_failed = 0
  type_failed = 0
  missing_tags = 0

  """
  We maintain a map of artist -> album -> title
  """
  file_map = {}

  paths = {
      "parse_failed": [],
      "type_failed": [],
      "missing_tags": []
  }

  @classmethod
  def add_parse_failure(cls, filename):
    cls.paths['parse_failed'].append(filename)
    cls.parse_failed += 1

  @classmethod
  def add_type_failure(cls, filename):
    cls.paths['type_failed'].append(filename)
    cls.type_failed += 1

  @classmethod
  def add_missing_tag_failure(cls, filename, newname):
    cls.paths['missing_tags'].append([filename, newname])
    cls.missing_tags += 1

  @classmethod
  def add_track(cls, filename, newname, artist, album, tracknumber, title):
    files = cls.file_map

    if not files.get(artist):
      files[artist] = {}
      cls.num_artists += 1

    if not files[artist].get(album):
      files[artist][album] = []
      cls.num_albums += 1

    track_list = files[artist][album]
    track_list.append({
      'filename': filename,
      'newname': newname,
      'tracknumber': tracknumber,
      'title': title
    })

    cls.renamed_files += 1

  @classmethod
  def display_stats(cls):
    log("Files read: %d" % (cls.files_read))
    log("Files successfully processed: %d" % (cls.renamed_files))
    log("Number of artists: %d" % (cls.num_artists))
    log("Number of albums: %d" % (cls.num_albums))
    log("Parse failures: %d" % (cls.parse_failed))
    for f in cls.paths['parse_failed']:
      log_clean("   %s" % f)
    log("Type determination failures: %d" % (cls.type_failed))
    for f in cls.paths['type_failed']:
      log_clean("   %s" % f)
    log("Files with missing tags: %d" % (cls.missing_tags))
    for f in cls.paths['missing_tags']:
      log_clean("   %s" % f[0])
      log_clean("     %s" % f[1])

  @classmethod
  def display_map(cls):
    for artist in sorted(cls.file_map):
      for album in sorted(cls.file_map[artist]):
        log("[ " + artist + " - " + album + " ]")
        for track in sorted(cls.file_map[artist][album],
                            key=itemgetter("tracknumber")):
          tracknumber = track['tracknumber'] or "#"
          title = track['title']
          log_clean("%s - %s" % (tracknumber, title))
        print

def sanitize_path(path):
  a = re.sub(r'[/]', r'_', path)
  return re.sub(r"(['])", r"'\''", a)

def escape_path(path):
  return re.sub(r"(['])", r"'\''", path)

def process_files(path, stats):
  """
  Recurse down directory path and process each audio file.
  """
  counter = 0
  for root, dirs, files in os.walk(path):
    for f in files:
      # We maintain a counter to keep file names unique
      counter += 1
      stats.files_read += 1
      filename = os.path.join(root, f)

      try:
        audio = File(filename, easy=True)
      except Exception, e:
        stats.add_type_failure(filename)
        continue

      if not audio:
        stats.add_parse_failure(filename)
        continue

      test_tags = ['artist', 'album', 'title']
      missing_tags = []

      for tag in test_tags:
        if not audio.has_key(tag):
          missing_tags.append(tag)

      tracknumber = audio.get('tracknumber', [None])[0]
      artist = sanitize_path(audio.get('artist', ['No Artist'])[0])
      album = sanitize_path(audio.get('album', ['No Album'])[0])
      title = sanitize_path(audio.get('title', ["%d_%s" % (counter, f)])[0])

      if not tracknumber:
        newname = os.path.join(artist, album, title)
      else:
        tracknumber = re.sub(r'.*?(\d+).*', r'\1', tracknumber)
        newname = os.path.join(artist, album, "%s - %s" % (tracknumber, title))

      if len(missing_tags) > 0:
        pretty_missing_tags = str.join(", ", missing_tags)
        stats.add_missing_tag_failure(
            filename + ": " + pretty_missing_tags,
            newname)

      stats.add_track(filename, newname, artist, album, tracknumber, title)

def gen_script_unix(file_map, script_path):
  mkdir_cmd = args.mkdir_command[0]
  rename_cmd = args.rename_command[0]
  if args.move: rename_cmd = "mv"
  f = codecs.open(script_path, encoding="utf-8", mode="w")
  f.write("#!/bin/bash -x\n")
  f.write("#\n# Generated with mp3renamer (by 0xfe).\n#\n")
  f.write("# Files will be copied or moved to current directory\n\n")
  for artist in sorted(file_map):
    for album in sorted(file_map[artist]):
      f.write("%s '%s'\n" % (mkdir_cmd, os.path.join(artist, album)))
      for track in file_map[artist][album]:
        filename = escape_path(track['filename'])
        newname = track['newname']
        f.write("%s '%s' '%s'\n" % (rename_cmd, filename, newname))
      f.write("\n")
  f.close()

if __name__ == "__main__":
  args = argparser.parse_args()
  if args.nocolor:
    color_map = NoColors

  path = args.path[0]
  process_files(path, Stats)

  if args.showmap:
    Stats.display_map()
    print

  if not args.nostats:
    Stats.display_stats()
    print

  if not args.noscript:
    log("Generating shell script: " + args.output_script)
    gen_script_unix(Stats.file_map, args.output_script)
