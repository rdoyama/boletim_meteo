'''
This program is intended to automate the generation
of reports with statistics and graphs of some meteorological
data from various sources, such as INMET and CEMADEN.

Input data and the type of analysis should be passed
in the config.ini file. If it is non existent, run this code
and it will be generated with default arguments.
'''

import sys
sys.path.append('code/')

import datetime as dt

from utils import log, genCfgFile, cfgparser, writePDF, clean_tmp
from cemaden import run_cemaden
from inmet import run_inmet


def main():
	parser = cfgparser('config.ini')

	cemaden_sta_data, cemaden_plot_paths = None, None
	if parser.get('files', 'cemaden') != 'None':
		print('Cemaden...', end='')
		cemaden_sta_data, cemaden_plot_paths = run_cemaden(parser)
		print('OK')

	inmet_sta_data, inmet_plot_paths = None, None
	if parser.get('files', 'inmet') != 'None':
		print('Inmet...', end='')
		inmet_sta_data, inmet_plot_paths = run_inmet(parser)
		print('OK')

	print('Writing PDF...', end='')
	writePDF(parser, cemaden_sta_data, cemaden_plot_paths, inmet_sta_data,
				inmet_plot_paths)
	print('OK')

	print('Cleaning tmp...', end='')
	clean_tmp()
	print('OK\n')

if __name__ == '__main__':
	main()
