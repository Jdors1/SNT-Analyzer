import csv
import sys

#Types of paths
layerIVStart = {}
layerIVEnd = {}
axonIds = {}
branches = {}


#Number of primary branches
#Number of secondary branches
#Number of tertiary branches

def keyFromPathName(pathName):
	return ''.join(pathName.split(' ') [:2])
if (len(sys.argv) != 2):
	print 'Usage: python snt-analyzer.py inputfile.csv > outputfile.csv'
	sys.exit(1)
filepath=sys.argv[1]
with open(filepath) as csvfile:
	reader = csv.reader(csvfile,delimiter=',', quotechar='"')
	next(reader, None)
	for row in reader:

		pathId = row[0]
		pathName = row[1].lower()
		key = keyFromPathName(pathName)
		primaryPath = row[3].lower() == 'true'
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

			if key not in branches:
				branches[key] =[]
			branches[key].append(branch) 

		elif pathName.endswith('s to iv'):
			layerIVStart[key] = max(startY, endY) 

		elif pathName.endswith('s to v'):
			layerIVEnd[key] = max(startY, endY)

		elif not pathName.endswith('d to s'):
			axonIds[key] = pathId

numKeys = len(branches)
if len(layerIVStart) != numKeys or len(layerIVEnd) != numKeys or len(axonIds) !=numKeys:
	print 'Error: inconsistent number of keys, check the data'
	sys.exit(1)



print 'Neuron,Layer IV Start,Layer IV End,Branches,1st Branches,2nd Branches,LII/III Branches,LIV Branches,"middle" LIV Branches,LV Branches,Source File'
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

		if branch['startsOnPath'] == axonIds[key]:
			primaryBranches += 1
		else:
			secondaryBranches += 1

	print '{},{},{},{},{},{},{},{},{},{},{}'.format(key, layerIVStart[key], layerIVEnd[key], len(branches[key]), primaryBranches, secondaryBranches, layerIIIBranches, layerIVBranches, middleThirdBranches, layerVBranches, filepath)
