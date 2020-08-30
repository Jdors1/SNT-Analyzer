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
		#writeSummary(mouseDir, neurons)

# Finds and parses all files inside directory name CSV and ending with .csv
# extension. Returns a dictionary: key = mouse directory, value = list of
# neuron objects
def parseMouseData():
	mouseData = {}
	for dirpath, dirnames, filenames in os.walk('In_vivo_analysis/JD662_Mouse 2'):
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
			primaryPath = row[3].lower() == 'true'
			pathLength = float(row[4])
			startsOnPath = row[6]
			startY = float(row[11])
			endY = float(row[14])

			if primaryPath:
				key = keyFromPathName(pathName)
				if pathName.endswith(' iv'):
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

			else:
				branch = {}
				branch['id'] = pathId
				branch['startY'] = startY
				branch['endY'] = endY
				branch['parentId'] = startsOnPath
				branch['length'] = pathLength
				#TODO: add where do the branches go and how many uM do they travel
				branches[pathId] = branch 

	numKeys = len(axons)
	if len(layerIVStart) != numKeys or len(layerIVEnd) != numKeys:
		print 'Error: inconsistent number of keys in file {}'.format(path)
		sys.exit(1)

	neurons = []
	for key in layerIVStart:
		neuron = {}
		neuron['name'] = key
		neuron['layerIVStart'] = layerIVStart[key]
		neuron['layerIVEnd'] = layerIVEnd[key]
		neuron['source'] = path
		neuron['branches'] = getChildren(branches, axons[key]['id'])
		neuron['axon'] = axons[key]
		neurons.append(neuron)
	return neurons

def keyFromPathName(pathName):
	return ''.join(pathName.split(' ')[:2])

def parseError(reason, key, path):
	print 'Error: {} for {} in file {}'.format(reason, key, path)
	sys.exit(1)

def getChildren(branches, pathId):
	children = []
	for branchId in branches:
		if branches[branchId]['parentId'] == pathId:
			children.append(branches[branchId])
	for child in children:
		child['branches'] = getChildren(branches, child['id'])
	return children

# Writes branch data to a file in the mouse directory
def writeBranches(mouseDir, neurons):
	branchesPath = os.path.join(mouseDir, 'branches.csv')
	print 'Writing branch data to {}'.format(branchesPath)
	with open(branchesPath, 'w') as branchFile:
		branchFile.write('Source,Neuron,Length,StartY,EndY,Layer,Complexity,Direction\n')
		for neuron in neurons:
			writeBranchesInner(branchFile, neuron, neuron['branches'], 1)

def writeBranchesInner(branchFile, neuron, branches, complexity):
	for branch in branches:
		csv = []
		csv.append(neuron['source'])
		csv.append(neuron['name'])
		csv.append(str(branch['length']))
		csv.append(str(branch['startY']))
		csv.append(str(branch['endY']))
		csv.append(getLayer(branch, neuron))
		csv.append(str(complexity))
		csv.append(getDirection(branch))
		branchFile.write(','.join(csv) + '\n')
		writeBranchesInner(branchFile, neuron, branch['branches'], complexity+1)


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
