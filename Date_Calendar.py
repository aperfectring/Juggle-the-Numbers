
import gtk
import datetime

class Date_Calendar:
	def __init__(self, parent_box, label_txt = None):
		self.parent_box = parent_box
		self.callback_list = []

		if label_txt == None:
			label_txt = "Date:"
		self.label = gtk.Label(label_txt)
		self.parent_box.pack_start(self.label, expand=False)

		self.calendar = gtk.Calendar()
		self.parent_box.pack_start(self.calendar, expand=False)
		self.calendar.select_month(datetime.date.today().month-1, datetime.date.today().year)
		self.calendar.select_day(datetime.date.today().day)

		self.calendar.connect('day-selected', self.repop)

	### Register with the class for callbacks on updates
	def register(self, callback):
		self.callback_list.append(callback)

	def get_date(self):
		(year, month, day) = self.calendar.get_date()
		return datetime.date(year, month+1, day).isoformat()
		
	def repop(self, calendar):
		map(lambda x: x(), self.callback_list)
