import csv
import sys
import os
import math

# Program entry point
def main():
	if len(sys.argv) != 2:
		print 'Usage: python snt-analyzer.py <path>'
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
	layerIVStart = {}
	layerIVEnd = {}
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
			startX = float(row[10])
			endX = float(row[13])
			startZ = float(row[12])
			endZ = float(row[15])

			if primaryPath:
				key = keyFromPathName(pathName)
				if pathName.endswith('s to iv'):
					if key in layerIVStart:
						parseError('found multiple soma to IV paths', key, path)
					layerIVStart[key] = max(startY, endY)

				elif pathName.endswith('layer iv'):
					if key in layerIVEnd:
						parseError('found multiple layer IV paths', key, path)
					layerIVEnd[key] = max(startY, endY)

				elif pathName.endswith('axon'):
					if key in axons:
						parseError('found multiple axons', key, path)
					axon = {}
					axon['id'] = pathId
					axon['startY'] = startY
					axons[key] = axon

				else:
					parseError('primary path has unexpected ending: {}'.format(pathName), key, path)

			else:
				branch = {}
				branch['id'] = pathId
				branch['startY'] = startY
				branch['endY'] = endY
				branch['startX'] = startX
				branch['endX'] = endX
				branch['startZ'] = startZ
				branch['endZ'] = endZ
				branch['parentId'] = startsOnPath
				branch['length'] = pathLength
				branches[pathId] = branch

	# Make sure keys match
	checkKeys(axons, layerIVStart, path)
	checkKeys(axons, layerIVEnd, path)

	neurons = []
	for key in layerIVStart:
		neuron = {}
		neuron['name'] = key
		neuron['layerIVStart'] = layerIVStart[key]
		neuron['layerIVEnd'] = layerIVEnd[key]
		neuron['source'] = path
		neuron['branches'] = getChildren(branches, axons[key]['id'], 1)
		neuron['axon'] = axons[key]
		neurons.append(neuron)
	return neurons

def keyFromPathName(pathName):
	return ''.join(pathName.split(' ')[:2])

def checkKeys(dict1, dict2, path):
	keys1 = set(dict1.keys())
	keys2 = set(dict2.keys())
	if keys1 != keys2:
		print 'Error: inconsistent keys in file {}'.format(path)
		print '  {} vs {}'.format(keys1, keys2)
		sys.exit(1)

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
		branchFile.write('Source,Neuron,PathId,Length,StartY,EndY,StartX,EndX,StartZ,EndZ,Layer,Complexity,Direction,Percent Along Axon (IV),Tortuosity\n')
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
		csv.append(getLayer(branch, neuron))
		csv.append(str(branch['complexity']))
		csv.append(getDirection(branch))
		csv.append(fromFloat(getPercentage(branch, neuron) *100))
		csv.append(fromFloat(getTortuosity(branch)))
		branchFile.write(','.join(csv) + '\n')
		writeBranchesInner(branchFile, neuron, branch['branches'])

# Write summary data to a file in the mouse directory
def writeSummary(mouseDir, neurons):
	summaryPath = os.path.join(mouseDir, 'summary.csv')
	print 'Writing summary data to {}'.format(summaryPath)
	with open(summaryPath, 'w') as summaryFile:
		summaryFile.write('Source,Neuron,Cell Body Position,Layer IV Start,Layer IV End,Total Puncta,Total Branches,Primary Branches,Secondary Branches,Tertiary Branches,Quarternary Branches,LII/III Branches,LIV Branches,"Middle" LIV Branches,LV Branches,Primary Layer II/III,Primary Layer V,Primary Layer IV,Primary Middle Third,Complex Middle LayerIV\n')
		for neuron in neurons:
			totalPuncta = countBranches(neuron['branches'], isPuncta)
			totalBranches = countBranches(neuron['branches'], isBranch)
			primaryBranches = countBranches(neuron['branches'], isComplex, complexity=1)
			secondaryBranches = countBranches(neuron['branches'], isComplex, complexity=2)
			tertiaryBranches = countBranches(neuron['branches'], isComplex, complexity=3)
			quaternaryBranches = countBranches(neuron['branches'], isComplex, complexity=4)
			layerIIIBranches =  countBranches(neuron['branches'], isLayer, layer='II/III', neuron=neuron)
			layerIVBranches = countBranches(neuron['branches'], isLayer, layer='IV', neuron=neuron)
			layerVBranches = countBranches(neuron['branches'], isLayer, layer='V', neuron=neuron)
			middleThirdBranches = countBranches(neuron['branches'], isMiddleThird, neuron=neuron)
			primaryLayerIV = countBranches(neuron['branches'], isPrimaryLayerIV, neuron=neuron)
			primaryLayerV = countBranches(neuron['branches'], isPrimaryLayerV, neuron=neuron)
			primaryLayer23 = countBranches(neuron['branches'], isPrimaryLayer23, neuron=neuron)
			primaryMiddleThird = countBranches(neuron['branches'], isPrimaryMiddleThird, neuron=neuron)
			complexMiddleThird = countBranches(neuron['branches'], isComplexMiddleLayerIV, neuron=neuron)

			csv = []
			csv.append(neuron['source'])
			csv.append(neuron['name'])
			csv.append(fromFloat(neuron['layerIVStart'] - neuron['axon']['startY']))
			csv.append(fromFloat(neuron['layerIVStart']))
			csv.append(fromFloat(neuron['layerIVEnd']))
			csv.append(str(totalPuncta))
			csv.append(str(totalBranches))
			csv.append(str(primaryBranches))
			csv.append(str(secondaryBranches))
			csv.append(str(tertiaryBranches))
			csv.append(str(quaternaryBranches))
			csv.append(str(layerIIIBranches))
			csv.append(str(layerIVBranches))
			csv.append(str(middleThirdBranches))
			csv.append(str(layerVBranches))
			csv.append(str(primaryLayer23))
			csv.append(str(primaryLayerV))
			csv.append(str(primaryLayerIV))
			csv.append(str(primaryMiddleThird))
			csv.append(str(complexMiddleThird))
			summaryFile.write(','.join(csv) + '\n')

