import csv
import sys
import os

#Types of paths
layerIVStart = {}
layerIVEnd = {}
axons = {}
branches = {}

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
	for csvpath in files:
		with open(csvpath) as csvfile:
			reader = csv.reader(csvfile,delimiter=',', quotechar='"')
			next(reader, None) #skip header
			data = [line for line in reader]
			analyzeFile(data)
			checkData()
			printSummary(csvpath)

def analyzeFile(data):
	for row in data:
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

def keyFromPathName(pathName):
	return ''.join(pathName.split(' ') [:2])

def checkData():
	numKeys = len(branches)
	if len(layerIVStart) != numKeys or len(layerIVEnd) != numKeys or len(axons) !=numKeys:
		print 'Error: inconsistent number of keys, check the data'
		sys.exit(1)

def printSummary(filepath):

	for key in layerIVStart:
		primaryBranches = 0
		secondaryBranches = 0
		layerIIIBranches = 0
		layerIVBranches = 0
		layerVBranches = 0
		middleThirdBranches = 0

		for branch in branches[key]:
			if branch['startY'] < layerIVStart[key]:
				layerIIIBranches += 1
			elif branch['startY'] < layerIVEnd[key]:
				layerIVBranches += 1
				percent = (branch['startY'] - layerIVStart[key])/(layerIVEnd[key] - layerIVStart[key])
				if percent > (1.0/3) and percent < (2.0/3):
					middleThirdBranches += 1
			else:
				layerVBranches += 1

			if branch['startsOnPath'] == axons[key]['id']:
				primaryBranches += 1
			else:
				secondaryBranches += 1

		print '{},{},{},{},{},{},{},{},{},{},{}'.format(key, layerIVStart[key], layerIVEnd[key], len(branches[key]), primaryBranches, secondaryBranches, layerIIIBranches, layerIVBranches, middleThirdBranches, layerVBranches, filepath)


if __name__== "__main__":
	main()
