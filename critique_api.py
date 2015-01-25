class ProblemType:
	# Once upon a time I was actually going to rasterize the document and detect alignment.
	# It never happened.
	TooManyTabstops = "toomanytabstops"

	# Text
	TooManyFonts = "toomanyfonts"
	TooManyFontSizes = "toomanyfontsizes"
	TooManyColours = "toomanycolours"
	InconsistentBullets = "inconsistentbullets"
	InconsistentBulletEndings = "inconsistentbulletptendings"
	ReusedVerbs = "reusedverbs"
	BoringVerbs = "boringverbs"
	Buzzwords = "buzzwords"
	StudentNumber = "studentnumber"
	InconsistentMonths = "inconsistentmonths"
	OutOfOrderDates = "outoforderdates"

	def humanify(type):
		mapping = {
			ProblemType.OutOfOrderDates: "Your dates are not in reverse-chronological order",
			ProblemType.InconsistentMonths: "Your month abbreviations are inconsistent",
			ProblemType.TooManyFonts: "You used too many font faces",
			ProblemType.TooManyFontSizes: "You used too many font sizes",
			ProblemType.TooManyColours: "You used too many colours",
			ProblemType.InconsistentBullets: "You used multiple types of bullets",
			ProblemType.InconsistentBulletEndings: "Sometimes you ended your bullets with periods, other times you didn't",
			ProblemType.ReusedVerbs: "You used some verbs too frequently",
			ProblemType.BoringVerbs: "These verbs are boring",
			ProblemType.Buzzwords: "You need fewer buzzwords",
			ProblemType.StudentNumber: "You included your student number"
		}
		return mapping[type]

class Snippet:
	def __init__(self, text, highlight_tuple=None, cssclass=None, style=None):
		self.text = text
		self.highlight_tuple = highlight_tuple
		self.css_class = cssclass
		self.style = style

	def __str__(self):
		if not self.highlight_tuple:
			return self.text
		else:
			return self.text[:self.highlight_tuple[0]] + "*" + self.text[self.highlight_tuple[0]:self.highlight_tuple[1]] + "*" + self.text[self.highlight_tuple[1]:]

	def __repr__(self):
		return self.__str__()

	def htmlify(self):
		if not self.highlight_tuple:
			return self.text
		else:
			return self.text[:self.highlight_tuple[0]] + "<strong>" + self.text[self.highlight_tuple[0]:self.highlight_tuple[1]] + "</strong>" + self.text[self.highlight_tuple[1]:]

class ProblemArea:
	def __init__(self, type, page, location=None, snippets=None):
		self.type = type
		self.page = page
		self.location = location
		self.snippets = snippets if snippets else []

	def __str__(self):
		buff = [self.type]
		if self.page:
			buff.append("on page %d" % self.page)
		if self.location:
			buff.append("on page %s" % self.location)
		if self.snippets:
			buff.append("at %s" % self.snippets)
		return " ".join(buff)

	def __repr__(self):
		return self.__str__()

	def humanify(self):
		return ProblemType.humanify(self.type)

class CritiqueGenerator:
	def critique(self, pdf_path):
		# Return an array of ProblemAreas
		raise NotImplemented()
