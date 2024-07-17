#!/usr/bin/env python

# opPtimizer: optimization framework for AI  
# Copyright (c) 2019 Artur Bak. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import time
import os
from .opp import *
from .putils import *
#import pylab as pl
#import matplotlib
#matplotlib.use('GTK')
import matplotlib.pyplot as pl   #TODO: uncomment if pl works
FAKE_PLOT = False  #change to False once pl works


#indexes in ctx_plots[]
PLOT_KEY_IND = 0
PLOT_VAL_IND = 1
PLOT_INV_IND = 2
PLOT_NORM_IND = 3
PLOT_THRESHOLD_IND = 4
PLOT_DISPLAY_IND = 5
PLOT_COLOR_IND = 6
PLOT_LABEL_IND = 7
PLOT_MIN_BETTER = 8 # if lower value is better than greater


tests = []
line_number = 0

main_plot = None
plot_x_line = None
plot_y_line = None
plot_test_line = None
plot_table = None
figure = None

RESULT_VERSION = 3

class PResult:
    def __init__(self):
        return

    def version():
        return 'r' + str(RESULT_VERSION)

def resetPlots():
	global tests,line_number,main_plot,plot_x_line,plot_y_line,plot_test_line,plot_table,figure
	
	tests = []
	line_number = 0

	main_plot = None
	plot_x_line = None
	plot_y_line = None
	plot_test_line = None
	plot_table = None
	figure = None
	
def highlightClosestTest(x,y):
	global plot_test_line, plot_table
	
	test_x = -1
	test_ind = -1
	for i in range(0,len(tests)):
		if tests[i][0] > x:
			if i == 0:
				test_x = tests[i][0]
				test_ind = i
				break
			else:
				if ((tests[i][0] - x) < (x - tests[i-1][0])):
					test_x = tests[i][0]
					test_ind = i
				else:
					test_x = tests[i-1][0]
					test_ind = i - 1
				break
	if (test_x == -1 and len(tests) > 0):
		test_ind = len(tests) - 1
		test_x = tests[test_ind][0]
		
	print('Pointer x', x, ' test ',  test_x, ' ind ', test_ind, 'len', len(tests))
	if (test_x > -1):	
		plot_test_line = main_plot.plot([test_x, test_x], [0,1], color='yellow')
		table_vals=[]
		row_labels = oppkeys(tests[test_ind][1])
		values = oppvals(tests[test_ind][1])
		for value in values:
			value = str(value)
			if len(value) > 20:
				value = value[:20] + '...'
			table_vals.append([value])
		print('TABLE-VALS:', table_vals)
		# the rectangle is where I want to place the table
		plot_table = main_plot.table(cellText=table_vals,
		                  colWidths = [0.1]*3,
		                  rowLabels=row_labels,
		                  loc='upper center')
	else:
		plot_test_line = None
		



def onPress(event):
    global main_plot, plot_x_line, plot_y_line, plot_test_line
    
    x = event.xdata
    y = event.ydata
    print(x, y)
    highlightClosestTest(x,y)
    plot_x_line = main_plot.plot([0,line_number], [y,y], color='red')
    plot_y_line = main_plot.plot([x,x], [0,1], color='red')
    main_plot.draw_artist(plot_x_line[0])
    main_plot.draw_artist(plot_y_line[0])
    if (plot_test_line != None):
        main_plot.draw_artist(plot_test_line[0])
	
    if not FAKE_PLOT:
        pl.draw()	

def onRelease(event):
    global main_plot, plot_x_line, plot_y_line, plot_test_line
    main_plot.lines.remove(plot_x_line[0])
    main_plot.lines.remove(plot_y_line[0])
    if (plot_test_line != None):
    	main_plot.lines.remove(plot_test_line[0])
    	plot_table.remove()
	
    if not FAKE_PLOT:
        pl.draw()

def resetTests():
	global tests
	tests = []

def getValForTest(line, plot):
	val = oppval(plot[PLOT_KEY_IND], line)
	if (val != None):
		if (val == 'Undefined'):
			val = '0.0'
		val = float(val)
		val = val/plot[PLOT_NORM_IND]
		
		if (plot[PLOT_INV_IND] == '1'):
			val = 1.0 - val
	return val

def findBestValue(plot, lines, inverse):

	bestVal = 0.0 if not inverse else 1.0 
	for line in lines:
		val = getValForTest(line, plot)
		betterThanBest = val > bestVal if not inverse else val < bestVal
		if betterThanBest:
			bestVal = val
			
	return bestVal
				
def readResultFile(plots, fileName):
	global tests, line_number

	print('PResult:readResultFile..')
	
	lines = getFileLines(fileName)
	if lines:
		print('- lines number: ' + str(len(lines)))
	else:
		print('- no lines read')

	#print(lines)
	line_number = 0
	accepted_lines = 0
	for line in lines:
		line_number += 1
		accepted = True
		bestOption = False
		bestValFound = False
		for plot in plots:
			val = getValForTest(line, plot)
			print('Check val ' + str(val))
			#print('val ' + str(val) + ' th ' + str(plot[PLOT_THRESHOLD_IND]))
			min_better = plot[PLOT_MIN_BETTER] == '1'
			print('MIN_BETTER: ' + str(min_better) + ' in plot  ' + str(plot))
			 # threshold > 1 means that only best value should be accepted (< 0 if 'minbetter' s used)
			bestValueToUse = plot[PLOT_THRESHOLD_IND] > 1.0 if not min_better else plot[PLOT_THRESHOLD_IND] < 0.0
			print('bestval ' + str(bestValueToUse))
			if (not bestValueToUse):
				thresholdNotMet = val < plot[PLOT_THRESHOLD_IND] if not min_better else val > plot[PLOT_THRESHOLD_IND]
				print(' th not meet ' + str(thresholdNotMet))
				if (thresholdNotMet):
					accepted = False
			else:
				bestOption = True
				bestVal = findBestValue(plot, lines, min_better)
				
				bestValFound = val >= bestVal if not min_better else val <= bestVal
				print(' bestVal ' + str(bestVal) + ' bestValFound ' + str(bestValFound))
		
		if (accepted and bestOption):
			accepted = bestValFound
		
		if accepted:

			tests.append([line_number, line])			
			for plot in plots:
				val = getValForTest(line, plot)
				plot[PLOT_VAL_IND].append(val)

			accepted_lines += 1

	print('Accepted lines: ' + str(accepted_lines))
	
