#  MythBox for XBMC - http://mythbox.googlecode.com
#  Copyright (C) 2009 analogue@yahoo.com
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

import os
import xbmcgui

from myGBPVRGlobals import *
from fanart import fanart
# =============================================================================            
class DetailDialog(xbmcgui.WindowXMLDialog):
	"""
	Show details of show, recording and recurring recording
	"""

	def __init__(self, *args, **kwargs):
		# Need to get: oid and gbpvr....
		self.settings = kwargs['settings']
		self.gbpvr = kwargs['gbpvr']
		
		self.oid = kwargs['oid']
		self.oid_type = kwargs['type']
		if kwargs.has_key('epg') == True:
			self.epg = True
		else:
			self.epg = False
		self.returnvalue = None
		
		self.win = None        
		self.shouldRefresh = False
		self.fanart = fanart()
		print self
		print repr(self)
        
	def onInit(self):
		self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())        
		self.showImage = self.getControl(302)
		self.channelImage = self.getControl(305)
		self.genre1Image = self.getControl(306)
		self.genre2Image = self.getControl(307)
		self.genre3Image = self.getControl(308)
		self.statusLabel = self.getControl(309)
		
		self.subtitleLabel = self.getControl(310)
		self.timeLabel = self.getControl(311)
		self.descLabel = self.getControl(312)
		self.showSeperator = self.getControl(4)
		
		self.placeFiller = self.getControl(7777)
		
		self.scheduleType = self.getControl(201)
		self.prePadding = self.getControl(202)
		self.postPadding = self.getControl(203)
		self.recDirId = self.getControl(204)
		self.extendTime = self.getControl(205)
		self.timeSlot = self.getControl(206)
		self.keepRecs = self.getControl(207)
		self.priority = self.getControl(208)
		self.priority.setVisible(False)
		self.qualityControl = self.getControl(205)
		self.saveButton = self.getControl(250)
		self.deleteButton = self.getControl(251)
		self.recordButton = self.getControl(252)
		self.closeButton = self.getControl(253)
		self.playButton = self.getControl(254)
		self.playButton.setVisible(False)
				
		self._getDetails()
		self._updateView()
    
	def onFocus(self, controlId):
		pass
        
	def onAction(self, action):
		if action.getId() in (EXIT_SCRIPT):
			self.close() 

	def goRecord(self):
		#self.detailData['rectype'] = 'Once'
		self.detailData['status'] = "Pending"
		self.detailData['recquality'] = "High"
		self.detailData['prepadding'] = "2"
		self.detailData['postpadding'] = "1"
		self.detailData['rectype'] = "Record Once"
		self.detailData['maxrecs'] = "0"
		self.detailData['recording_oid'] = 0
		self.detailData['directory'] = "Default"
		self._updateView()

	def error_message(self):
		dialog = xbmcgui.Dialog()
		dialog.ok("Sorry", "An error occurred!")

	def onClick(self, controlId):
		source = self.getControl(controlId)
		if self.closeButton == source:
			self.close()
		elif self.recordButton == source:
			self.goRecord()
		elif self.saveButton == source:
			if self.gbpvr.AreYouThere(self.settings.usewol(), self.settings.GBPVR_MAC, self.settings.GBPVR_BROADCAST):
				try:
					if self.detailData['recording_oid'] == 0:
						if self.gbpvr.scheduleRecording(self.settings.GBPVR_USER, self.settings.GBPVR_PW, self.detailData):
							self.returnvalue = "REC"
							self.close("REC")
						else:
							self.error_message()
					else:
						if self.gbpvr.updateRecording(self.settings.GBPVR_USER, self.settings.GBPVR_PW, self.detailData):
							self.returnvalue = "REC"
							self.close("REC")
						else:
							self.error_message()
							
				except:
					xbmcgui.Dialog().ok('Sorry', 'An error occurred!')
		elif self.deleteButton == source:
			if self.gbpvr.AreYouThere(self.settings.usewol(), self.settings.GBPVR_MAC, self.settings.GBPVR_BROADCAST):
					try:
							if self.gbpvr.cancelRecording(self.settings.GBPVR_USER, self.settings.GBPVR_PW, self.detailData):
									self.returnvalue = "DEL"
									self.close("DEL")
							else:
									self.error_message()
					except:
							xbmcgui.Dialog().ok('Sorry', 'An error occurred!')
			else:
					xbmcgui.Dialog().ok('Sorry', 'Something went wrong!!')
		elif self.scheduleType == source:
			self.detailData['rectype']
			if self.detailData['recording_oid'] == 0: # Only for new recording
					self.detailData['rectype'] = self._pickFromList("Select recording type", ["Record Once",
                    "Record Season (NEW episodes on this channel)",
                    "Record Season (All episodes on this channel)",
                    "Record Season (Daily, this timeslot)",
                    "Record Season (Weekly, this timeslot)",
                    "Record Season (Monday-Friday, this timeslot)",
                    "Record Season (Weekends, this timeslot)",
                    "Record All Episodes, All Channels"], self.detailData['rectype'])
					self._updateView()
		elif self.qualityControl == source:
			self.detailData['recquality'] = self._pickFromList("Select recording quality", ["Best", "Better", "Best", "Default"], self.detailData['recquality'])
			self._updateView()
		elif self.prePadding == source:
			self.detailData['prepadding'] = str(self._getNumber("Select prepadding minutes", self.detailData['prepadding'], 0, 30))
			self._updateView()
		elif self.postPadding == source:
			self.detailData['postpadding'] = str(self._getNumber("Select postpadding minutes", self.detailData['postpadding'], 0, 30))
			self._updateView()
		elif self.extendTime == source:
			self.detailData['extendend'] = str(self._getNumber("Select time extenstion (minutes)", 0, 0, 30))
			self._updateView()
		elif self.keepRecs == source:
			self.detailData['maxrecs'] = str(self._getNumber("Select recordings to keep (0 means all)", self.detailData['maxrecs'], 0, 30))
			self._updateView()
		elif self.recDirId == source:
			self.detailData['directory'] = self._pickFromList("Recording Directory", self.gbpvr.RecDirs, self.detailData['directory'])
			self._updateView()
		elif self.playButton == source:
			import xbmcgui,xbmc
			self.urly = self.gbpvr.getURL()
			if self.detailData.has_key('filename') == False:
				self.channelIcon = self.fanart.getChannelIcon(self.detailData['channel'][0])
				if self.channelIcon is not None:
					listitem = xbmcgui.ListItem(self.detailData["title"],  thumbnailImage=self.channelIcon)
					infolabels={ "Title": self.detailData['title']  }
					listitem.setInfo( type="Video", infoLabels=infolabels )
				else:
					listitem = xbmcgui.ListItem(self.detailData['title'])				
				url = self.urly + "/live?channel=" + self.detailData['channel'][1]
			else:
				listitem = xbmcgui.ListItem(self.detailData['title'],"")
				infolabels={ "Title": self.detailData['title'] , 'plot': self.detailData['desc'] }
				listitem.setInfo( type="Video", infoLabels=infolabels )
				import os.path
				if os.path.isfile(self.detailData['filename']):
					url = self.detailData['filename']
				else:
					url = self.urly + "/live?recording=" + str(self.detailData['recording_oid'])

			print "Playing " + url
			xbmc.Player( xbmc.PLAYER_CORE_MPLAYER ).play(url, listitem)
			self.close();

	def _getDetails(self):
		self.win.setProperty('busy', 'true')
		if self.gbpvr.AreYouThere(self.settings.usewol(), self.settings.GBPVR_MAC, self.settings.GBPVR_BROADCAST):
			self.detailData = self.gbpvr.getDetails(self.settings.GBPVR_USER, self.settings.GBPVR_PW, self.oid, self.oid_type)
		else:
			self.win.setProperty('busy', 'false')
			xbmcgui.Dialog().ok('Sorry', 'Unable to contact GBPVR server!!')
			self.close()
		self.win.setProperty('busy', 'false')

	def _updateView(self):        
		self.win.setProperty('busy', 'true')
		
		self.win.setProperty('title', self.detailData['title'])
		self.win.setProperty('channel', self.detailData['channel'][0])
		self.win.setProperty('genre', str(self.detailData['genres']))
		
		self.channelIcon = self.fanart.getChannelIcon(self.detailData['channel'][0])
		if self.channelIcon is not None:
			self.channelImage.setImage(self.channelIcon)
		
		if self.epg == True:
			from datetime import datetime
			if datetime.now() >= self.detailData['start'] and datetime.now() < self.detailData['end']:
				self.playButton.setVisible(True)
				self.playButton.setLabel("Watch")
		elif self.detailData.has_key('filename') == False:
			self.playButton.setVisible(False)
		else:
			self.playButton.setVisible(True)
		
		self.showIcon = self.fanart.getShowIcon(self.detailData['title'])
		if self.showIcon is not None:
			self.showImage.setImage(self.showIcon)
		
		if len(self.detailData['genres']) > 0:
			self.genreIcon = self.fanart.getGenreIcon(self.detailData['genres'][0])
			if self.genreIcon is not None:
				self.genre1Image.setImage(self.genreIcon)
		
		if len(self.detailData['genres']) > 1:
			self.genreIcon = self.fanart.getGenreIcon(self.detailData['genres'][1])
			if self.genreIcon is not None:
				self.genre2Image.setImage(self.genreIcon)
		
		if len(self.detailData['genres']) > 2:
			self.genreIcon = self.fanart.getGenreIcon(self.detailData['genres'][2])
			if self.genreIcon is not None:
				self.genre3Image.setImage(self.genreIcon)
		
		self.statusLabel.setVisible(True)
		self.statusLabel.setLabel(self.detailData['status'])
		if self.detailData['rectype'] !="" and self.detailData['rectype'] != 'Record Once' and self.detailData['rectype'] != "Single"  and self.detailData['status'] != "Completed" and self.detailData['status'] != "In-Progress":
			self.win.setProperty('heading', 'Recurring Recording Properties')
			self.subtitleLabel.setVisible(False)
			self.timeLabel.setVisible(False)
			self.descLabel.setVisible(False)
			self.showSeperator.setVisible(False)
			self.extendTime.setVisible(False)
		
			self.qualityControl.setLabel( "Quality:", label2=self.detailData['recquality'] )
			self.qualityControl.setVisible(True)
			self.prePadding.setLabel( "Pre-Padding (min.):", label2=self.detailData['prepadding'] )
			self.prePadding.setVisible(True)
			self.postPadding.setLabel( "Post-Padding (min.):", label2=self.detailData['postpadding'] )
			self.postPadding.setVisible(True)
			self.scheduleType.setLabel( "Schedule Type:", label2=self.detailData['rectype'] )
			self.scheduleType.setVisible(True)
			#self.timeSlot.setLabel( "Timeslot:", label2=str(self.detailData['recdate']) )
			self.timeSlot.setVisible(False)
			self.keepRecs.setLabel( "Recordings to Keep:", label2=str(self.detailData['maxrecs']) )
			self.keepRecs.setVisible(True)
			self.recDirId.setLabel( "Directory:", label2=str(self.detailData['directory']) )
			self.recDirId.setVisible(True)
			
			self.placeFiller.setVisible(False)
			
			self.recordButton.setVisible(False)
			self.saveButton.setVisible(True)
			if self.detailData['recording_oid'] > 0:
				self.deleteButton.setVisible(True)
			else:
				self.deleteButton.setVisible(False)

			self.closeButton.setVisible(True)			
			xbmcgui.WindowXML.setFocus(self, self.scheduleType)
		
		elif (self.detailData['rectype'] == 'Record Once' or self.detailData['rectype'] == 'Single')  and self.detailData['status'] != "Completed" and self.detailData['status'] != "In-Progress":
			self.win.setProperty('heading', 'Recording Properties')
			
			self.subtitleLabel.setVisible(True)
			self.subtitleLabel.setLabel(self.detailData['subtitle'])
			self.timeLabel.setVisible(True)
			ctmp = self.detailData['start'].strftime('%a, %b %d %H:%M') + " - " + self.detailData['end'].strftime('%H:%M')
			ctmp = ctmp + " (" + str(int((self.detailData['end'] - self.detailData['start']).seconds / 60)) + " min.)"
			self.timeLabel.setLabel(ctmp)
			self.descLabel.setVisible(True)
			self.descLabel.setText(self.detailData['desc'])
			self.showSeperator.setVisible(True)
			if (self.detailData['status'] == "Pending"):
				if self.detailData['status'] == "In-Progress":
					self.extendTime.setLabel( "Extend End-Time:", label2='Unknown' )
					self.extendTime.setVisible(True)
				else:
					self.extendTime.setVisible(False)
					self.scheduleType.setLabel( "Schedule Type:", label2=self.detailData['rectype'] )
					self.scheduleType.setVisible(True)
					self.prePadding.setLabel( "Pre-Padding (min.):", label2=self.detailData['prepadding'] )
					self.prePadding.setVisible(True)
					self.postPadding.setLabel( "Post-Padding (min.):", label2=self.detailData['postpadding'] )
					self.postPadding.setVisible(True)
					self.recDirId.setLabel( "Directory:", label2=str(self.detailData['directory']) )
					self.recDirId.setVisible(True)
					self.qualityControl.setLabel( "Quality:", label2=self.detailData['recquality'] )
					self.qualityControl.setVisible(True)
					self.saveButton.setVisible(True)		
			else:
				self.extendTime.setVisible(False)
				self.qualityControl.setVisible(False)
				self.prePadding.setVisible(False)
				self.postPadding.setVisible(False)
				self.saveButton.setVisible(False)
				self.scheduleType.setVisible(False)
			
			self.timeSlot.setVisible(False)
			self.keepRecs.setVisible(False)
			
			#self.placeFiller.setVisible(True)
			
			self.recordButton.setVisible(False)
			if self.detailData['recording_oid'] > 0:
				self.deleteButton.setVisible(True)
			else:
				self.deleteButton.setVisible(False)
			
			self.closeButton.setVisible(True)

			if self.detailData['recording_oid'] > 0:
				xbmcgui.WindowXML.setFocus(self, self.closeButton)
			else:
				xbmcgui.WindowXML.setFocus(self, self.scheduleType)
		else:
			self.win.setProperty('heading', 'Program Details')
			self.subtitleLabel.setVisible(True)
			self.subtitleLabel.setLabel(self.detailData['subtitle'])
			self.timeLabel.setVisible(True)
			ctmp = self.detailData['start'].strftime('%a, %b %d %H:%M') + " - " + self.detailData['end'].strftime('%H:%M')
			ctmp = ctmp + " (" + str(int((self.detailData['end'] - self.detailData['start']).seconds / 60)) + " min.)"
			self.timeLabel.setLabel(ctmp)
			self.descLabel.setHeight(220)
			self.descLabel.setVisible(True)
			self.descLabel.setText(self.detailData['desc'])
			x, y = self.showSeperator.getPosition()
			self.showSeperator.setPosition(x, y+220)
			self.showSeperator.setVisible(True)
			
			self.qualityControl.setVisible(False)
			self.prePadding.setVisible(False)
			self.postPadding.setVisible(False)
			self.extendTime.setVisible(False)
			self.scheduleType.setVisible(False)
			self.timeSlot.setVisible(False)
			self.keepRecs.setVisible(False)
			self.recDirId.setVisible(False)
			
			self.placeFiller.setVisible(True)
			if self.detailData['status'] != "Completed" and self.detailData['status'] != "In-Progress":
				self.recordButton.setVisible(True)
				self.deleteButton.setVisible(False)
			else:
				self.recordButton.setVisible(False)
				self.deleteButton.setVisible(True)
			self.saveButton.setVisible(False)
			self.closeButton.setVisible(True)

			xbmcgui.WindowXML.setFocus(self, self.closeButton)
		self.win.setProperty('busy', 'false')

	def _pickFromList(self, title, choices, current):
		selected = xbmcgui.Dialog().select(title, choices)
		if selected >= 0:
			return choices[selected]
		else:
			return current;
            
	def _getNumber(self, heading, current, min=None, max=None):
		value = xbmcgui.Dialog().numeric(0, heading, str(current))
		if value == str(current):
			return current
		
		result = int(value)
		
		if min is not None and result < min:
			xbmcgui.Dialog().ok('Error', 'Value must be between %d and %d' % (min, max))
			result = current
			
		if max is not None and result > max:
			xbmcgui.Dialog().ok('Error', 'Value must be between %d and %d' % (min, max))
			result = current
			
		return result             
