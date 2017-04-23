import sys
import requests
import itertools
import urllib
import string

def findOverlap(x, y, k):
	if len(x) < k or len(y) < k:
		return 0
	idx = len(y)
	while True:
		hit = string.rfind(y, x[-k:], 0, idx)
		if hit == -1:
			return 0
		ln = hit + k
		if x[-ln:] == y[:ln]:
			return ln
		idx = hit + k - 1
	return -1

class OverlapGraph(object):
	def __init__(self):
		self.nodes = {}

	def traverse_graph(self):
		visited = set()
		starts = []
		for node in self.nodes.values():
			if len(node.parents) == 0:
				#starting node
				starts.append(node)
		assembled_texts = []
		for start in starts:
			assembled_text = start.fragment
			curr_node = start
			while len(curr_node.neighbors) > 0:
				if curr_node not in visited:
					key_fn = lambda x:x[0].depth
					next_node, weight = max(curr_node.neighbors.items(), key=key_fn)
					assembled_text += next_node.fragment[weight:]
					visited.add(curr_node)
					curr_node = next_node
				else:
					break
			assembled_texts.append(assembled_text)
		return assembled_texts

	def create_graph(self, shuffled_text, k):
		#call findOverlap for every pair of strings, and k=3
		for i in range(0, len(shuffled_text) - 1):
			max_pre_overlap = 0
			max_post_overlap = 0
			prefix = None
			suffix = None
			x = shuffled_text[i]
			if x in self.nodes:
				curr_node = self.nodes[x]
			else:
				curr_node = OverlapNode(x)
				self.nodes[x] = curr_node
			for j in range(1, len(shuffled_text)):
				if i == j:
					continue
				y = shuffled_text[j]
				pre_overlap = findOverlap(x, y, k)
				if pre_overlap > max_pre_overlap:
					suffix = y
					max_pre_overlap = pre_overlap
				post_overlap = findOverlap(y, x, k)
				if post_overlap > max_post_overlap:
					prefix = y
					max_post_overlap = post_overlap
			# add to graph
			if suffix:
				if suffix in self.nodes:
					suffix_node = self.nodes[suffix]
				else:
					suffix_node = OverlapNode(suffix)
					self.nodes[suffix] = suffix_node
				if not curr_node.has_neighbor(suffix_node):
					curr_node.add_neighbor(suffix_node, max_pre_overlap)
					suffix_node.add_parent(curr_node)
			if prefix:
				if prefix in self.nodes:
					prefix_node = self.nodes[prefix]
				else:
					prefix_node = OverlapNode(prefix)
					self.nodes[prefix] = prefix_node
				if not prefix_node.has_neighbor(curr_node):
					prefix_node.add_neighbor(curr_node, max_post_overlap)
					curr_node.add_parent(prefix_node)

class OverlapNode(object):
	def __init__(self, fragment):
		self.fragment = fragment
		self.neighbors = {}
		self.parents = []
		self.depth = 0

	def add_parent(self, parent):
		self.parents.append(parent)

	def add_neighbor(self, neighbor, weight):
		self.neighbors[neighbor] = weight
		self._update_depth(neighbor)

	def _update_depth(self, neighbor):
		self.depth = max(self.depth, neighbor.depth + 1)
		for parent in self.parents:
			if not self.can_reach(parent):
				parent._update_depth(self)

	def has_neighbor(self, neighbor):
		return neighbor in self.neighbors

	def can_reach(self, other, visited=None):
		reachable = False
		visited = visited or set()
		for neighbor in self.neighbors:
			if neighbor == other:
				return True
			if neighbor in visited:
				continue
			visited.add(neighbor)
			reachable |= neighbor.can_reach(other, visited)
		return reachable

	def __eq__(self, other):
		return self.fragment == other.fragment

	def __str__(self):
		return self.fragment + str(len(self.parents))

	def __repr__(self):
		return str(self)
		
#main method:
def assemble(shuffled_text):
	assembled_fragments = shuffled_text
	k = 3
	graph = OverlapGraph()
	graph.create_graph(assembled_fragments, k)
	assembled_fragments = graph.traverse_graph()
	return assembled_fragments

def main():
	shuffled_text = []
	if len(sys.argv) == 1:
		for line in sys.stdin:
			shuffled_text.append(urllib.unquote_plus(line.rstrip('\n')))
	elif len(sys.argv) == 2:
		shuffled_text = [urllib.unquote_plus(line.rstrip('\n')) for line in open(sys.argv[1])]
	print assemble(shuffled_text)

if __name__ == '__main__':
	main()
