# Indian Number Reader (lakh/crore) - NVDA global plugin
# Copyright (C) 2026 Mukesh Jain, VisionAccess
# This file is covered by the GNU General Public License version 2.

import addonHandler
import api
import config
import globalPluginHandler
import gui
import scriptHandler
import speech
import textInfos
import ui
import wx
from gui import guiHelper, nvdaControls
from gui.settingsDialogs import NVDASettingsDialog, SettingsPanel
from logHandler import log
from scriptHandler import script

from . import numconv

try:
	addonHandler.initTranslation()
except Exception:
	pass
try:
	_
except NameError:
	def _(s):
		return s

try:
	from speech.extensions import filter_speechSequence
except Exception:
	filter_speechSequence = None

SECTION = "indianNumberReader"
config.conf.spec[SECTION] = {
	"autoRead": "boolean(default=True)",
	"convertPlain": "boolean(default=True)",
	"minPlainDigits": "integer(default=7, min=6, max=15)",
	"maxPlainDigits": "integer(default=9, min=6, max=15)",
}


def _conf():
	return config.conf[SECTION]


def convertAuto(text):
	c = _conf()
	return numconv.convertText(
		text,
		convertPlain=c["convertPlain"],
		minPlainDigits=c["minPlainDigits"],
		maxPlainDigits=c["maxPlainDigits"],
	)


def convertOnDemand(text, style="words"):
	# The user asked explicitly, so be generous with plain numbers.
	return numconv.convertText(text, convertPlain=True, minPlainDigits=6, maxPlainDigits=15, style=style)


def _filterSpeech(speechSequence, *args, **kwargs):
	try:
		if not _conf()["autoRead"]:
			return speechSequence
		return [convertAuto(item) if isinstance(item, str) else item for item in speechSequence]
	except Exception:
		log.debugWarning("Indian Number Reader: speech filter failed", exc_info=True)
		return speechSequence


class IndianNumberReaderPanel(SettingsPanel):
	# Translators: title of the settings panel
	title = _("Indian Number Reader")

	def makeSettings(self, settingsSizer):
		c = _conf()
		helper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		self.autoCheck = helper.addItem(
			wx.CheckBox(self, label=_("&Automatically read numbers in lakh and crore in all applications"))
		)
		self.autoCheck.SetValue(c["autoRead"])
		self.plainCheck = helper.addItem(
			wx.CheckBox(self, label=_("Also convert numbers written &without commas (for example 1500000)"))
		)
		self.plainCheck.SetValue(c["convertPlain"])
		self.minSpin = helper.addLabeledControl(
			_("Mi&nimum digits for numbers without commas:"),
			nvdaControls.SelectOnFocusSpinCtrl,
			min=6, max=15, initial=c["minPlainDigits"],
		)
		self.maxSpin = helper.addLabeledControl(
			_("Ma&ximum digits for numbers without commas:"),
			nvdaControls.SelectOnFocusSpinCtrl,
			min=6, max=15, initial=c["maxPlainDigits"],
		)

	def onSave(self):
		c = _conf()
		c["autoRead"] = self.autoCheck.GetValue()
		c["convertPlain"] = self.plainCheck.GetValue()
		lo, hi = self.minSpin.GetValue(), self.maxSpin.GetValue()
		if lo > hi:
			lo, hi = hi, lo
		c["minPlainDigits"] = lo
		c["maxPlainDigits"] = hi


def _selectedText():
	obj = api.getFocusObject()
	ti = getattr(obj, "treeInterceptor", None)
	if ti is not None and getattr(ti, "isReady", False) and not getattr(ti, "passThrough", False):
		obj = ti
	try:
		info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
		if not info.isCollapsed and info.text.strip():
			return info.text
	except Exception:
		pass
	return ""


def _reviewLineText():
	try:
		pos = api.getReviewPosition()
		if pos is None:
			return ""
		info = pos.copy()
		info.expand(textInfos.UNIT_LINE)
		return info.text.strip()
	except Exception:
		return ""


def _navigatorText():
	obj = api.getNavigatorObject()
	if obj is None:
		return ""
	parts = []
	for attr in ("name", "value"):
		try:
			v = getattr(obj, attr, None)
		except Exception:
			v = None
		if v and v not in parts:
			parts.append(v)
	return " ".join(parts).strip()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	# Translators: input gestures category
	scriptCategory = _("Indian Number Reader")

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._patched = None
		if filter_speechSequence is not None:
			filter_speechSequence.register(_filterSpeech)
		else:
			self._patchSpeak()
		NVDASettingsDialog.categoryClasses.append(IndianNumberReaderPanel)

	def _patchSpeak(self):
		# Fallback for NVDA versions without the speech filter extension point.
		import speech.speech as speechModule
		original = speechModule.speak

		def patchedSpeak(speechSequence, *args, **kwargs):
			return original(_filterSpeech(list(speechSequence)), *args, **kwargs)

		speechModule.speak = patchedSpeak
		speech.speak = patchedSpeak
		self._patched = (speechModule, original)

	def terminate(self):
		try:
			if filter_speechSequence is not None:
				filter_speechSequence.unregister(_filterSpeech)
			elif self._patched:
				speechModule, original = self._patched
				speechModule.speak = original
				speech.speak = original
		except Exception:
			log.debugWarning("Indian Number Reader: cleanup failed", exc_info=True)
		try:
			NVDASettingsDialog.categoryClasses.remove(IndianNumberReaderPanel)
		except ValueError:
			pass
		super().terminate()

	def _textToRead(self):
		for getter in (_selectedText, _reviewLineText, _navigatorText):
			text = getter()
			if text and convertOnDemand(text) != text:
				return text
		# Nothing convertible found: return whatever we have.
		return _selectedText() or _reviewLineText() or _navigatorText()

	@script(
		description=_(
			"Reads the selected text, or the current line or cell, with numbers in lakh and crore. "
			"Press twice to copy it to the clipboard with Indian commas (15,00,000)"
		),
		gesture="kb:NVDA+alt+i",
	)
	def script_readIndian(self, gesture):
		text = self._textToRead()
		if not text:
			ui.message(_("No text found"))
			return
		if scriptHandler.getLastScriptRepeatCount() >= 1:
			api.copyToClip(convertOnDemand(text, style="commas"))
			ui.message(_("Copied with Indian commas"))
			return
		ui.message(convertOnDemand(text))

	@script(
		description=_("Turns automatic reading of numbers in lakh and crore on or off"),
		gesture="kb:NVDA+alt+n",
	)
	def script_toggleAuto(self, gesture):
		c = _conf()
		c["autoRead"] = not c["autoRead"]
		if c["autoRead"]:
			ui.message(_("Indian numbers on"))
		else:
			ui.message(_("Indian numbers off"))

	@script(description=_("Opens the Indian Number Reader settings"))
	def script_openSettings(self, gesture):
		wx.CallAfter(gui.mainFrame.popupSettingsDialog, NVDASettingsDialog, IndianNumberReaderPanel)
