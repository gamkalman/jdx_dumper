#!/usr/bin/python3
import os
import io
import re
import sys
import argparse
import logging
import jcamp
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pylab import *

# interactive off
# ---------------
ioff()

# constants
# ---------
DEBUG = os.environ.get('DEBUG', '0') != '0'
this_script = sys.argv[0]
usage_message = f'python3 {this_script} \
        -f <filename.jdx|str>  -d <input_dir|str> -o <outdir|str>'
VERSION = '1.0.0'
JDX_HEADER_DELIMITER = '##END='
MIN_SPECTRA_INV_CM = 756
MAX_SPECTRA_INV_CM = 1400

# set up logging
# --------------
logging.basicConfig(stream = sys.stderr,
  level = logging.DEBUG if DEBUG else logging.INFO,
  format  =
    '[%(asctime)s.%(msecs)03d %(levelname)s] %(filename)s:%(lineno)d:\n%(message)s'
      if DEBUG else '[%(asctime)s.%(msecs)03d %(levelname)s] %(message)s',
  datefmt = '%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

class jdx_file(object):

  def __init__(self, jdx_filename: str, outdir: str = '') -> None:
    '''Contructor method'''
    self.filename = jdx_filename
    self.outdir = outdir

  def __del__(self):
    '''Destructor method'''
    pass

  def spectra_contains_range_756_1400(self, x_values: np.ndarray) -> bool:
    '''
    Use spectra from .jdx/.JDX file to determine if this spectra contains
    the range 756-1400 cm-1. Returns true or false.
    '''
    min_x_value = x_values.min()
    max_x_value = x_values.max()

    if MIN_SPECTRA_INV_CM >= min_x_value and MAX_SPECTRA_INV_CM <= max_x_value:
      return True
    return False

  @staticmethod
  def parse_jdx_header_params(header_strings: list):
    '''
    Parse certain attributes from the jdx header lines.

    Args:
      header_strings (list): header strings.

    Returns:
      dict: Some parsed information from jdx header.
    '''
    chemical_outname = ''
    ylabel = ''

    for line in header_strings:
      if '##CAS NAME' in line or '##TITLE' in line:
        chemical_outname = line.strip().split('=')[-1].strip()
      if '##YLABEL' in line:
        ylabel = line.strip().split('=')[-1].strip()

    # format the chemical name
    # ------------------------
    return {
      'chemical_name': chemical_outname,
      'ylabel': ylabel
    }

  def plot_spectra_and_write_txt(self, header: list, spectrum_data_hash: dict) -> None:
    '''
    Create PNG plot of spectra. Takes in header string
    and dictionary cantaining spectrum data using jcamp.

    Args:
      header_str (list): header for spectra from .jdx/.JDX file.
      spectrum_data_hash (dict): data read via jcamp library.
    '''
    # get the chemical name e.g. ##CAS NAME or ##TITLE
    # ------------------------------------------------
    header_params = jdx_file.parse_jdx_header_params(header)

    chemical_name = header_params['chemical_name'] 
    chemical_name = re.sub(r'[-,%() ]', '_', chemical_name)

    # make sure we have string for the header
    # ---------------------------------------
    header_str = '\n'.join(header)

    x = spectrum_data_hash['x']
    y = spectrum_data_hash['y']
    ylabel = header_params['ylabel']
    ylabel = re.sub(r'[ -%(),]', '_', ylabel)

    # create out png filename to hold plot of spectra
    # -----------------------------------------------
    basename, extension = os.path.splitext(self.filename) 
    basename = os.path.basename(basename) 

    if len(ylabel) > 0:
      outname_png = '_'.join([basename, chemical_name, ylabel])
    else:
      outname_png = '_'.join([basename, chemical_name])
 
    outname_png = outname_png.rstrip('_-') + '.png'
    outname_png = os.path.join(self.outdir, outname_png)
    if os.path.isfile(outname_png):
      os.remove(outname_png)
    
    logger.info(f'creating following output PNG: {outname_png}')

    # create the actual plot & write to png
    # -------------------------------------
    plt.clf()
    plt.plot(x, y, linewidth = 0.6)
    plt.xlabel(spectrum_data_hash['xunits'].lower())
    plt.ylabel(spectrum_data_hash['yunits'].lower())
    plt.title(spectrum_data_hash['title'])
    plt.grid(linewidth = 0.2)
    plt.savefig(outname_png, dpi = 250, bbox_inches = 'tight')
    plt.close()

    # write header-lines to txt file
    # ------------------------------
    header_txt_filename = outname_png.replace('.png', '-metadata.txt')
    if os.path.isfile(header_txt_filename):
      os.remove(header_txt_filename)

    with open(header_txt_filename, 'w') as f:
      for line in header:
        f.write('%s\n' % line.strip())

    # write the spectral data to text-file
    # ------------------------------------
    spectral_data_filename = outname_png.replace('.png', '-ir_spectra.txt')
    if os.path.isfile(spectral_data_filename):
      os.remove(spectral_data_filename)

    xy = np.column_stack((x, y))
    np.savetxt(spectral_data_filename, xy, delimiter = ',')

  def get_jdx_headers_and_datalines(self) -> dict:
    '''
    Instance method to get the header(s) from a .JDX/.jdx file, as well
    as corresponding data (spectra) for each header.

    Returns:
      tuple: (Nested list[] of lists of strings for header(s) in a .JDX/.jdx file., 
        List of corresponding lines with spectra (numeric) data (list of lists)
    '''
    # list to hold one or more headers from jdx file
    # (one header for each spectra)
    # ----------------------------------------------
    jdx_headers, jdx_data_blocks = [], []
  
    # first read entire contents of the .jdx/.JDX file
    # ------------------------------------------------
    with open(self.filename, 'r', encoding = 'utf-8', errors = 'ignore') as f:
      jdx_content = f.read()

    # split into separate chunks (one chunk for each header)
    # ------------------------------------------------------
    header_sections = jdx_content.split(JDX_HEADER_DELIMITER)

    for header_section in header_sections:

      # remove trailing/starting empty spaces
      # -------------------------------------
      header_section = header_section.strip()

      # skip empty headers
      # ------------------
      if len(header_section) < 1:
        continue

      # now iterate through lines in header
      # -----------------------------------
      header_lines, data_lines = [], []
  
      for line in header_section.split('\n'):
        
        line = line.strip()
        line_pieces = list(filter(None, line.split(' ')))

        if jdx_file.is_numeric_list(line_pieces):
          data_lines.append(line)
        else:
          header_lines.append(line)

      data_lines.append(JDX_HEADER_DELIMITER)
      jdx_headers.append(header_lines)
      jdx_data_blocks.append(data_lines)

    # return nested list[] of one or more headers
    # -------------------------------------------
    return (jdx_headers, jdx_data_blocks)

  def get_headers(self):
    '''
    Instance method to get the header(s) from the .jdx/.JDX file. Returns them
    in a list of lists (where each sublist is a list[] corresponding to one header.

    Returns:
      list: List of lists (where each sub-list is a header (list of lines).
    '''
    return self.get_jdx_headers_and_datalines()[0]

  def get_datalines(self):
    '''
    Instance method to get all the lines containing spectral data from the
    .jdx/.JDX file. Returns list[] of lists, whereas each sub-list
    is a set of lines for each spectra block in the file (more than one
    is possible).

    Returns:
      list: List of lists (where each sub-list is a set of 
        lines for a spectra block).
    '''
    return self.get_jdx_headers_and_datalines()[1]

  def get_jcamp_obj(self, header: list, datalines: list) -> dict: 
    '''
    Return a jcamp reader object outputted from jcamp.read(), which returns
    a dictionary.

    Args:
      header (list): header lines
      datalines (list): list of lines for spectral data for the header

    Returns:
      dict: output from jcamp.read()
    '''
    jdx_str = '\n'.join(header + datalines)
    jdx_file_obj = io.StringIO(jdx_str.strip())
    spectrum_data_hash = jcamp.read(jdx_file_obj)
    return spectrum_data_hash

  def plot_all_spectra_to_png(self) -> tuple:
    '''
    Return a tuple() with 2 NumPy arrays: x and y
    for the spectra found in the .JDX/.jdx file.

    Returns: 
      tuple: tuple of 2 NumPy arrays (x & y) for spectra.
    '''
    (headers, spectras) = self.get_headers(), self.get_datalines() 

    for header, spectra in zip(headers, spectras):
      spectrum_data_hash = self.get_jcamp_obj(header, spectra) 
      self.plot_spectra_and_write_txt(header, spectrum_data_hash)

  @staticmethod
  def is_numeric_list(lst: list) -> bool:
    '''
    Determine if a list contains only numbers.
  
    Args:
      lst (list): list of strings

    Returns:
      bool: True or False if a list contains only numbers.
    '''
    for item in lst:
      try:
        float(item)
      except:
        return False
    return True

def show_version() -> None:
  '''
  Show version.
  '''
  print(f'Version: {VERSION}')
  sys.exit(0)

def show_usage(error_message: str = '') -> None:
  '''
  Show help message.

  Args:
    error_message (str): error message.

  Returns:
    None.
  '''
  print(error_message)
  print(usage_message)
  sys.exit()

def main():
 
  # set up command-line arguments
  # -----------------------------
  parser = argparse.ArgumentParser(description = 'jdx conversion/dumper tool.')

  parser.add_argument('-f','--filename', required = False, 
          dest = 'filename', help = 'jdx filename')
  parser.add_argument('-d', '--directory', required = False, 
          dest = 'directory', help = 'input directory')
  parser.add_argument('-o', '--outdir', required = False, 
          dest = 'outdir', help = 'output directory')
  parser.add_argument('-v', '--version', required = False, 
          dest = 'version', action = 'store_true', help = 'show version.')
  parser.add_argument('-u', '--usage', required = False, 
          dest = 'usage', action = 'store_true', help = 'show usage message.')

  # gather actual command-line arguments
  # ------------------------------------
  args = parser.parse_args()
  
  jdx_filename = args.filename
  input_directory = args.directory
  outdir = args.outdir

  # show version or this script, or usage message, if requested
  # -----------------------------------------------------------
  version = args.version
  usage = args.usage

  if version:
    show_version()
  elif usage:
    show_usage('')

  # check the output directory, if passed in. If not, use CWD
  # ---------------------------------------------------------
  if outdir and not os.path.isdir(str(outdir)):
    show_usage(f'ERROR (fatal): not an existing directory: {outdir}. Exiting ...')
  
  if not outdir:
    outdir = os.getcwd()
    logger.info(f'Note: no output directory passed in via -o/--outdir flag. \
            Using current working directory ...')

  # user should pass in either a .jdx filename OR a directory
  # path with .jdx files
  # ---------------------------------------------------------
  if not jdx_filename and not input_directory:
    show_usage('ERROR (usage): Pass in .jdx filename OR \
            an input directory path with .jdx files.')
  elif jdx_filename and input_directory:
    show_usage('ERROR (usage): Pass in .jdx filename OR \
            an input directory path with .jdx files.')

  # get list of files in input-dir if directory
  # passed-in
  # -------------------------------------------
  if jdx_filename:
    # make sure file actually exists
    # and has valid .jdx/.JDX extension
    # ---------------------------------
    if not os.path.isfile(jdx_filename):
      show_usage(f'ERROR (fatal): file does not exist: {jdx_filename}')
    elif not jdx_filename.lower().endswith('.jdx'):
      show_usage(f'ERROR (fatal): not a valid .jdx/.JDX filename: {jdx_filename}')
    
    # put into 1-element list[]
    # -------------------------
    jdx_filenames = [jdx_filename]
  else:
    # search input directory recursively for .jdx filenames
    # -----------------------------------------------------
    jdx_filenames = [] 

    for root, dirs, files in os.walk(input_directory):
      path = root.split(os.sep)
      for f in files:
        if f.lower().endswith('.jdx'): 
          jdx_filenames.append(os.path.join(root, f))

    # make sure directory had at least one .jdx/.JDX file
    # ---------------------------------------------------
    if len(jdx_filenames) < 1:
      show_usage('ERROR: no .jdx/.JDX files found in: {input_directory}')

  # now that we havef list filenames, we can begin
  # to parse the files
  # ----------------------------------------------
  for jdx_filename in jdx_filenames:
  
    #if not os.path.basename(jdx_filename) == '693-07-2-IR.jdx': 
    #  continue
    #logger.info(f'processing following JDX filename: {jdx_filename}')

    # create object to read jdx file
    # ------------------------------
    jdx_file_reader = jdx_file(jdx_filename, outdir)

    # get the header(s) from .jdx file
    # --------------------------------
    (jdx_headers, jdx_data_blocks) = \
            jdx_file_reader.get_jdx_headers_and_datalines()
    logger.info(f'    number of headers (spectra) found in {jdx_filename} => {len(jdx_headers)}')

    # read the spectra from the .JDX/.jdx file
    # ----------------------------------------
    jdx_file_reader.plot_all_spectra_to_png()
 
  # return status to console
  # ------------------------
  return 0

if __name__ == '__main__':
  main()
