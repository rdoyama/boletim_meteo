#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt

from utils import log


''' CEMADEN data format
﻿municipio,codEstacao,uf,nomeEstacao,latitude,longitude,datahora,valorMedida
CUIABÁ,510340301A,MT,Jardim Liberdade,-55.99056,-15.61462,2020-12-04 22:20:00.0,0.40,

8 columns
'''


def read_and_group(path):
	'''Reads the data in the .csv file as a DataFrame and
	groups the data by station. Returns a dictionary where
	the key is the name of the station and the values are
	DataFrames.'''

	try:
		data = pd.read_csv(path, index_col=False)
	except FileNotFoundError:
		log(f'No such file or directory: {path}', 2)
	stations = list(set(data['nomeEstacao']))

	grouped_df = {}
	for sta in stations:
		grouped_df[sta] = data[data.nomeEstacao == sta]

	return grouped_df


def filter_by_time(df, start, end):
	'''Select rows where start <= datahora <= end
	Returns a list of mdates objects and a list of indexes
	start and end cannot contain minutes or seconds'''

	datahora = df['datahora']

	# Conversion to datetime
	datahora = [dt.datetime.strptime(i[:-2], '%Y-%m-%d %H:%M:%S') for i in datahora]

	# Indexes selected
	indexes = [i for i, t in enumerate(datahora) if start <= t < end]
	datahora = [i for i in datahora if start <= i < end]

	return datahora, indexes


def precipitation(df, start, end):
	'''Sums the precipitation in 1h intervals,
	end - start must be > 1 hour.
	Returns a list of datetimes and the cumulative precipitation
	by hour'''
	n_hours = int((end - start).total_seconds() / 3600)

	# Cumulative precipitation per hour
	cum_h_prec = np.zeros(n_hours)

	# Initialize the list of hours of size n_hours
	hours = []
	for i in range(n_hours):
		hours.append(start + dt.timedelta(hours=i, minutes=30))

	datahora, indexes = filter_by_time(df, start, end)
	data = (df['valorMedida'][indexes]).to_numpy()

	# Cumulative precipitation
	for n, d in enumerate(datahora):
		h = int((d - start).total_seconds() / 3600)
		cum_h_prec[h] += float(data[n])

	return hours, cum_h_prec

# Plot
def plot_precipitation(hours, cum_h_prec, station, latitude, longitude):
	fig, axs = plt.subplots(1, figsize=(8, 6))
	fig.suptitle(f'Estação {station}\nLatitude: {round(latitude, 5)}, Longitude: {round(longitude, 5)}')
	axs.bar(hours, cum_h_prec, width=0.8/24)
	# Uncomment to write coordinates as annotation
	#bbox_props = dict(boxstyle="round,pad=0.23", fc="w", ec="k", lw=0.5, alpha=0.1)
	#axs.annotate(f'Latitude: {round(latitude, 5)}\nLongitude: {round(longitude, 5)}', xy=(0.38,0.90) ,xycoords='axes fraction',
	#                            fontsize=8, bbox=bbox_props)
	myFmt = mdates.DateFormatter("%H:%M")
	axs.xaxis.set_major_formatter(myFmt)
	axs.set_xlabel('Hora (UTC)')
	axs.set_ylabel('Pluviosidade (mm)')
	axs.xaxis_date()
	axs.autoscale()
	path = './tmp/' + ''.join(station.split(' ')) + '.png'
	plt.savefig(path, dpi=250)
	plt.close()
	return path


def get_sta_info(df):
	'''Returns a dictionary containing information about the station'''
	d = {}
	d['municipio'] = df.loc[0, 'municipio']
	d['uf'] = df.loc[0, 'uf']
	d['latitude'] = df.loc[0, 'longitude']
	d['longitude'] = df.loc[0, 'latitude']
	return d


def sample2csv(df, start, end):
	datahora = df['datahora']

	# Conversion to datetime
	datahora = [dt.datetime.strptime(i[:-2], '%Y-%m-%d %H:%M:%S') for i in datahora]

	# Indexes selected
	indexes = [i for i, t in enumerate(datahora) if start <= t < end]
	data = df.iloc[indexes, :]
	data.reset_index(inplace = True, drop = True)
	data = data.iloc[:10, :]
	data.to_csv('./tmp/sample_cemaden.csv', index=False)


def run_cemaden(parser):
	filename = parser.get('files', 'cemaden')
	start = dt.datetime.strptime(parser.get('time', 'start'), '%Y-%m-%d %H')
	end = dt.datetime.strptime(parser.get('time', 'end'), '%Y-%m-%d %H')
	write_sample = True if parser.get('cemaden', 'write_sample') == 'True' else False
	write_stats = True if parser.get('cemaden', 'write_stats') == 'True' else False
	plots = True if parser.get('cemaden', 'plots') == 'True' else False

	grouped_df = read_and_group(filename)

	prec_data, sta_data = [], {}
	plot_paths = []
	
	for i, (sta, df) in enumerate(grouped_df.items()):
		df.reset_index(inplace = True, drop = True)

		if i == 0 and write_sample:
			sample2csv(df, start, end)

		sta_data[sta] = get_sta_info(df)

		hours, cum_h_prec = precipitation(df, start, end)
		prec_data.append((sta, cum_h_prec))
		latitude, longitude = df['latitude'][0], df['longitude'][0]
		
		if plots:
			plot_paths.append(plot_precipitation(hours, cum_h_prec, 
								sta, latitude, longitude))
	
	if write_stats:
		# Other statistics
		total = 0
		for sta, cp in prec_data:
			tot = sum(cp)
			sta_data[sta]['precipitation'] = tot
	
	return sta_data, plot_paths

