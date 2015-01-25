from critique_text import TextCritiquer

class Critiquer:
	critiquers = [TextCritiquer()]
	def critique(self, pdf):
		problems = []
		for critiquer in self.critiquers:
			problems += critiquer.critique(pdf)

		deduped_problems = {}
		for problem in problems:
			hk = "%s%s%s" % (problem.type, problem.page, problem.location)
			if hk in deduped_problems:
				deduped_problems[hk].snippets += problem.snippets
			else:
				deduped_problems[hk] = problem
		
		return deduped_problems.values()