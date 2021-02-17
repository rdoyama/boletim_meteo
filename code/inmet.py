#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
from windrose import WindroseAxes
import matplotlib.cm as cm
from utils import log

# vento_dir = Direção horária dos ventos (graus)
# vento_rajmax = Velocidade máxima da rajada (m/s)
# vento_vel = Velocidade horária do vento (m/s)

def read_inmet(path):
	'''Reads data from csv and select columns with: date,
	time, vento_dir, vento_rajmax e vento-vel'''
	try:
		data = pd.read_csv(path, skiprows=8, encoding='ISO8859_15')
	except FileNotFoundError:
		log(f'No such file or directory: {path}', 2)
	data = data.iloc[:, [0, 1, -4, -3, -2]]
	data.columns = ['data', 'hora', 'vento_dir', 'vento_rajmax', 'vento_vel']
	
	# Delete all rows with NaN
	#data = data[data['vento_dir'].notna() & data['vento_rajmax'].notna() & data['vento_vel'].notna()]
	data.dropna(inplace=True)
	data.reset_index(inplace = True, drop = True)
	return data


def filter_by_time(df, start, end):
	# Collects data from DataFrame
	dates = df['data']
	times = df['hora']
	
	# Format string for datetime creation
	times = [i[:2] + ':' + i[2:4] for i in times]
	
	# Datetimes
	datetimes = np.array([dt.datetime.strptime(' '.join([i, j]), '%Y/%m/%d %H:%M') for i, j in zip(dates, times)])
	
	# Filter
	indexes = [i for i, t in enumerate(datetimes) if start <= t < end]
	data = df.iloc[indexes, :]
	data.reset_index(inplace = True, drop = True)
	datetimes = datetimes[indexes]
	return data


def plot_windrose(data):
	# Wind properties
	vento_dir = data['vento_dir'].to_numpy()
	vento_rajmax = data['vento_rajmax'].to_numpy()
	vento_vel = data['vento_vel'].to_numpy()
	
	# Correction
	vento_dir = (vento_dir + 90) % 360

	ax = WindroseAxes.from_ax()
	ax.bar(vento_dir, vento_vel, normed=True, opening=0.8, edgecolor='white', cmap=cm.jet)
	ax.set_xticklabels(['N', 'NW',  'W', 'SW', 'S', 'SE','E', 'NE'])
	
	# Change if necessary
	ax.set_legend(title="Wind speed (m/s)", bbox_to_anchor=(-0.05, -0.11), ncol=6)
	
	ax.set_theta_zero_location('N')
	path = './tmp/windrose.png'
	plt.savefig(path, dpi=250)
	plt.close()
	return path


def get_station_info(path):
	# Station Information
	info = ['regiao', 'uf', 'estacao', 'codigo', 'latitude', 'longitude', 'altitude', 'fundacao']
	si = dict()
	with open(path, 'r', encoding='ISO8859_15') as f:
		for i, line in enumerate(f.readlines()[:8]):
			si[info[i]] = line.strip().split(',')[1]
	return si


def get_statistics(data, si):
	# Other Statistics
	si['rajmax'] = np.max(data['vento_rajmax'])
	si['wind_avg'] = np.mean(data['vento_vel'])


def sample2csv(data):
	data.iloc[:10, :].to_csv('./tmp/sample_inmet.csv', index=False)


def run_inmet(parser):
	filename = parser.get('files', 'inmet')
	start = dt.datetime.strptime(parser.get('time', 'start'), '%Y-%m-%d %H')
	end = dt.datetime.strptime(parser.get('time', 'end'), '%Y-%m-%d %H')
	write_sample = True if parser.get('inmet', 'write_sample') == 'True' else False
	write_stats = True if parser.get('inmet', 'write_stats') == 'True' else False
	plot = True if parser.get('inmet', 'windrose') == 'True' else False
	
	data = read_inmet(filename)
	data = filter_by_time(data, start, end)
	
	path = []
	if plot:
		path.append(plot_windrose(data))
	if write_sample:
		sample2csv(data)
	sta_info = get_station_info(filename)
	if write_stats:
		get_statistics(data, sta_info)
	return sta_info, path

