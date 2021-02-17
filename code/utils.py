from configparser import ConfigParser
import sys, os
import glob
from fpdf import FPDF
import datetime as dt
import pandas as pd

'''
Dimensões da folha A4 em mm: 210 x 297
'''


def log(message, level = 2, verbose=True):
	levels = ['Message:', 'Warning:', 'Error:']
	if not hasattr(log, 'lastlevel'):
		log.lastlevel = None
	
	if level == 0 and verbose is False: return
	if log.lastlevel != level:
		print('')
		print('{}'.format(levels[level]))
		log.lastlevel = level
	
	print('  {}'.format(message))
	if level == 2: sys.exit(1)


def genCfgFile(INIFIle):
	'''Writes a default configuration file'''
	config = ConfigParser()
	config['files'] = {'inmet': '<path_to>/inmet.csv',
					   'cemaden': '<path_to>/cemaden.csv'}
	config['time'] = {'start': 'YYYY-mm-dd HH',
					  'end': 'YYYY-mm-dd HH'}
	config['cemaden'] = {'write_sample': 'True',
						 'write_stats': 'True',
						 'plots' : 'True'}
	config['inmet'] = {'write_sample': 'True',
					   'write_stats': 'True',
					   'plots' : 'True'}
	with open('config.ini', 'w') as f:
		config.write(f)


def cfgparser(INIfile):
	'''Tries to read the config file. If there isn't one,
	it is created with default values.'''
	parser = ConfigParser(allow_no_value = True)
	try:
		with open(INIfile, 'r') as f:
			parser.read_file(f)
	except IOError:
		log(f'No such file or directory: {INIfile}', 1)
		genCfgFile(INIfile)
		log('Default configuration file created.'+
				' Check values to proceed', 1)
		sys.exit(0)

	return parser


def cemaden_station_table(pdf, cemaden_sta, start, end):
	pdf.set_font('Arial', 'B', 16)
	pdf.set_xy(0, 3)
	pdf.cell(210, 10, "Dados de estações pluviométricas do CEMADEN", 0, 2, 'C')
	pdf.cell(210, 10, f"Período: {start} até {end} UTC", 0, 2, 'C')
	pdf.cell(10, 10, '', 0, 2, 'C')
	pdf.set_font('Arial', 'B', 10)
	pdf.cell(210, 10, 'Estações utilizadas', 0, 2, 'C')
	pdf.cell(20)
	pdf.cell(75, 6, 'Estação', 1, 0, 'C')
	pdf.cell(45, 6, 'Local', 1, 0, 'C')
	pdf.cell(50, 6, 'Lat/Lon', 1, 2, 'C')
	pdf.set_font('Arial', '', 10)
	pdf.cell(-120)
	for sta, info in cemaden_sta.items():
		pdf.cell(75, 6, sta, 1, 0, 'C')
		pdf.cell(45, 6, '-'.join([info['municipio'], info['uf']]), 1, 0, 'C')
		pdf.cell(50, 6, '/'.join(map(str, [round(info['latitude'], 6), round(info['longitude'], 6)])), 1, 2, 'C')
		pdf.cell(-120)
	pdf.set_x(0)


def cemaden_stats_table(pdf, cemaden_sta):
	pdf.cell(10, 10, '', 0, 2, 'C')
	pdf.set_font('Arial', 'B', 10)
	pdf.cell(210, 10, 'Chuva acumulada por estação', 0, 2, 'C')
	pdf.cell(42)
	pdf.cell(75, 6, 'Estação', 1, 0, 'C')
	pdf.cell(51, 6, 'Chuva acumulada (mm)', 1, 2, 'C')
	pdf.cell(-75)
	pdf.set_font('Arial', '', 10)
	for sta, info in cemaden_sta.items():
		pdf.cell(75, 6, sta, 1, 0, 'C')
		pdf.cell(51, 6, str(round(info['precipitation'], 1)), 1, 2, 'C')
		pdf.cell(-75)
	pdf.set_font('Arial', 'B', 10)
	pdf.cell(75, 6, 'Média', 1, 0, 'C')
	media = sum(i['precipitation'] for i in cemaden_sta.values())
	media /= len(cemaden_sta.keys())
	pdf.cell(51, 6, str(round(media, 1)), 1, 2, 'C')
	pdf.set_x(0)


