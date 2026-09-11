###### JDX Spectroscopy File Dumper 
    
    This is a simple Python script that dumps the contents of one or more
    .jdx/.JDX spectroscopy file(s) to a set of 3 files: (1) a text file with header data
    (2) converted spectroscopy data (3) a PNG plot of the spectrum.  

###### GENERAL USAGE

    To use, pass in either a .jdx filename with -f (-filename) flag OR
    a directory with multiple .jdx/.JDX files (-d, --directory).

    Optional argument include -o (output directory), get the help message (-h),
    get the version (-v, --version), or -u (--usage, -u).

    usage: jdx_dump.py [-h] [-f FILENAME] [-d DIRECTORY] [-o OUTDIR] [-v] [-u]

    jdx conversion/dumper tool.

    optional arguments:
    -h, --help            show this help message and exit
    -f FILENAME, --filename FILENAME
                        jdx filename
    -d DIRECTORY, --directory DIRECTORY
                        input directory
    -o OUTDIR, --outdir OUTDIR
                        output directory
    -v, --version         show version.
    -u, --usage           show usage message.


###### USAGE/HOW TO RUN (Windows)
 
    It is expected that you will have a Python3 installation (with both python3 and pip3 command-line tools)
    on your system. On Windows, please go to:
    https://www.python.org/downloads/

    And click the "Download Python install manager" button.

    This will download the python-manager-XX.X file onto your system. Find this downloaded file, and double-click
    it to run and install python3 and pip3, as command-line tools, into your local Windows PC. It may open command-line
    terminals as needed during the install. Type "y" and hit enter, as necessary (for yes) for all necessary installs. Run as
    administrator if needed. 
    
    Once complete, search "CMD" in your PC to open the command prompt for your Windows installation. Install the
    necessary packages:
    > pip3 install numpy
    > pip3 install matplotlib
    > pip3 install pathlib
    > pip3 install jcamp
    
    Next, download this code from GitHub as a zip-file. Upzip, and navigate to your unzipped folder e.g.

    > cd C:\Users\dessb\Desktop\jdx_dumper
    C:\Users\dessb\Desktop\jdx_dumper> 

    Now you can run the code e.g.
    > python3 jdx_dump.py --version
    Version: 1.0.0    
 
    Run with an input directory (sample files provided in inputs/ directory in repo.), and be default,
    output files will be sent to current working directory (as no output directory specified with -o flag).
    
    > python3 jdx_dump.py -d inputs/ 
 
    Run with single file, and send outputs to a particular directory:

    Set the output directory to the current working directory, under a sub-folder 'outputs':
    > set "DIR=%CD%"\outputs
    > mkdir outputs
    > python3 jdx_dump.py -f inputs/693-07-2-IR.jdx -o %DIR%\outputs

###### Sample Images
 
    (1) IR Spectra Propene: 

![image info](sample_images/115-07-1-IR_Propene.png)

    (2) Acetic Acid / Butyl Ester 

![image info](sample_images/123-86-4-IR_ACETIC_ACID__n_BUTYL_ESTER.png)

###### VERSION
    
    Version 1.0.0
    Last Updated: 11 September 2026

###### 3rd party Python libraries used

    The required 3rd-party Python libraries are required:

    numpy - for array manipulation and matrix computations 
    matplotlib - for creating contour objects to be used in creating KMLs with isolines
    jcamp - to read .jdx/.JDX spectroscopy file
    Pathlib - for writing output file(s)

###### PYTHON VERSION:
     
    Supports Python 3.8.10+
