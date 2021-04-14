import sys
import os
import snt_calc
import snt_parser

# Program entry point
def main():
	if len(sys.argv) != 2:
		print 'Usage: python snt_analyzer.py <path>'
		sys.exit(1)

	# Parses out a dictionary where:
	#     key = mouse directory
	#     value = list of neuron objects
	mouseData = snt_parser.parseMouseData(sys.argv[1], False)

	# Perform analysis over the data and write output files
	for mouseDir, neurons in mouseData.iteritems():
		writeBranches(mouseDir, neurons)
		writeSummary(mouseDir, neurons)

# Writes branch data to a file in the mouse directory
def writeBranches(mouseDir, neurons):
	branchesPath = os.path.join(mouseDir, 'branches.csv')
	print 'Writing branch data to {}'.format(branchesPath)
	with open(branchesPath, 'w') as branchFile:
		branchFile.write(','.join([
			'Source',
			'Neuron',
			'PathId',
			'Length',
			'StartY',
			'EndY',
			'StartX',
			'EndX',
			'StartZ',
			'EndZ',
			'Layer',
			'Complexity',
			'Direction',
			'Percent Along Axon (IV)',
			'Tortuosity',
			'CombinedTreeLength',
			'CombinedTreeCount']) + '\n')
		for neuron in neurons:
			writeBranchesInner(branchFile, neuron, neuron['branches'])

def writeBranchesInner(branchFile, neuron, branches):
	for branch in branches:
		csv = []
		csv.append(neuron['source'])
		csv.append(neuron['name'])
		csv.append(str(branch['id']))
		csv.append(fromFloat(branch['length']))
		csv.append(fromFloat(branch['startY']))
		csv.append(fromFloat(branch['endY']))
		csv.append(fromFloat(branch['startX']))
		csv.append(fromFloat(branch['endX']))
		csv.append(fromFloat(branch['startZ']))
		csv.append(fromFloat(branch['endZ']))
		csv.append(snt_calc.getLayer(branch, neuron))
		csv.append(str(branch['complexity']))
		csv.append(snt_calc.getDirection(branch))
		csv.append(fromFloat(snt_calc.getPercentage(branch, neuron)*100))
		csv.append(fromFloat(snt_calc.getTortuosity(branch)))
		csv.append(fromFloat(branch['combinedTreeLength']))
		csv.append(str(branch['combinedTreeCount']))
		branchFile.write(','.join(csv) + '\n')
		writeBranchesInner(branchFile, neuron, branch['branches'])

# Write summary data to a file in the mouse directory
def writeSummary(mouseDir, neurons):
	summaryPath = os.path.join(mouseDir, 'summary.csv')
	print 'Writing summary data to {}'.format(summaryPath)
	with open(summaryPath, 'w') as summaryFile:
		summaryFile.write(','.join([
			'Source',
			'Neuron',
			'Cell Body Position',
			'Layer IV Start',
			'Layer IV End',
			'Total Branches With Puncta',
			'Total Branches',
			'Primary Branches',
			'Secondary Branches',
			'Tertiary Branches',
			'Quarternary Branches',
			'LII/III Branches',
			'LIV Branches',
			'LV Branches',
			'Primary Layer II/III',
			'Primary Layer V',
			'Primary Layer IV',
			'"Middle" Layer IV',
			'Primary "Middle" Layer IV',
			'Complex "Middle" Layer IV',
			'Layer V Total Length',
			'"Middle" Layer IV Total Length']) + '\n')

		for neuron in neurons:
			totalBranchesWithPuncta = snt_calc.count(neuron, minLength=0.0)
			totalBranches = snt_calc.count(neuron)
			primaryBranches = snt_calc.count(neuron, complexity=1)
			secondaryBranches = snt_calc.count(neuron, complexity=2)
			tertiaryBranches = snt_calc.count(neuron, complexity=3)
			quaternaryBranches = snt_calc.count(neuron, complexity=4)
			layerIIIBranches = snt_calc.count(neuron, layer='II/III')
			layerIVBranches = snt_calc.count(neuron, layer='IV')
			layerVBranches = snt_calc.count(neuron, layer='V')
			primaryLayerIV = snt_calc.count(neuron, complexity=1, layer='IV')
			primaryLayerV = snt_calc.count(neuron, complexity=1, layer='V')
			primaryLayer23 = snt_calc.count(neuron, complexity=1, layer='II/III')
			middleLayerIV = snt_calc.count(neuron, layer='IV', minPercentage=0.25, maxPercentage=0.75)
			primaryMiddleLayerIV = snt_calc.count(neuron, complexity=1, layer='IV', minPercentage=0.25, maxPercentage=0.75)
			complexMiddleLayerIV = snt_calc.count(neuron, minComplexity=2, layer='IV', minPercentage=0.25, maxPercentage=0.75)
			layerVTotalLength = snt_calc.measureLength(neuron, minLength=0.0, layer='V')
			middleLayerIVTotalLength = snt_calc.measureLength(neuron, minLength=0.0, layer='IV', minPercentage=0.25, maxPercentage=0.75)

			csv = []
			csv.append(neuron['source'])
			csv.append(neuron['name'])
			csv.append(fromFloat(neuron['layerIVStart'] - neuron['axon']['startY']))
			csv.append(fromFloat(neuron['layerIVStart']))
			csv.append(fromFloat(neuron['layerIVEnd']))
			csv.append(str(totalBranchesWithPuncta))
			csv.append(str(totalBranches))
			csv.append(str(primaryBranches))
			csv.append(str(secondaryBranches))
			csv.append(str(tertiaryBranches))
			csv.append(str(quaternaryBranches))
			csv.append(str(layerIIIBranches))
			csv.append(str(layerIVBranches))
			csv.append(str(layerVBranches))
			csv.append(str(primaryLayer23))
			csv.append(str(primaryLayerV))
			csv.append(str(primaryLayerIV))
			csv.append(str(middleLayerIV))
			csv.append(str(primaryMiddleLayerIV))
			csv.append(str(complexMiddleLayerIV))
			csv.append(fromFloat(layerVTotalLength))
			csv.append(fromFloat(middleLayerIVTotalLength))
			summaryFile.write(','.join(csv) + '\n')

def fromFloat(number):
	return '%.2f' % number

if __name__== '__main__':
	main()