def countBranches(branches, supplier, **kwargs):
	count = 0
	for branch in branches:
		count += countBranches(branch['branches'], supplier, **kwargs)
		count += supplier(branch, **kwargs)
	return count

# Branches are anything greater than 10um, otherwise they are puncta
def isBranch(branch, **kwargs):
	return 1 if branch['length'] > 10 else 0

def isPuncta(branch, **kwargs):
	return 1 if not isBranch(branch, **kwargs) else 0

def isComplex(branch, **kwargs):
	return isBranch(branch, **kwargs) if branch['complexity'] == kwargs['complexity'] else 0

def isLayer(branch, **kwargs):
	return isBranch(branch, **kwargs) if getLayer(branch, kwargs['neuron']) == kwargs['layer'] else 0

def isMiddleThird(branch, **kwargs):
	neuron = kwargs['neuron']
	if getLayer(branch, neuron) == 'IV':
		percent = getPercentage(branch, neuron)
		return isBranch(branch, **kwargs) if percent > (1.0/4) and percent < (3.0/4) else 0
	return 0

def isPrimaryMiddleThird(branch, **kwargs):
	return isBranch(branch, **kwargs) if branch['complexity'] == 1 and isMiddleThird(branch, **kwargs) else 0

def isComplexMiddleLayerIV(branch, **kwargs):
	return isBranch(branch, **kwargs) if branch['complexity'] > 1 and isMiddleThird(branch, **kwargs) else 0

def isPrimaryLayerIV(branch, **kwargs):
	return isBranch(branch, **kwargs) if branch['complexity'] == 1 and getLayer(branch, kwargs['neuron']) == 'IV' else 0

def isPrimaryLayerV(branch, **kwargs):
	return isBranch(branch, **kwargs) if branch['complexity'] == 1 and getLayer(branch, kwargs['neuron']) == 'V' else 0

def isPrimaryLayer23(branch, **kwargs):
	return isBranch(branch, **kwargs) if branch['complexity'] == 1 and getLayer(branch, kwargs['neuron']) == 'II/III' else 0

def getLayer(branch, neuron):
	if branch['startY'] < neuron['layerIVStart']:
		return 'II/III'
	elif branch['startY'] < neuron['layerIVEnd']:
		return 'IV'
	else:
		return 'V'

def getTortuosity(branch, **kwargs):
	distance = math.sqrt(math.pow(branch['startY']-branch['endY'],2) + math.pow(branch['startX']-branch['endX'],2) + math.pow(branch['startZ']-branch['endZ'],2))
	return branch['length']/distance

def getPercentage(branch, neuron):
	return (branch['startY'] - neuron['layerIVStart'])/(neuron['layerIVEnd'] - neuron['layerIVStart'])

def getDirection(branch):
	if branch['endY'] < branch['startY']:
		return 'II/III'
	elif branch['endY'] > branch['startY']:
		return 'V'
	else:
		return 'stable'

def fromFloat(number):
	return '%.2f' % number

if __name__== '__main__':
	main()
