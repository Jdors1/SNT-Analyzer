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
			'Total Puncta',
			'Total Primary Puncta',
			'Total Branches',
			'Total Branch Length',
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
			'Layer II/III Total Length',
			'"Middle" Layer IV Total Length',
			'Primary Middle Layer IV Puncta',
			'Primary Layer V Puncta',
			'Layer V Puncta',
			'Layer IV Puncta',
			'Primary Layer IV Puncta',
			'Layer II/III Puncta',
			'Primary Layer II/III Puncta',
			'Middle Layer IV Puncta']) + '\n')

		for neuron in neurons:
			totalBranchesWithPuncta = snt_calc.count(neuron, minLength=0.0)
			totalPuncta = snt_calc.count(neuron, minLength=0.0, maxLength=10.0)
			totalPrimaryPuncta = snt_calc.count(neuron, minLength=0.0, maxLength=10.0, complexity=1)
			totalBranches = snt_calc.count(neuron)
			totalBranchLength = snt_calc.measureLength(neuron, minLength=0.0)
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
			layer23TotalLength = snt_calc.measureLength(neuron, minLength=0.0, layer ='II/III')
			middleLayerIVTotalLength = snt_calc.measureLength(neuron, minLength=0.0, layer='IV', minPercentage=0.25, maxPercentage=0.75)
			primaryMiddleLayerIVPuncta = snt_calc.count(neuron, minLength=0.0, maxLength=10.0, layer ='IV', complexity=1, minPercentage=0.25, maxPercentage=0.75)
			primaryLayerVPuncta = snt_calc.count(neuron, minLength=0.0, maxLength=10.0, layer='V', complexity=1)
			layerVPuncta = snt_calc.count(neuron, minLength=0.0, maxLength=10.0, layer='V')
			layerIVPuncta = snt_calc.count(neuron, minLength=0.0, maxLength=10.0, layer='IV')
			primaryLayerIVPuncta = snt_calc.count(neuron, minLength=0.0, maxLength=10.0, layer='IV', complexity=1)
			layer23Puncta = snt_calc.count(neuron, minLength=0.0, maxLength=10.0, layer='II/III')
			primaryLayer23Puncta = snt_calc.count(neuron, minLength=0.0, maxLength=10.0, layer='IV', complexity=1)
			middleLayerIVPuncta = snt_calc.count(neuron, minLength=0.0, maxLength=10.0, layer='IV')

			csv = []
			csv.append(neuron['source'])
			csv.append(neuron['name'])
			csv.append(fromFloat(neuron['layerIVStart'] - neuron['axon']['startY']))
			csv.append(fromFloat(neuron['layerIVStart']))
			csv.append(fromFloat(neuron['layerIVEnd']))
			csv.append(str(totalBranchesWithPuncta))
			csv.append(str(totalPuncta))
			csv.append(str(totalPrimaryPuncta))
			csv.append(str(totalBranches))
			csv.append(fromFloat(totalBranchLength))
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
			csv.append(fromFloat(layer23TotalLength))
			csv.append(fromFloat(middleLayerIVTotalLength))
			csv.append(str(primaryMiddleLayerIVPuncta))
			csv.append(str(primaryLayerVPuncta))
			csv.append(str(layerVPuncta))
			csv.append(str(layerIVPuncta))
			csv.append(str(primaryLayerIVPuncta))
			csv.append(str(layer23Puncta))
			csv.append(str(primaryLayer23Puncta))
			csv.append(str(middleLayerIVPuncta))
			summaryFile.write(','.join(csv) + '\n')

def fromFloat(number):
	return '%.2f' % number

if __name__== '__main__':
	main()
