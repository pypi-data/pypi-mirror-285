# Description

This project provides several utility scripts to help with file management at
WMUL-FM.

## Annual Archiver

For yearly archiving. Deletes the junk files, renames equivalent files, copies everything to a separate directory, converts the wav files to mp3s, and does a final comparison to check for missing files.

## Bulk Copier

Script to copy the contents of one folder of into another. If the copy of a particular file fails for any reason, 
it continues with the remaining files (rather than quitting, like Windows). If a file already exists, compares the
creation and modification times. If the origin file is newer, overwrites the destination file.

## Convert Folder To MP3

Script to archive a directory or set of directories into mp3 format. This script is multi-threaded and uses at least
two threads. One thread issues file copy commands to the os, the other calls the mp3 converter. Any extra threads call
additional mp3 converters.

## Copy Yesterdays Skimmer Files

Script to copy yesterday's skimmer files. For each pair input, it looks for yesterday's date directory under the source directory. The date folder must be in YYYY-MM-DD format. E.G. If today is 2018-May-16 and the source folder is `D:\\Skimmer\\`, it will look for `D:\\Skimmer\\2018-05-15`.

It copies the files in the source date folder to the destination date folder. E.G. The destination is `U:\\Skimmer\\`, it will copy to `U:\\Skimmer\\2018-05-15\\`.

## Create News Folders

This script will create the news folders between two given dates and under the given folder.

E.G.
> Start Date - 2023-01-23   
> End Date - 2023-04-28  
> Folder - Z:/News/Packages, Sports & Weather/Spring 2023

It will create:  
> Z:/News/Packages, Sports & Weather/Spring 2023/01 - Monday/01-23  
> Z:/News/Packages, Sports & Weather/Spring 2023/02 - Tuesday/01-24  
> Z:/News/Packages, Sports & Weather/Spring 2023/03 - Wendesday/01-25  
> Z:/News/Packages, Sports & Weather/Spring 2023/04 - Thursday/01-26  
> Z:/News/Packages, Sports & Weather/Spring 2023/05 - Friday/01-27  
> ...  
>   
> Z:/News/Packages, Sports & Weather/Spring 2023/01 - Monday/04-24  
> Z:/News/Packages, Sports & Weather/Spring 2023/02 - Tuesday/04-25  
> Z:/News/Packages, Sports & Weather/Spring 2023/03 - Wendesday/04-26  
> Z:/News/Packages, Sports & Weather/Spring 2023/04 - Thursday/04-27  
> Z:/News/Packages, Sports & Weather/Spring 2023/05 - Friday/04-28  

## Delete Junk Files

Iterates the contents of the given folder and deletes all of the junk files in the directory.

Junk files are the ones with one of the provided extensions. Defaults are .pk files created by Adobe Audition,
.sfk, .tmp, and .sfap0 files created by Sound Forge.

Outputs, either to a file or to standard out, the deleted files' names and the total size of the deleted files.

## Delete Old Files

Script that deletes old files and folders off a given root folder.

## Did The Skimmer Copy the Files

Checks the provided folders and makes certain that yesterday's skimmer files were copied to that location.

## Equivalent File Finder

Iterates through a folder and its subfolders finding files in the same folder that differ only by their suffix.
This is to find cases where someone has created both a .wav and .mp3 version of the same file.
E.G. foo.wav and foo.mp3.

Optionally, the files can be renamed where the original suffix is added to the name.
E.G. blah.wav, blah.mp3 become blah_wav.wav and blah_mp3.mp3

This prepares folders for bulk mp3ing by ConvertFolderToMP3.py

## Find Old Directories

This script will search within a given path and find all the top level folders that only have files older than the
    cutoff date.

E.G.: If you pass it Z:, and Z: contains
    Z:
    | - Adam
    | - Betty
    | - Carl

It will search each folder for new files. If Adam contains any files that are newer than the cutoff, Adam will be
    marked as new. The directory structure below the top level does not matter. Top level folders are considered new if
    they contain a new file anywhere within them. Otherwise they are old.

## Folder Comparer

This script compares the contents of two folders. E.G. A Folder and its backup folder.

It does this in one of two ways.

1) By same relative path, then by modification time (mtime), then by size.

2) By same relative path, including equivalent suffixes.

Relative path example:

original/foo/bar.txt
backup/foo/bar.txt

Equivalent suffix example:

original/foo/bar.wav
backup/foo/bar.mp3

If prints four lists of files:
1) Any files or directories for which the system lacks read permission.
2) Any files in the first directory which would be duplicates with equivalent suffixes.
E.G. original/foo/bar.wav, original/foo/bar.mp3
3) Any files that are in the first directory but not the second.
4) Any files that are in the second directory but not the first.

When method 1 is used for comparison, then lists 3 and 4 would include files that are in both folders, but with
different mtimes and/or sizes.

## Is The Skimmer Working

Run once per hour. Checks the provided folders for files corresponding to the previous hour's skimmer recordings.
  Emails the provided addresses if there was a problem.
