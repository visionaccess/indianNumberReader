# Indian Number Reader - number conversion logic
# Copyright (C) 2026 Mukesh Jain, VisionAccess
# This file is covered by the GNU General Public License version 2.
# Pure Python (no NVDA imports) so it can be tested outside NVDA.

import re

LAKH = "lakh"
CRORE = "crore"
POINT = "point"

ONE_LAKH = 100000
ONE_CRORE = 10000000

# A number is either:
#   Indian grouped   e.g. 1,00,000  15,00,000  1,25,30,500
#   Western grouped  e.g. 100,000   1,500,000  12,345,678
#   Plain digits     e.g. 1500000
# optionally followed by a decimal part.
# It must not be glued to letters/underscores/digits/commas on either side,
# so IDs like INV1500000 or CSV runs are left alone.
_NUMBER_RE = re.compile(
	r"(?<![\w,])(?<!\d\.)"
	r"(?P<int>\d{1,2}(?:,\d{2})+,\d{3}|\d{1,3}(?:,\d{3})+|\d+)"
	r"(?:\.(?P<dec>\d+))?"
	r"(?!\w)(?![.,]\d)"
)


def indianWords(n):
	"""Return n spoken in the Indian system using digits plus lakh/crore.
	e.g. 1523456 -> '15 lakh 23456' (a synthesizer reads 23456 as
	'twenty three thousand four hundred fifty six').
	"""
	if n < ONE_LAKH:
		return str(n)
	parts = []
	crore, rest = divmod(n, ONE_CRORE)
	if crore:
		# 500000 crore -> '5 lakh crore'
		parts.append(indianWords(crore))
		parts.append(CRORE)
	lakh, rest = divmod(rest, ONE_LAKH)
	if lakh:
		parts.append(str(lakh))
		parts.append(LAKH)
	if rest:
		parts.append(str(rest))
	return " ".join(parts)


def indianGrouping(n):
	"""Return n written with Indian commas, e.g. 1523456 -> '15,23,456'."""
	s = str(n)
	if len(s) <= 3:
		return s
	head, last3 = s[:-3], s[-3:]
	groups = []
	while len(head) > 2:
		groups.insert(0, head[-2:])
		head = head[:-2]
	if head:
		groups.insert(0, head)
	return ",".join(groups) + "," + last3


def convertText(text, convertPlain=True, minPlainDigits=7, maxPlainDigits=9, style="words"):
	"""Rewrite every number of one lakh or more found in text.
	style='words'  -> '15 lakh 23456 point 5 0'
	style='commas' -> '15,23,456.50'
	Numbers without commas are only touched when convertPlain is True and
	they have between minPlainDigits and maxPlainDigits digits, so phone
	numbers, PIN codes, OTPs and account numbers are not mangled.
	"""
	if not text or not any(ch.isdigit() for ch in text):
		return text

	def repl(m):
		raw = m.group("int")
		dec = m.group("dec")
		digits = raw.replace(",", "")
		if "," not in raw:
			if (
				not convertPlain
				or len(digits) < minPlainDigits
				or len(digits) > maxPlainDigits
				or (len(digits) > 1 and digits.startswith("0"))
			):
				return m.group(0)
		n = int(digits)
		if n < ONE_LAKH:
			return m.group(0)
		if style == "commas":
			out = indianGrouping(n)
			if dec:
				out += "." + dec
			return out
		out = indianWords(n)
		if dec:
			out += " %s %s" % (POINT, " ".join(dec))
		return out

	return _NUMBER_RE.sub(repl, text)
