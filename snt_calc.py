import math

def count(neuron, **kwargs):
	return summate(lambda b: 1, neuron['branches'], neuron, **kwargs)

def measureLength(neuron, **kwargs):
	return summate(lambda b: b['length'], neuron['branches'], neuron, **kwargs)

def summate(reducer, branches, neuron, **kwargs):
	total = 0
	for branch in branches:
		if matches(branch, neuron, **kwargs):
			total += reducer(branch)
		total += summate(reducer, branch['branches'], neuron, **kwargs)
	return total

def matches(branch, neuron, **kwargs):
	match = True
	if 'minLength' in kwargs:
		match = match and branch['length'] > kwargs['minLength']
	else:
		match = match and branch['length'] > 10.0 # Default to this unless caller provides their own min
	if 'maxLength' in kwargs:
		match = match and branch['length'] < kwargs['maxLength']
	if 'layer' in kwargs:
		match = match and getLayer(branch, neuron) == kwargs['layer']
	if 'minPercentage' in kwargs:
		match = match and getPercentage(branch, neuron) > kwargs['minPercentage']
	if 'maxPercentage' in kwargs:
		match = match and getPercentage(branch, neuron) < kwargs['maxPercentage']
	if 'complexity' in kwargs:
		match = match and branch['complexity'] == kwargs['complexity']
	if 'minComplexity' in kwargs:
		match = match and branch['complexity'] >= kwargs['minComplexity']
	if 'maxComplexity' in kwargs:
		match = match and branch['complexity'] <= kwargs['maxComplexity']
	return match

def getLayer(branch, neuron):
	if branch['startY'] < neuron['layerIVStart']:
		return 'II/III'
	elif branch['startY'] < neuron['layerIVEnd']:
		return 'IV'
	else:
		return 'V'

def getTortuosity(branch):
	euclideanDistance = math.sqrt(math.pow(branch['startY']-branch['endY'], 2) +
	                              math.pow(branch['startX']-branch['endX'], 2) +
	                              math.pow(branch['startZ']-branch['endZ'], 2))
	return branch['length']/euclideanDistance

def getPercentage(branch, neuron):
	return (branch['startY'] - neuron['layerIVStart'])/(neuron['layerIVEnd'] - neuron['layerIVStart'])

def getDirection(branch):
	if branch['endY'] < branch['startY']:
		return 'II/III'
	elif branch['endY'] > branch['startY']:
		return 'V'
	else:
		return 'stable'