def startPlots(plots, params = '', execDir = None):
    global main_plot, plot_x_line, plot_y_line, main_cavas, figure

    print('startPlots..')

    if FAKE_PLOT:
        return

    figure = pl.figure()
    print('startPlots:figure' + str(figure))
    
    main_plot = figure.add_subplot(111)
	
    figure.canvas.mpl_connect('button_press_event', onPress)
    figure.canvas.mpl_connect('button_release_event', onRelease)
    
    #bounding box for plots
    main_plot.plot([0,line_number], [1,1], color="gray")
    main_plot.plot([0,line_number], [0,0], color="gray")
    main_plot.plot([0,0], [0,1], color="gray")
    main_plot.plot([line_number,line_number], [0,1], color="gray")
    
    
    indexes = [pair[0] for pair in tests]
    
    print(str(indexes))
    for plot in plots:
    	if plot[PLOT_DISPLAY_IND] == '1':
    		main_plot.plot(indexes, plot[PLOT_VAL_IND], 'b-o',  color=plot[PLOT_COLOR_IND], label=plot[PLOT_LABEL_IND])
    
    title = oppval('plotTitle', params, default='Experiment result chart')
    plotLabelX = oppval('plotLabelX', params, default='Test cases')
    plotLabelY = oppval('plotLabelY', params, default='Results')
    
    main_plot.legend( loc='upper right', numpoints = 1, fancybox=True )

    main_plot.set_ylim([0, 1.4])
    pl.xlabel(plotLabelX)
    pl.ylabel(plotLabelY)
    figure.suptitle(title)
    pl.grid()
    
    #pl.show()
    if execDir:
        pl.savefig(execDir + P_DIR_SEP + 'plotResultChart.png')
	
def releasePlots():
	global figure

	if not FAKE_PLOT:
		figure.canvas.mpl_disconnect('button_press_event')
		figure.canvas.mpl_disconnect('button_release_event')

def Slot(refSlot, paramsToUpdate):
	return oppmodify(refSlot, paramsToUpdate) 

def applyPlots(plots_strings):
	
	plots = []
	for plot_str in plots_strings:
		key_val = oppval('key', plot_str)
		print("PResult:applyPlots: " + str(plot_str))
		if (key_val != None):
			inverse_val = oppval('inverse', plot_str, '0')
			print("PResult:applyPlots: inverse is " + str(inverse_val))
			norm_val = oppval('normfactor', plot_str)
			if (norm_val == None):
				norm_val = 1.0
			else:
				norm_val = float(norm_val)

			min_better = oppval('minbetter', plot_str, '0')

			threshold_val = oppval('threshold', plot_str)
			if (threshold_val == None):
				if min_better == '0':
					print("default thershold to 0.0")
					threshold_val = 0.0
				else:
					print("default thershold to 1.0")
					threshold_val = 1.0
			else:
				threshold_val = float(threshold_val)
			label_val = oppval('label', plot_str)
			if (label_val == None):
				label_val = key_val
			display_val = oppval('display', plot_str)
			if (display_val == None):
				display_val = '1'
			color_val = oppval('color', plot_str)
			if (color_val == None):
				color_val = 'black'
			plots.append([key_val, [], inverse_val, norm_val, threshold_val, display_val, color_val, label_val, min_better])

	return plots
	
def	preparePlots(plots, resultFile):
	plots = applyPlots(plots)
	readResultFile(plots, resultFile)
	return plots

def displayPlots(plots, params = '', execDir = None):
	startPlots(plots, params, execDir = execDir)  #blocks on show()
	print('Release..')
	releasePlots()
	
def saveResultToFile(newResultFile):
	newFile = open(newResultFile,'w')
	
	for t in tests:
		newFile.write(t[1] + '\n')

def main(argv):
	
	slotBase = 'threshold=0.0'
	
	pl_accuracy = Slot(slotBase,'key=accuracy;color=green;label=Accuracy;display=1')
	pl_precision = Slot(slotBase,'key=precision;color=blue;label=Precision;display=0')
	pl_recall = Slot(slotBase,'key=recall;color=purple;label=Recall;display=0')
	pl_fallout = Slot(slotBase,'key=fallout;inverse=1;color=orange;label=Fallout;display=0')
	pl_sigma = Slot(slotBase,'key=sigma;normfactor=25;threshold=0.01;color=brown;label=Sigma;display=1')
	plots = [pl_fallout, pl_recall, pl_precision, pl_accuracy, pl_sigma]

	plots = preparePlots(plots, 'result.txt')
	displayPlots(plots)


if __name__ == "__main__":
	sys.exit(main(sys.argv))
