from critique_api import * # Wheeeeee
import re

class TextCritiquer(CritiqueGenerator):
	bullet_pts = ["›", "•", "»"]
	probably_bullet_pts = ["-", "—", "–", "*", "!"]
	seperator_chars = ["\n", "\t"] + bullet_pts
	flagged_buzzphrases = r"ajax,web 2\.0,synergy,revolution,disrupt,node\.js,ruby,c\+\+,aws,s3,shard,mongo,hadoop,map reduce".split(",")
	blacklisted_verbs = "made,wrote,did,said,worked".split(",")
	month_abbrs = [
		"january,february,march,april,may,june,july,august,september,october,november,december".split(","),
		"jan,feb,march,apr,may,jun,jul,aug,sep,oct,nov,dec".split(",")
	]
	def literal_parser(self, txt):
		literal = txt.group(1)
		if literal == "t":
			return " " # All these were turning into spaces :wtf:
		elif literal == "r":
			return "\r"
		elif literal == "n":
			return "\n"
		elif literal[0] == "U":
			return chr(int(literal[1:], 16))
		pass
	def extract_text(self, pdf):
		import subprocess, ast
		out = subprocess.check_output(["automator", "-i", pdf, "extracttext.workflow/"], stderr=subprocess.STDOUT)
		subprocess.check_output(["textutil", "-convert", "txt", "/Volumes/MacintoshHD/Users/collinfair/Desktop/uploaded.rtf"])
		rtf = open("/Volumes/MacintoshHD/Users/collinfair/Desktop/uploaded.rtf", "rb").read().decode("utf-8")
		text = open("/Volumes/MacintoshHD/Users/collinfair/Desktop/uploaded.txt", "rb").read().decode("utf-8")
		return rtf, text

	def critique(self, pdf):
		problems = []
		rtf, txt = self.extract_text(pdf)
		runs = re.findall("(?:[%s])(?:[^%s]+)" % ("".join(self.seperator_chars), "".join(self.seperator_chars)), txt)
		runs = [x.strip() for x in runs]

		problems += self.bullet_consistency(runs)
		problems += self.verbs(runs)
		problems += self.buzzphrases(runs)
		problems += self.student_number(runs)
		problems += self.month_consistency(runs)
		problems += self.chronological_sections(runs)

		problems += self.fonts(rtf)
		problems += self.colours(rtf)
		problems += self.font_sizes(rtf)

		return problems

	def fonts(self, rtf):
		fonts = re.findall(r"\\fcharset0 (\w+)", rtf)
		# some fonts are just for bulles
		font_usages = set([int(x) for x in re.findall(r"\\f(\d+).+?\w{5}\\?$", rtf, re.MULTILINE)])
		actually_used_fonts = []
		for idx, font in enumerate(fonts):
			if idx in font_usages:
				actually_used_fonts.append(font)

		# 1 header + 1 body
		if len(actually_used_fonts) > 2:
			return [ProblemArea(ProblemType.TooManyFonts, 0, snippets=[Snippet(x, style="font-family: %s;" % x) for x in actually_used_fonts])]
		return []

	def colours(self, rtf):
		colours = re.findall(r"\\red(\d{1,3})\\green(\d{1,3})\\blue(\d{1,3})", rtf)
		# white, black, background, fg-1, fg-2
		# so, 5
		if len(colours) > 5:
			# HAXX
			snippets = [Snippet("&nbsp", style="background-color:rgb(%s, %s, %s)" % x, cssclass="swatch") for x in colours]
			return [ProblemArea(ProblemType.TooManyColours, 0, snippets=snippets)]
		return []

	def font_sizes(self, rtf):
		sizes = set(re.findall(r"\\fs(\d+).+?\w{5}\\?$", rtf, re.MULTILINE))
		# header, subheader, body
		if len(sizes) > 3:
			snippets = [Snippet("Size %s" % x, style="font-size: %spx;" % x) for x in sorted(sizes)]
			return [ProblemArea(ProblemType.TooManyFontSizes, 0, snippets=snippets)]
		return []

	def student_number(self, runs):
		for run in runs:
			match = re.search(r"\d{8}", run)
			if match:
				return [ProblemArea(ProblemType.StudentNumber,0, snippets=[Snippet(run, (match.start(), match.end()))])]
			return []

	def chronological_sections(self, runs):
		import dateutil.parser
		collection_head = None
		current_min_date = None
		problems = []

		allabbrs = []
		for abbrset in self.month_abbrs:
			allabbrs += abbrset

		for run in runs:
			if run[0] not in self.bullet_pts + self.probably_bullet_pts:
				collection_head = run
				current_min_date = None
			else:
				# find the dates
				unparsed_dates = re.findall("(?:%s) \d{4}" % "|".join(allabbrs), run, re.IGNORECASE)
				parsed_dates = [dateutil.parser.parse(x) for x in unparsed_dates]
				if parsed_dates:
					mindate = min(parsed_dates)
					if current_min_date is None:
						current_min_date = mindate

					if current_min_date < mindate:
						problems.append(ProblemArea(ProblemType.OutOfOrderDates, 0, snippets=[Snippet(collection_head)]))

					current_min_date = min(current_min_date, mindate)

		return problems

	def month_consistency(self, runs):
		selected_abbr_set = None
		offending_matches = {}
		problems = []
		for run in runs:
			using_abbr_sets = []
			for idx, abbrset in enumerate(self.month_abbrs):

				match = re.search("|".join([x + "\s" for x in abbrset]), run, re.IGNORECASE)
				if match:
					offending_matches[idx] = match
					using_abbr_sets.append(abbrset)


			if using_abbr_sets and selected_abbr_set is None:
				selected_abbr_set = using_abbr_sets[0]

			for abbrset in using_abbr_sets:
				if abbrset != selected_abbr_set:
					snippets = [Snippet(run, (offending_matches[self.month_abbrs.index(abbrset)].start(), offending_matches[self.month_abbrs.index(abbrset)].end()))]
					problems.append(ProblemArea(ProblemType.InconsistentMonths, 0, snippets=snippets))

		return problems


	def bullet_consistency(self, runs):
		used_bullet_types = set()
		exemplar_line = None
		problems = []
		line_ending_with_period = None
		for run in runs:
			if len(run) < 5:
				continue
			if run[0] in self.bullet_pts + self.probably_bullet_pts:
				if len(used_bullet_types):
					if run[0] not in used_bullet_types:
						snippets = [Snippet(run, (0, 1))]
						if len(used_bullet_types) == 1:
							snippets.append(Snippet(exemplar_line, (0, 1)))
						problems.append(ProblemArea(ProblemType.InconsistentBullets, None, snippets=snippets))
				if line_ending_with_period is not None:
					if (run[-1] == ".") ^ line_ending_with_period:
						problems.append(ProblemArea(ProblemType.InconsistentBulletEndings, None, snippets=[Snippet(run, (len(run)-1, len(run)))]))
				else:
					line_ending_with_period = run[-1] == "."
				used_bullet_types.add(run[0])
				exemplar_line = run
		return problems

	def verbs(self, runs):
		verbs = []
		verb_runs = []
		problems = []
		for run in runs:
			for widx, word in enumerate(run.split(" ")):
				oword = word
				word = word.lower()
				if re.match("(.+ed|%s)$" % "|".join(self.blacklisted_verbs), word):
					lastocc = None
					lastoccrun = None
					for idx, verb in enumerate(verbs):
						if verb == word:
							lastocc = idx
							lastoccrun = verb_runs[idx]
					if lastocc and len(verbs) - lastocc < 2:
						snippets = [
							Snippet(run, (run.index(oword), run.index(oword) + len(word))),
							Snippet(lastoccrun, (lastoccrun.lower().index(oword.lower()), lastoccrun.lower().index(oword.lower()) + len(word)))
						]
						problems.append(ProblemArea(ProblemType.ReusedVerbs, None, snippets=snippets))
					verbs.append(word)
					verb_runs.append(run)

					# These verbs are legitimate inside sentences
					if word in self.blacklisted_verbs and widx in [0, 1]:
						problems.append(ProblemArea(ProblemType.BoringVerbs, None, snippets=[Snippet(run, (run.index(oword), run.index(oword) + len(word)))]))

		return problems

	def buzzphrases(self, runs):
		problems = []
		# Kick out when a run contains too many buzzphrases (and isn't in a list of technologies)
		max_frac = 0.25
		min_words = 5
		for run in runs:
			wordct = len(run.split(" "))
			buzzct = len(re.findall("|".join(self.flagged_buzzphrases), run, re.IGNORECASE))
			if buzzct / wordct > max_frac and wordct >= min_words:
				offenders = re.finditer("|".join(self.flagged_buzzphrases), run, re.IGNORECASE)
				snippets = []
				for offender in offenders:
					snippets.append(Snippet(run, (offender.start(), offender.end())))
				problems.append(ProblemArea(ProblemType.Buzzwords, None, snippets=snippets))

		return problems
