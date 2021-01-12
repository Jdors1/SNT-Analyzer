import csv
import sys
import os

# Program entry point
def main():
	if len(sys.argv) != 2:
		print 'Usage: python snt-cutlure-analyzer.py <path>'
		sys.exit(1)

	mouseData = parseMouseData(sys.argv[1])
	for mouseDir, neurons in mouseData.iteritems():
		writeBranches(mouseDir, neurons)
		writeSummary(mouseDir, neurons)

# Finds and parses all files inside directory name CSV and ending with .csv
# extension. Returns a dictionary: key = mouse directory, value = list of
# neuron objects
def parseMouseData(path):
	mouseData = {}
	for dirpath, dirnames, filenames in os.walk(path):
		if dirpath.lower().endswith('/csv'):
			mouseDir = os.path.split(dirpath)[0]
			csvPaths = [os.path.join(dirpath, f) for f in filenames if f.lower().endswith('.csv')]
			neurons = [neuron for path in csvPaths for neuron in parseCsv(path)]
			mouseData[mouseDir] = neurons
			print 'Found {} neurons across {} csv files in {}'.format(len(neurons), len(csvPaths), mouseDir)
	return mouseData

# Parses a single CSV file at the given path. Returns a list of neuron objects
def parseCsv(path):
	# Types of paths
	axons = {}
	branches = {}

	with open(path) as csvfile:
		reader = csv.reader(csvfile,delimiter=',', quotechar='"')
		next(reader, None) #skip header

		for row in reader:
			pathId = row[0]
			pathName = row[1].lower().strip()
			primaryPath = row[3].lower() == 'true'
			pathLength = float(row[4])
			startsOnPath = row[6]
			startY = float(row[11])
			endY = float(row[14])

			if primaryPath:
				key = keyFromPathName(pathName)

				if pathName.endswith('axon'):
					if key in axons:
						parseError('found multiple axons', key, path)
					axon = {}
					axon['id'] = pathId
					axon['length'] = pathLength
					axons[key] = axon

				else:
					parseError('primary path has unexpected ending: {}'.format(pathName), key, path)

			else:
				branch = {}
				branch['id'] = pathId
				branch['startY'] = startY
				branch['endY'] = endY
				branch['parentId'] = startsOnPath
				branch['length'] = pathLength
				branches[pathId] = branch

	neurons = []
	for key in axons:
		neuron = {}
		neuron['name'] = key
		neuron['source'] = path
		neuron['branches'] = getChildren(branches, axons[key]['id'], 1)
		neuron['axon'] = axons[key]
		neurons.append(neuron)
	return neurons

def keyFromPathName(pathName):
	return ''.join(pathName.split(' ')[:2])

def parseError(reason, key, path):
	print 'Error: {} for {} in file {}'.format(reason, key, path)
	sys.exit(1)

def getChildren(branches, pathId, complexity):
	children = []
	for branchId in branches:
		if branches[branchId]['parentId'] == pathId:
			branches[branchId]['complexity'] = complexity
			children.append(branches[branchId])
	for child in children:
		child['branches'] = getChildren(branches, child['id'], complexity + 1)
	return children

# Writes branch data to a file in the mouse directory
def writeBranches(mouseDir, neurons):
	branchesPath = os.path.join(mouseDir, 'branches.csv')
	print 'Writing branch data to {}'.format(branchesPath)
	with open(branchesPath, 'w') as branchFile:
		branchFile.write('Source,Neuron,Length,StartY,EndY,Complexity\n')
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
		branchFile.write(','.join(csv) + '\n')
		writeBranchesInner(branchFile, neuron, branch['branches'])

# Write summary data to a file in the mouse directory
def writeSummary(mouseDir, neurons):
	summaryPath = os.path.join(mouseDir, 'summary.csv')
	print 'Writing summary data to {}'.format(summaryPath)
	with open(summaryPath, 'w') as summaryFile:
		summaryFile.write('Source,Neuron,Axon Length,Total Branches,Primary Branches,Secondary Branches,Tertiary Branches,Quarternary Branches, Branches Greater than 30uM\n')
		for neuron in neurons:
			totalBranches = countBranches(neuron['branches'], isBranch)
			primaryBranches = countBranches(neuron['branches'], isComplex, complexity=1)
			secondaryBranches = countBranches(neuron['branches'], isComplex, complexity=2)
			tertiaryBranches = countBranches(neuron['branches'], isComplex, complexity=3)
			quaternaryBranches = countBranches(neuron['branches'], isComplex, complexity=4)
			greaterThan30 = countBranches(neuron['branches'], isLong)

			csv = []
			csv.append(neuron['source'])
			csv.append(neuron['name'])
			csv.append(fromFloat(neuron['axon']['length']))
			csv.append(str(totalBranches))
			csv.append(str(primaryBranches))
			csv.append(str(secondaryBranches))
			csv.append(str(tertiaryBranches))
			csv.append(str(quaternaryBranches))
			csv.append(str(greaterThan30))
			summaryFile.write(','.join(csv) + '\n')

def countBranches(branches, supplier, **kwargs):
	count = 0
	for branch in branches:
		count += countBranches(branch['branches'], supplier, **kwargs)
		count += supplier(branch, **kwargs)
	return count

def isBranch(branch, **kwargs):
	return 1

def isComplex(branch, **kwargs):
	return 1 if branch['complexity'] == kwargs['complexity'] else 0

def isLong(branch, **kwargs):
	return 1 if branch['length'] > 30 else 0

def fromFloat(number):
	return '%.2f' % number

if __name__== '__main__':
	main()
