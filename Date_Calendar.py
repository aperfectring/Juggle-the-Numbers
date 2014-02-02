
import gtk
import datetime

class Date_Calendar:
	def __init__(self, parent):
		self.parent = parent
		self.label = gtk.Label("Date:")
		self.parent.date_vbox.pack_start(self.label, expand=False)

		self.calendar = gtk.Calendar()
		self.parent.date_vbox.pack_start(self.calendar, expand=False)
		self.calendar.select_month(datetime.date.today().month-1, datetime.date.today().year)
		self.calendar.select_day(datetime.date.today().day)

		self.calendar.connect('day-selected', self.repop)

	def get_date(self):
		(year, month, day) = self.calendar.get_date()
		return datetime.date(year, month+1, day).isoformat()
		
	def repop(self, calendar):
		self.parent.games_note.repop()
