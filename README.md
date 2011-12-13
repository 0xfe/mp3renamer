# mp3renamer - Organize your audio directories

## About

mp3renamer is a commandline tool that can reorganize your audio file
collection and sort them by artist/album/title. It supports most audio formats
(e.g., MP3, M4A, FLAC, etc.) and works particularly well
for renaming files in an iTunes databases, (e.g., transferring files out of
your iPod) where files names are obfuscated.

## License

Copyright (c) 2011 Mohit Muthanna Cheppudira <mohit@muthanna.com>

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

## Prerequisites

*  Python >= 2.7.
*  Library: mutagen >= 1.12

With macports: sudo port install py27-mutagen

## Quickstart

The commandline syntax for mp3renamer is:

    mp3renamer.py [-h] [--output_script FILE] [--rename_command CMD]
                  [--mkdir_command CMD] [--nocolor] [--showmap] [--nostats]
                  [--noscript] [--move]
                  PATH

    positional arguments:
      PATH                  Path to MP3 root directory.

    optional arguments:
      -h, --help            show this help message and exit
      --output_script FILE  Name of generated shell script
      --rename_command CMD  Specify command to rename file (default is 'cp')
      --mkdir_command CMD   Specify command to create directory (default is 'mkdir
                            -p')
      --nocolor             Disable ANSI terminal colors
      --showmap             Show artist/album/track map
      --nostats             Show statistics and failures
      --noscript            Don't generate script (e.g. only see stats)
      --move                Move files instead of copying them

The braindead way to use this:

### 1. Mount your iPod. Enable disk access.

### 2. Create a target directory to copy the reorganized music to.

```
    $ mkdir MyMusic
    $ cd MyMusic
```

### 3. Generate the copier script from your library.

```
    $ mp3renamer.py /Volumes/iPod

     Files read: 6223
     Files successfully processed: 4528
     Number of artists: 486
     Number of albums: 803
     Parse failures: 1294
        /Volumes/iPod/Old/._F00
        /Volumes/iPod/Old/._F01
        /Volumes/iPod/Old/._F02
        /Volumes/iPod/Old/._F03
        /Volumes/iPod/Old/._F04
        /Volumes/iPod/Old/._F05
        /Volumes/iPod/Old/._F06
        ...
     Type determination failures: 401
        /Volumes/iPod/Old/F00/._AOBU.mp3
        /Volumes/iPod/Old/F00/._CEGD.mp3
        /Volumes/iPod/Old/F00/._EAFM.mp3
        /Volumes/iPod/Old/F00/._NNDJ.mp3
        /Volumes/iPod/Old/F00/._PMEB.mp3
        ...
     Files with missing tags: 260
        /Volumes/iPod/Old/F00/FRCK.mp3: album
          Fuel/No Album/01 - Hemorrhage (In My Hands) (Acoustic)
        /Volumes/iPod/Old/F00/LHMF.mp3: album
          Gonzalo Rubalcaba/No Album/Agua de Beber
        /Volumes/iPod/Old/F00/NYQL.mp3: album, title
          Aebersold/No Album/112_NYQL.mp3
        /Volumes/iPod/Old/F01/EULK.mp3: album
          Red Hot Chilli Peppers/No Album/00 - Otherside
        /Volumes/iPod/Old/F01/GSTH.mp3: title
          Wes Montgomery/The Best of Wes/210_GSTH.mp3

     Generating shell script: renamer.sh
```

   This command will generate a a shell script which copies all the audio
   files from /Volumes/iPod to a clean hierarchy in the current directory. You
   are free to edit this script should you need to.

   The generated script consists of lots of lines like below for each of your
   tracks:

     mkdir -p 'Sting/Nothing Like The Sun'
     cp '/Volumes/iPod/F06/RSGM.mp3' 'Sting/Blah/4 - History Will Teach Us Nothing'
     cp '/Volumes/iPod/F06/SUGG.mp3' 'Sting/Blah/9 - Rock Steady'

   If you specify `--move`, files will be moved instead of copied. Alternatively,
   you can use the `--rename_command` and `--mkdir_command` flags to provide the exact
   commands to execute. E.g.

     $  mp3renamer.py ~/Music/Copy/ \
          --rename_command 'echo cp' --mkdir_command 'echo mkdir'

### 4. Run the script in your target directory.

```
     $ chmod +x renamer.sh
     $ ./renamer.sh
```

## More information

All done. Send your bugs, comments, or criticisms to mohit@muthanna.com.

[the blog][http://0xfe.blogspot.com]