def cemaden_pdf_sample(pdf):
	try:
		data = pd.read_csv('./tmp/sample_cemaden.csv', index_col=False)
	except:
		log(f'Error when trying to open {"./tmp/sample_cemaden.csv"}', 2)
	keys = ['municipio','codEstacao','uf','nomeEstacao','latitude','longitude','datahora','valorMedida']
	pdf.cell(10, 10, '', 0, 2, 'C')
	pdf.set_font('Arial', 'B', 10)
	pdf.cell(210, 10, 'Amostra não processada dos dados do CEMADEN', 0, 2, 'C')
	pdf.cell(10)
	pdf.cell(20, 6, 'municipio', 1, 0, 'C')
	pdf.cell(25, 6, 'codEstacao', 1, 0, 'C')
	pdf.cell(15, 6, 'uf', 1, 0, 'C')
	pdf.cell(35, 6, 'nomeEstacao', 1, 0, 'C')
	pdf.cell(20, 6, 'latitude', 1, 0, 'C')
	pdf.cell(20, 6, 'longitude', 1, 0, 'C')
	pdf.cell(30, 6, 'datahora', 1, 0, 'C')
	pdf.cell(25, 6, 'valorMedida', 1, 2, 'C')
	pdf.set_x(10)
	pdf.set_font('Arial', '', 8)
	for i in range(len(data)):
		pdf.cell(20, 6, data.loc[i, 'municipio'], 1, 0, 'C')
		pdf.cell(25, 6, data.loc[i, 'codEstacao'], 1, 0, 'C')
		pdf.cell(15, 6, data.loc[i, 'uf'], 1, 0, 'C')
		pdf.cell(35, 6, data.loc[i, 'nomeEstacao'], 1, 0, 'C')
		pdf.cell(20, 6, str(round(data.loc[i, 'latitude'], 6)), 1, 0, 'C')
		pdf.cell(20, 6, str(round(data.loc[i, 'longitude'], 6)), 1, 0, 'C')
		pdf.cell(30, 6, data.loc[i, 'datahora'], 1, 0, 'C')
		pdf.cell(25, 6, str(data.loc[i, 'valorMedida']), 1, 2, 'C')
		pdf.set_x(10)
	pdf.set_x(0)


def plot_cemaden(pdf, paths):
	if len(paths) == 0:
		return
	pdf.add_page()
	pdf.set_xy(0, 3)
	pdf.set_font('Arial', 'B', 12)
	pdf.cell(210, 10, "Chuva (mm) acumulada por hora por estação", 0, 2, 'C')
	pdf.cell(10, 10, '', 0, 2, 'C')
	for path in paths:
		pdf.cell(30)
		pdf.image(path, w=150)
		pdf.set_x(0)


def inmet_station_table(pdf, si, inmet_stats, start, end):
	pdf.add_page()
	pdf.set_font('Arial', 'B', 16)
	pdf.set_xy(0, 3)
	pdf.cell(210, 10, "Dados da estação do INMET", 0, 2, 'C')
	pdf.cell(210, 10, f"Período: {start} até {end} UTC", 0, 2, 'C')
	pdf.cell(10, 10, '', 0, 2, 'C')
	pdf.set_font('Arial', 'B', 10)
	pdf.cell(210, 10, "Dados da estação e das medidas de vento coletadas", 0, 2, 'C')
	pdf.cell(15)
	pdf.cell(30, 6, 'Estação', 1, 0, 'C')
	pdf.cell(35, 6, 'Lat/Lon', 1, 0, 'C')
	pdf.cell(30, 6, 'Altitude (m)', 1, 0, 'C')
	pdf.cell(40, 6, 'Rajada máxima (m/s)', 1, 0, 'C')
	pdf.cell(45, 6, 'Velocidade média (m/s)', 1, 2, 'C')
	pdf.set_x(15)
	pdf.set_font('Arial', '', 8)
	pdf.cell(30, 6, f'{si["codigo"]}, {si["estacao"]}-{si["uf"]}', 1, 0, 'C')
	pdf.cell(35, 6, f'{si["latitude"]}/{si["longitude"]}', 1, 0, 'C')
	pdf.cell(30, 6, f'{si["altitude"]}', 1, 0, 'C')
	pdf.cell(40, 6, f'{si["rajmax"]}', 1, 0, 'C')
	pdf.cell(45, 6, f'{round(si["wind_avg"], 2)}', 1, 2, 'C')
	pdf.set_x(0)


