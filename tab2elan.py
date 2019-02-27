# -*- coding: utf-8 -*-

#
# Tab区切りファイルからELAN(eaf)ファイルを作成
#

import sys, os
import re
import argparse
from xml.etree.ElementTree import Element, SubElement, parse, tostring
from xml.dom.minidom import parseString

# Arguments
p = argparse.ArgumentParser(description='This script converts a transcript file into a tab-splitted file for ELAN')
p.add_argument('inputfile')
p.add_argument('outputfile')
p.add_argument('-odf', '--outdefault', default="elan_raw.eaf", help="Output default file (empty eaf file)")
p.add_argument('-ie', '--inputencoding', default='utf-8', help="Input file encoding")
p.add_argument('-oe', '--outputencoding', default='utf-8', help="Output file encoding")
args = p.parse_args()

filename_input = args.inputfile
filename_output = args.outputfile
filename_output_default = args.outdefault
INPUT_FILE_ENCODING = args.inputencoding
OUTPUT_FILE_ENCODING = args.outputencoding

TIER_TYPES = [
	u"Utterance(ERICA)", u"Utterance(Subject)",
	u"Filler(ERICA)" , u"Filler(Subject)",
	u"Backchannel(ERICA)", u"Backchannel(Subject)",
	u"Laugh(ERICA)", u"Laugh(Subject)",
]

if os.path.exists(filename_input) == False:
	print("Input file not found ! : %s" % filename_input)
	sys.exit()

# 出力のディレクトリがなければ作る
if os.path.exists(os.path.dirname(filename_output)) == False and len(os.path.dirname(filename_output).rstrip()) > 0:
	os.makedirs(os.path.dirname(filename_output))

# タブで区切られた情報を読み込む
f = open(filename_input, 'r', encoding=INPUT_FILE_ENCODING)
lines = f.readlines()
f.close()

# TIER_TYPESを自動で判定
tier_types = {}
for line in lines:
	tier_name = line.split('\t')[0].strip()
	tier_types[tier_name] = 1
TIER_TYPES = tier_types.keys()

data = []
time_data = []
time_index = 1
annotation_index = 1
for line in lines:
	
	#line = line.decode(INPUT_FILE_ENCODING)

	d = line.split('\t')
	if len(d) != 4:
		continue

	tier = d[0].rstrip()
	start_sec = float(d[1].rstrip())
	start_mill = int(start_sec * 1000) # ミリ秒にする
	end_sec = float(d[2].rstrip())
	end_mill = int(end_sec * 1000) # ミリ秒にする
	annotation = d[3].rstrip()

	time_data.append([time_index, start_mill])
	start_mill_index = time_index
	time_index += 1
	time_data.append([time_index, end_mill])
	end_mill_index = time_index
	time_index += 1
	
	data.append([annotation_index, tier, start_mill_index, end_mill_index, annotation])
	annotation_index += 1

# ベースとなるEAF(XML)ファイルを読み込む
tree = parse(filename_output_default) # 返値はElementTree型
root = tree.getroot() # ルート要素を取得(Element型)

# 時間情報を追加
time_order = SubElement(root, 'TIME_ORDER')
for time in time_data:
	slot_id = ('ts%d'%time[0])#.decode(OUTPUT_FILE_ENCODING)
	slot_value = ('%d' % time[1])#.decode(OUTPUT_FILE_ENCODING)
	time_slot = SubElement(time_order, 'TIME_SLOT', {'TIME_SLOT_ID': slot_id, 'TIME_VALUE': slot_value})

# Tier情報を追加
for tier_type in TIER_TYPES:
	tier_id = tier_type
	tier = SubElement(root, 'TIER', {'DEFAULT_LOCALE': 'us', 'LINGUISTIC_TYPE_REF': 'default', 'TIER_ID': tier_id})

# アノテーション情報を追加
for d in data:
	
	annotation_index = ('a%d'%d[0])#.decode(OUTPUT_FILE_ENCODING)
	tier_id = d[1]#.encode(OUTPUT_FILE_ENCODING)
	start_index = ('ts%d'%d[2])#.decode(OUTPUT_FILE_ENCODING)
	end_index =  ('ts%d'%d[3])#.decode(OUTPUT_FILE_ENCODING)
	annotation = d[4]#.encode(OUTPUT_FILE_ENCODING)

	for tier in root.getchildren():
		if tier.tag == "TIER":
			if tier.attrib['TIER_ID'] == tier_id:
				sub1 = SubElement(tier, 'ANNOTATION')
				sub2 = SubElement(sub1, 'ALIGNABLE_ANNOTATION',
					{'ANNOTATION_ID': annotation_index, 'TIME_SLOT_REF1': start_index, 'TIME_SLOT_REF2': end_index}
				)
				sub3 = SubElement(sub2, 'ANNOTATION_VALUE')
				sub3.text = annotation

# XMLを整形して書き出し
out_txt = parseString(tostring(root)).toprettyxml()
f = open(filename_output, 'w', encoding=OUTPUT_FILE_ENCODING)
f.write(out_txt)
f.close()
#tree.write(filename_output)
