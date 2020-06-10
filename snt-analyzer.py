import csv
import sys
import os

# Program entry point
def main():
	if len(sys.argv) != 1:
		print 'Usage: python snt-analyzer.py' 
		sys.exit(1)

	mouseData = parseMouseData()
	for mouseDir, neurons in mouseData.iteritems():
		writeBranches(mouseDir, neurons)
		writeSummary(mouseDir, neurons)

# Finds and parses all files inside directory name CSV and ending with .csv
# extension. Returns a dictionary: key = mouse directory, value = list of
# neuron objects
def parseMouseData():
	mouseData = {}
	for dirpath, dirnames, filenames in os.walk('In_vivo_analysis/GSK null/Mouse8'):
		if dirpath.lower().endswith('/csv'):
			mouseDir = os.path.split(dirpath)[0]
			csvPaths = [os.path.join(dirpath, f) for f in filenames if f.endswith('.csv')]
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
			pathName = row[1].lower()
			key = keyFromPathName(pathName)
			primaryPath = row[3].lower() == 'true'
			pathLength = float(row[4])
			startsOnPath = row[6]
			connectedPathIds = row[8]
			childPathIds = row[9]
			startY = float(row[11])
			endY = float(row[14])

			if not primaryPath:
				branch = {}
				branch['id'] = pathId
				branch['startY'] = startY
				branch['endY'] = endY
				branch['startsOnPath'] = startsOnPath
				branch['connectedPathIds'] = connectedPathIds
				branch['childPathIds'] = childPathIds
				branch['length'] = pathLength
				#TODO: add where do the branches go and how many uM do they travel
				if key not in branches:
					branches[key] =[]
				branches[key].append(branch) 

			elif pathName.endswith(' iv'):
				if key in layerIVStart:
					parseError('found multiple soma to IV paths', key, path)
				layerIVStart[key] = max(startY, endY) 

			elif pathName.endswith(' v'):
				if key in layerIVEnd:
					parseError('found multiple soma to V paths', key, path)
				layerIVEnd[key] = max(startY, endY)

			elif not pathName.endswith(' s'):
				if key in axons:
					parseError('found multiple axons', key, path)
				axon = {}
				axon['id'] = pathId
				axon['length'] = pathLength
				axons[key] = axon

	numKeys = len(branches)
	if len(layerIVStart) != numKeys or len(layerIVEnd) != numKeys or len(axons) != numKeys:
		print 'Error: inconsistent number of keys in file {}'.format(path)
		sys.exit(1)

	neurons = []
	for key in layerIVStart:
		neuron = {}
		neuron['name'] = key
		neuron['layerIVStart'] = layerIVStart[key]
		neuron['layerIVEnd'] = layerIVEnd[key]
		neuron['source'] = path
		neuron['branches'] = branches[key]
		neuron['axon'] = axons[key]
		neurons.append(neuron)
	return neurons

def keyFromPathName(pathName):
	return ''.join(pathName.split(' ')[:2])

def parseError(reason, key, path):
	print 'Error: {} for {} in file {}'.format(reason, key, path)
	sys.exit(1)

# Writes branch data to a file in the mouse directory
def writeBranches(mouseDir, neurons):
	branchesPath = os.path.join(mouseDir, 'branches.csv')
	print 'Writing branch data to {}'.format(branchesPath)
	with open(branchesPath, 'w') as branchFile:
		branchFile.write('Source,Neuron,Length,StartY,EndY,Layer,Complexity,Direction\n')
		for neuron in neurons:
			for branch in neuron['branches']:
				csv = []
				csv.append(neuron['source'])
				csv.append(neuron['name'])
				csv.append(str(branch['length']))
				csv.append(str(branch['startY']))
				csv.append(str(branch['endY']))
				csv.append(getLayer(branch, neuron))
				csv.append(getComplexity(branch, neuron))
				csv.append(getDirection(branch))
				branchFile.write(','.join(csv) + '\n')

# Write summary data to a file in the mouse directory
def writeSummary(mouseDir, neurons):
	summaryPath = os.path.join(mouseDir, 'summary.csv')
	print 'Writing summary data to {}'.format(summaryPath)
	with open(summaryPath, 'w') as summaryFile:
		summaryFile.write('Source,Neuron,Layer IV Start,Layer IV End,Total Branches,Primary Branches,Secondary Branches,LII/III Branches,LIV Branches,"Middle" LIV Branches,LV Branches\n')
		for neuron in neurons:
			primaryBranches = 0
			secondaryBranches = 0
			layerIIIBranches = 0
			layerIVBranches = 0
			layerVBranches = 0
			middleThirdBranches = 0

			for branch in neuron['branches']:
				layer = getLayer(branch, neuron)
				if layer == 'II/III':
					layerIIIBranches += 1
				elif layer == 'IV':
					layerIVBranches += 1
					percent = (branch['startY'] - neuron['layerIVStart'])/(neuron['layerIVEnd'] - neuron['layerIVStart'])
					if percent > (1.0/3) and percent < (2.0/3):
						middleThirdBranches += 1
				else:
					layerVBranches += 1

				if getComplexity(branch, neuron) == 'primary':
					primaryBranches += 1
				else:
					secondaryBranches += 1

			csv = []
			csv.append(neuron['source'])
			csv.append(neuron['name'])
			csv.append(str(neuron['layerIVStart']))
			csv.append(str(neuron['layerIVEnd']))
			csv.append(str(len(neuron['branches'])))
			csv.append(str(primaryBranches))
			csv.append(str(secondaryBranches))
			csv.append(str(layerIIIBranches))
			csv.append(str(layerIVBranches))
			csv.append(str(middleThirdBranches))
			csv.append(str(layerVBranches))
			summaryFile.write(','.join(csv) + '\n')

def getComplexity(branch, neuron):
	if branch['startsOnPath'] == neuron['axon']['id']:
		return 'primary'
	else:
		return 'secondary'

def getLayer(branch, neuron):
	if branch['startY'] < neuron['layerIVStart']:
		return 'II/III'
	elif branch['startY'] < neuron['layerIVEnd']:
		return 'IV'
	else:
		return 'V'

def getDirection(branch):
	if branch['endY'] < branch['startY']:
		return 'II/III'
	elif branch['endY'] > branch['startY']:
		return 'V'
	else:
		return 'stable'

if __name__== '__main__':
	main()