def inmet_pdf_sample(pdf):
	try:
		data = pd.read_csv('./tmp/sample_inmet.csv', index_col=False)
	except:
		log(f'Error when trying to open {"./tmp/sample_inmet.csv"}', 2)
	keys = ['data','hora','vento_dir','vento_rajmax','vento_vel']
	pdf.cell(10, 10, '', 0, 2, 'C')
	pdf.set_font('Arial', 'B', 10)
	pdf.cell(210, 5, 'Amostra não processada dos dados do INMET', 0, 2, 'C')
	pdf.cell(210, 5, 'Apenas os dados de vento foram selecionados', 0, 2, 'C')
	pdf.cell(5)
	pdf.cell(30, 6, 'Data', 1, 0, 'C')
	pdf.cell(40, 6, 'Hora (HHMM, UTC)', 1, 0, 'C')
	pdf.cell(40, 6, 'Direção média (º)', 1, 0, 'C')
	pdf.cell(45, 6, 'Rajada máxima (m/s)', 1, 0, 'C')
	pdf.cell(45, 6, 'Velocidade média (m/s)', 1, 2, 'C')
	pdf.set_x(5)
	pdf.set_font('Arial', '', 8)
	for i in range(len(data)):
		pdf.cell(30, 6, data.loc[i, 'data'], 1, 0, 'C')
		pdf.cell(40, 6, data.loc[i, 'hora'], 1, 0, 'C')
		pdf.cell(40, 6, str(data.loc[i, 'vento_dir']), 1, 0, 'C')
		pdf.cell(45, 6, str(data.loc[i, 'vento_rajmax']), 1, 0, 'C')
		pdf.cell(45, 6, str(data.loc[i, 'vento_vel']), 1, 2, 'C')
		pdf.set_x(5)
	pdf.set_x(0)


def plot_inmet(pdf, paths):
	if len(paths) == 0:
		return
	pdf.add_page()
	pdf.set_xy(0, 3)
	pdf.set_font('Arial', 'B', 12)
	pdf.cell(210, 10, "Rosa dos ventos", 0, 2, 'C')
	pdf.cell(10, 10, '', 0, 2, 'C')
	for path in paths:
		pdf.cell(20)
		pdf.image(path, w=170)
		pdf.set_x(0)


def writePDF(parser, cemaden_sta, cemaden_plots, inmet_sta, inmet_plots):
	cemaden_sample = True if parser.get('cemaden', 'write_sample') == 'True' else False
	cemaden_stats = True if parser.get('cemaden', 'write_stats') == 'True' else False
	inmet_sample = True if parser.get('inmet', 'write_sample') == 'True' else False
	inmet_stats = True if parser.get('inmet', 'write_stats') == 'True' else False
	start = dt.datetime.strptime(parser.get('time', 'start'), '%Y-%m-%d %H')
	end = dt.datetime.strptime(parser.get('time', 'end'), '%Y-%m-%d %H')
	## Cell(float w [, float h [, string txt [, mixed border [, 
	## int ln [, string align [, boolean fill [, mixed link]]]]]]])
	pdf = FPDF()
	pdf.add_page()

	cemaden_station_table(pdf, cemaden_sta, start, end)
	if cemaden_stats:
		cemaden_stats_table(pdf, cemaden_sta)
	if cemaden_sample:
		cemaden_pdf_sample(pdf)
	plot_cemaden(pdf, cemaden_plots)
	
	inmet_station_table(pdf, inmet_sta, inmet_stats, start, end)
	if inmet_sample:
		inmet_pdf_sample(pdf)
	plot_inmet(pdf, inmet_plots)
	
	pdf.output('report.pdf', 'F')


def clean_tmp():
	files = glob.glob('./tmp/*')
	for f in files:
		os.remove(f)





























