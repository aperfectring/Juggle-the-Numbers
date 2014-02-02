
import gtk
import re

class Season_Notebook:
	def __init__(self, parent_box, JTN_db, get_season_id):
		self.parent_box = parent_box
		self.JTN_db = JTN_db
		self.get_season_id = get_season_id
		self.callback_list = []

		self.start_hbox = gtk.HBox(spacing=10)
		self.start_hbox.set_border_width(5)
		self.parent_box.add(self.start_hbox)

		self.start_label = gtk.Label("Start Date:")
		self.start_hbox.add(self.start_label)

		self.start_cal = gtk.Calendar()
		self.start_hbox.add(self.start_cal)

		self.end_hbox = gtk.HBox(spacing=10)
		self.end_hbox.set_border_width(5)
		self.parent_box.add(self.end_hbox)

		self.end_label = gtk.Label("End Date:")
		self.end_hbox.add(self.end_label)

		self.end_cal = gtk.Calendar()
		self.end_hbox.add(self.end_cal)

		self.update_button = gtk.Button("Update")
		self.parent_box.pack_start(self.update_button, expand=False)
		self.update_button.connect('clicked', self.update)

	### Register with the class for callbacks on updates
	def register(self, callback):
		self.callback_list.append(callback)


	### Callback for the "Update" button on the season notebook page
	###    This writes the currently selected dates into the database, and updates the combobox with the
	###    appropriate date range.
	def update(self, button):
		season_id = self.get_season_id()
		start_date = self.start_cal.get_date()
		end_date = self.end_cal.get_date()
		start_date_str = str(start_date[0]) + "-" + str(start_date[1]+1).zfill(2) + "-" + str(start_date[2]).zfill(2)
		end_date_str =   str(end_date[0]) + "-" + str(end_date[1]+1).zfill(2) + "-" + str(end_date[2]).zfill(2) 

		self.JTN_db.set_season(season_id, start_date_str, end_date_str)

		if(start_date[0] == end_date[0]):
			new_name = str(start_date[0])
		else:
			new_name = str(start_date[0]) + "-" + str(end_date[0])

		for callback in self.callback_list:
			callback(new_name)


	### Update the start date calendar with the appropriate year, month, and day
	def set_start(self, year = None, month = None, day = None):
		if (month != None) and (year != None):
			self.start_cal.select_month(int(month)-1, int(year))
			if(day != None):
				self.start_cal.select_day(int(day))

	### Update the end date calendar with the appropriate year, month, and day
	def set_end(self, year = None, month = None, day = None):
		if (month != None) and (year != None):
			self.end_cal.select_month(int(month)-1, int(year))
			if(day != None):
				self.end_cal.select_day(int(day))

	def repop(self):
		season_id = self.get_season_id()

		### Decode the starting year month and day from the season entry in the database		
		row = self.JTN_db.get_season(season_id = season_id)
		if(row[0] != None):
			start_date = re.split('-', row[0])
			self.set_start(year = start_date[0], month = start_date[1], day = start_date[2])

		if(row[1] != None):
			end_date = re.split('-', row[1])
			self.set_end(year = end_date[0], month = end_date[1], day = end_date[2])


