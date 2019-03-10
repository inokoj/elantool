# -*- coding: utf-8 -*-

#
# 書き起こしファイルからTab区切りファイルを作成
#

import sys, os
import re
import argparse

# Arguments
p = argparse.ArgumentParser(description='This script converts a transcript file into a tab-splitted file for ELAN')
p.add_argument('inputfile')
p.add_argument('outputfile')
p.add_argument('-ot', '--fileopentype_output', default="w", help="File writing mode for the output file (w or a)")
p.add_argument('-d', '--data_type', default="all", help="data type (e.g. text, filler)")
p.add_argument('-p', '--person', default="ERICA", help="person label (e.g. ERICA or SUBJECT)")
p.add_argument('-ie', '--inputencoding', default='shift-jis', help="Input file encoding")
p.add_argument('-oe', '--outputencoding', default='shift-jis', help="Output file encoding")
args = p.parse_args()

filename_input = args.inputfile
filename_output = args.outputfile
fileopentype_output = args.fileopentype_output
person = args.person
data_type = args.data_type
INPUT_FILE_ENCODING = args.inputencoding
OUTPUT_FILE_ENCODING = args.outputencoding

SPLIT_WORD = u' '

PATTERN_TIME = r"\d{4} \d{5}\.\d{3}[-\s]\d{5}\.\d{3} .:"

# tier type, pattern, tier name (used in ELAN)
# PATTERN_TEXT = [
# 	["text", r".+" , "Utterance(%s)" % person],
# 	["filler", r".*\(F .+\).*", "Filler(%s)" % person],
# 	["backchannel", r".*\(I .+\).*", "Backchannel(%s)" % person],
# 	["laugh", r"\{LAUGH\}", "Laugh(%s)" % person],
# 	["laugh", r".*\(L .+ L\).*", "Laugh(%s)" % person],	# "{LAUGH}"と"(L L)"は排反なのでOK
# ]

PATTERN_TEXT = [
	["text", r".+" , "Utterance(%s)" % person],
	["luuda", r".+" , "LUU_DA(%s)" % person],
	["filler", r".*\(F .+\).*", "Filler(%s)" % person],
	["backchannel", r".*\(I .+\).*", "Backchannel(%s)" % person],
	["laugh", r"\{LAUGH\}", "Laugh(%s)" % person],
	["laugh", r".*\(L .+ L\).*", "Laugh(%s)" % person],	# "{LAUGH}"と"(L L)"は排反なのでOK
]

DATA_ALL = {}

# Check the input file
if os.path.exists(filename_input) == False:
	print("Input file not found ! : %s" % filename_input)
	sys.exit()

# 出力のディレクトリがなければ作る
if os.path.exists(os.path.dirname(filename_output)) == False and len(os.path.dirname(filename_output).rstrip()) > 0:
	os.makedirs(os.path.dirname(filename_output))

# Read the input file
f = open(filename_input, 'r', encoding=INPUT_FILE_ENCODING)
lines = f.readlines()
f.close()
print('Input : ' + filename_input)

def store_data(text_list, start, end):
	#global DATA_ALL, PATTERN_TEXT

	for pattern in PATTERN_TEXT:

		if pattern[0] != data_type and data_type != 'all':
			continue

		matched = False
		t = pattern[0]
		p = pattern[1]
		tier = pattern[2]
		for text in text_list:
			if re.match(p, text):
				matched = True

		text_long = ' '.join(text_list)

		if re.match(p, text_long):
			matched = True

		if matched == True:
			if t not in DATA_ALL:
				DATA_ALL[t] = []
			DATA_ALL[t].append([text_list, tier, start, end])

text_list = []

start = 0.
end = 0.

for line in lines:
	
	line = line.rstrip()

	# Time 
	if re.match(PATTERN_TIME, line):

		# Store the data
		if len(text_list) > 0:
			store_data(text_list, start, end)

		index = int(line.split(' ')[0])
		
		if len(line.split(' ')) == 3:
			start = float(line.split(' ')[1].split('-')[0])
			end = float(line.split(' ')[1].split('-')[1])
			person = line.split(' ')[2][0]
		
		# 時間がハイフンではなくスペースで区切られていた場合の対策
		elif len(line.split(' ')) == 4:
			start = float(line.split(' ')[1])
			end = float(line.split(' ')[2])
			person = line.split(' ')[3]

		text_list = []
	
	# Text
	else:
		# コメントアウトがあった場合の対策
		if "%" in line:
			line = line.split("%")[0].strip()
		
		text_list.append(line)

# Store the data of the last IPU
if len(text_list) > 0:
	store_data(text_list, start, end)

# Output
f = open(filename_output, fileopentype_output, encoding=OUTPUT_FILE_ENCODING)
for data_type in DATA_ALL.values():
	for data in data_type:
		text = SPLIT_WORD.join(data[0])
		tier = data[1]
		start = data[2]
		end = data[3]

		f.write('%s\t%f\t%f\t%s\n' % (tier, start, end, text))
f.close()
print('Output : ' + filename_output)