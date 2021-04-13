import math

def summate(branches, supplier, **kwargs):
	total = 0
	for branch in branches:
		total += summate(branch['branches'], supplier, **kwargs)
		total += supplier(branch, **kwargs)
	return total

# Branches are anything greater than 10um, otherwise they are puncta
def isBranch(branch, **kwargs):
	if 'includePuncta' in kwargs and kwargs['includePuncta']:
		return 1
	else:
		return 1 if branch['length'] > 10 else 0

def isComplex(branch, **kwargs):
	return isBranch(branch, **kwargs) if branch['complexity'] == kwargs['complexity'] else 0

def isLayer(branch, **kwargs):
	return isBranch(branch, **kwargs) if getLayer(branch, kwargs['neuron']) == kwargs['layer'] else 0

def isMiddleLayerIV(branch, **kwargs):
	neuron = kwargs['neuron']
	if getLayer(branch, neuron) == 'IV':
		percent = getPercentage(branch, neuron)
		return isBranch(branch, **kwargs) if percent > (1.0/4) and percent < (3.0/4) else 0
	return 0

def isPrimaryMiddleLayerIV(branch, **kwargs):
	return isBranch(branch, **kwargs) if branch['complexity'] == 1 and isMiddleLayerIV(branch, **kwargs) else 0

def isComplexMiddleLayerIV(branch, **kwargs):
	return isBranch(branch, **kwargs) if branch['complexity'] > 1 and isMiddleLayerIV(branch, **kwargs) else 0

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

def getTortuosity(branch):
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

def getMiddleLayerIVLength(branch, **kwargs):
	return branch['length'] if isMiddleLayerIV(branch, **kwargs) else 0

def getLayerLength(branch, **kwargs):
	return branch['length'] if isLayer(branch, **kwargs) else 0
