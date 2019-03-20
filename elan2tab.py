# -*- coding: utf-8 -*-

import os, sys
import numpy as np
import scipy as sp
import scipy.ndimage as spimage
import math
from scipy import stats
import copy
import argparse
from xml.etree import ElementTree

# Arguments
p = argparse.ArgumentParser(description='Translate the input eaf file to a tab-splitted file')
p.add_argument('inputfile_eaf')
p.add_argument('outputfile')
p.add_argument('-tiername', default='all')
p.add_argument('-tiername_output', default='none', help='If you want to change the tiername')
p.add_argument('-a', action='store_true', help='Append the content at the end of the outputfile')	# Overwrite
args = p.parse_args()

filename_input_eaf = args.inputfile_eaf
filename_output = args.outputfile

if os.path.exists(filename_input_eaf) == False:
	print("Input file not found ! : %s" % filename_input_eaf)
	sys.exit()

# 出力のディレクトリがなければ作る
if os.path.exists(os.path.dirname(filename_output)) == False and len(os.path.dirname(filename_output).rstrip()) > 0:
	os.makedirs(os.path.dirname(filename_output))

print("Input : %s" % filename_input_eaf)

tree = ElementTree.parse(filename_input_eaf)  # ファイルから読み込み
root = tree.getroot()

# 時間情報を取得
time_slot_data = {}
for child in list(root):
	if child.tag == "TIME_ORDER":
		for time_slot in child.findall('TIME_SLOT'):
			slot_id = time_slot.attrib['TIME_SLOT_ID']
			sec = float(time_slot.attrib['TIME_VALUE']) / 1000.0
			time_slot_data[slot_id] = sec

tier_data = []

print(args.tiername)

# 各Tier毎に処理
for child in list(root):
	if child.tag == "TIER":
		tier_id = child.attrib['TIER_ID'].rstrip()

		if args.tiername != 'all': 
			if tier_id != args.tiername:
				continue

		for annotation in child.findall('ANNOTATION'):
			start_sec = time_slot_data[list(annotation)[0].attrib['TIME_SLOT_REF1']]
			end_sec = time_slot_data[list(annotation)[0].attrib['TIME_SLOT_REF2']]
			text = list(annotation)[0][0].text
			if text == None:
				text = u""

			if args.tiername_output != 'none':
				tier_id = args.tiername_output
			
			# コメントアウトがあった場合の対策
			if "%" in text:
				# %のあとのスペース対策
				for idx in range(10):
					text = text.replace('% ', '%')
				
				# 文節単位で区切る
				data_splited = []
				for t in text.split(' '):
					if t.startswith('%'):
						continue
					data_splited.append(t)
				
				#text = text.split("%")[0].strip()
				text = ' '.join(data_splited)
			
			tier_data.append([tier_id, start_sec, end_sec, text])

# Tab区切りで出力
file_write_type = 'w'
if args.a == True:
	file_write_type = 'a'

f = open(filename_output, file_write_type, encoding='utf-8')

for line in tier_data:
	f.write('%s\t%f\t%f\t%s\n' % (line[0], line[1], line[2], line[3]))
f.close()

print("Output : %s" % filename_output) 
