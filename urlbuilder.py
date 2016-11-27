class UrlBuilder:
	def __init__(self, base):
		if base[-1] != '?':
			raise ValueError("Base must end with question mark.")
		if "http://" not in base and "https://" not in base:
			raise ValueError("http:// not in base")
		self.base = base
		self.params = []
		self.paramstr = ""
	def addParam(self, opt, val):
		self.params.append([opt, val])
	def getURL(self):
		self.paramstr = ""
		for paramset in self.params:
			self.paramstr += str("=".join([str(p) for p in paramset]))
			self.paramstr += "&"
		return self.base + self.paramstr