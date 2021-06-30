import sys
import os
import snt_calc
import snt_parser

# Program entry point
def main():
	if len(sys.argv) != 2:
		print('Usage: python snt_cutlure_analyzer.py <path>')
		sys.exit(1)

	# Parses out a dictionary where:
	#     key = mouse directory
	#     value = list of neuron objects
	mouseData = snt_parser.parseMouseData(sys.argv[1], True)

	# Perform analysis over the data and write output files
	for mouseDir, neurons in mouseData.items():
		writeBranches(mouseDir, neurons)
		writeSummary(mouseDir, neurons)

# Writes branch data to a file in the mouse directory
def writeBranches(mouseDir, neurons):
	branchesPath = os.path.join(mouseDir, 'branches.csv')
	print('Writing branch data to {}'.format(branchesPath))
	with open(branchesPath, 'w') as branchFile:
		branchFile.write(','.join([
			'Source',
			'Neuron',
			'Length',
			'StartY',
			'EndY',
			'Complexity',
			'Tortuosity']) + '\n')
		for neuron in neurons:
			writeBranchesInner(branchFile, neuron, neuron['branches'])

def writeBranchesInner(branchFile, neuron, branches):
	for branch in branches:
		csv = []
		csv.append(neuron['source'])
		csv.append(neuron['name'])
		csv.append(fromFloat(branch['length']))
		csv.append(fromFloat(branch['startY']))
		csv.append(fromFloat(branch['endY']))
		csv.append(str(branch['complexity']))
		csv.append(fromFloat(snt_calc.getTortuosity(branch)))
		branchFile.write(','.join(csv) + '\n')
		writeBranchesInner(branchFile, neuron, branch['branches'])

# Write summary data to a file in the mouse directory
def writeSummary(mouseDir, neurons):
	summaryPath = os.path.join(mouseDir, 'summary.csv')
	print('Writing summary data to {}'.format(summaryPath))
	with open(summaryPath, 'w') as summaryFile:
		summaryFile.write(','.join([
			'Source',
			'Neuron',
			'Axon Length',
			'Total Branches With Puncta',
			'Total Puncta',
			'Total Branches',
			'Primary Branches',
			'Secondary Branches',
			'Tertiary Branches',
			'Quarternary Branches']) + '\n')

		for neuron in neurons:
			totalBranchesWithPuncta = snt_calc.count(neuron, minLength=0.0)
			totalPuncta = snt_calc.count(neuron, minLength=0.0, maxLength=10.0)
			totalBranches = snt_calc.count(neuron)
			primaryBranches = snt_calc.count(neuron, complexity=1)
			secondaryBranches = snt_calc.count(neuron, complexity=2)
			tertiaryBranches = snt_calc.count(neuron, complexity=3)
			quaternaryBranches = snt_calc.count(neuron, complexity=4)

			csv = []
			csv.append(neuron['source'])
			csv.append(neuron['name'])
			csv.append(fromFloat(neuron['axon']['length']))
			csv.append(str(totalBranchesWithPuncta))
			csv.append(str(totalPuncta))
			csv.append(str(totalBranches))
			csv.append(str(primaryBranches))
			csv.append(str(secondaryBranches))
			csv.append(str(tertiaryBranches))
			csv.append(str(quaternaryBranches))
			summaryFile.write(','.join(csv) + '\n')

def fromFloat(number):
	return '%.2f' % number

if __name__== '__main__':
	main()
