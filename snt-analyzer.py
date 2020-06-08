import csv
import sys
import os


def main():
	if len(sys.argv) != 1:
		print 'Usage: python snt-analyzer.py' 
		sys.exit(1)
	
	print 'Neuron,Layer IV Start,Layer IV End,Branches,1st Branches,2nd Branches,LII/III Branches,LIV Branches,"middle" LIV Branches,LV Branches,Source File'

	#Which files we search only with directory name CSV and only with ending in .csv
	for dirpath, dirnames, filenames in os.walk('In_vivo_analysis/GSK null/Mouse8'):
		if dirpath.lower().endswith('/csv'):

			#where to save the output file
			mouseDir = os.path.split(dirpath)[0]
			files = [os.path.join(dirpath, f) for f in filenames if f.endswith('.csv')]
			analyzeMouse(mouseDir, files)
		
def analyzeMouse(mouseDir, files):
	neurons = []
	for csvpath in files:
			neurons.extend(analyzeFile(csvpath))
	writeBranches(mouseDir,neurons)
	printSummary(neurons)

def analyzeFile(csvpath):
	#Types of paths
	layerIVStart = {}
	layerIVEnd = {}
	axons = {}
	branches = {}

	with open(csvpath) as csvfile:
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

			elif pathName.endswith('s to iv'):
				layerIVStart[key] = max(startY, endY) 

			elif pathName.endswith('s to v'):
				layerIVEnd[key] = max(startY, endY)

			elif not pathName.endswith('d to s'):
				axon = {}
				axon['id'] = pathId
				axon['length'] = pathLength
				axons[key] = axon

	numKeys = len(branches)
	if len(layerIVStart) != numKeys or len(layerIVEnd) != numKeys or len(axons) !=numKeys:
		print 'Error: inconsistent number of keys, check the data in {}'.format(csvpath)
		sys.exit(1)

	neurons = []
	for key in layerIVStart:
		neuron = {}
		neuron['name'] = key
		neuron['layerIVStart'] = layerIVStart[key]
		neuron['layerIVEnd'] = layerIVEnd[key]
		neuron['sourceFile'] = csvpath
		neuron['branches'] = branches[key]
		neuron['axon'] = axons[key]
		neurons.append(neuron)
	return neurons


def keyFromPathName(pathName):
	return ''.join(pathName.split(' ') [:2])

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

def writeBranches(mouseDir, neurons):
	#writes to a file in the mouse directory
	branchesPath = os.path.join(mouseDir, 'branches.csv')
	with open(branchesPath, 'w') as branchFile:
		branchFile.write('sourceFile,neuron,length,startY,endY,layer,complexity,direction\n')
		for neuron in neurons:
			for branch in neuron['branches']:
				complexity = getComplexity(branch, neuron)
				layer = getLayer(branch, neuron)
				direction = getDirection(branch)
				branchFile.write('{},{},{},{},{},{},{},{}\n'.format(

					neuron['sourceFile'],
					neuron['name'],
					branch['length'],
					branch['startY'],
					branch['endY'],
					layer, complexity, direction
					))

def printSummary(neurons):
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

		print '{},{},{},{},{},{},{},{},{},{},{}'.format(neuron['name'], neuron['layerIVStart'], neuron['layerIVEnd'], len(neuron['branches']), 
														primaryBranches, secondaryBranches, layerIIIBranches, layerIVBranches, middleThirdBranches, 
														layerVBranches, neuron['sourceFile'])


if __name__== "__main__":
	main()
