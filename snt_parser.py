import csv
import sys
import os
import snt_calc

# Finds and parses all files inside directory name CSV and ending with .csv
# extension. Returns a dictionary: key = mouse directory, value = list of
# neuron objects
def parseMouseData(path, is_culture):
	mouseData = {}
	for dirpath, dirnames, filenames in os.walk(path):
		if dirpath.lower().endswith('/csv'):
			mouseDir = os.path.split(dirpath)[0]
			csvPaths = [os.path.join(dirpath, f) for f in filenames if f.lower().endswith('.csv')]
			neurons = [neuron for path in csvPaths for neuron in parseCsv(path, is_culture)]
			mouseData[mouseDir] = neurons
			print 'Found {} neurons across {} csv files in {}'.format(len(neurons), len(csvPaths), mouseDir)
	return mouseData

# Parses a single CSV file at the given path. Returns a list of neuron objects
def parseCsv(path, is_culture):
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
	if not is_culture:
		checkKeys(axons, layerIVStart, path)
		checkKeys(axons, layerIVEnd, path)

	neurons = []
	for key in layerIVStart:
		neuron = {}
		neuron['name'] = key
		if not is_culture:
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
			child = branches[branchId]
			child['complexity'] = complexity
			child['branches'] = getChildren(branches, child['id'], complexity + 1)
			child['combinedTreeLength'] = child['length']
			child['combinedTreeCount'] = 1
			child['combinedTreeCountSansPuncta'] = snt_calc.isBranch(child)
			for grandchild in child['branches']:
				child['combinedTreeLength'] += grandchild['combinedTreeLength']
				child['combinedTreeCount'] += grandchild['combinedTreeCount']
				child['combinedTreeCountSansPuncta'] += grandchild['combinedTreeCountSansPuncta']
			children.append(child)
	return children
