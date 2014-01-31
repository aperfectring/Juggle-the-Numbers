
import gtk

class Season_Notebook:
	def __init__(self, parent):
		self.parent = parent

		self.start_hbox = gtk.HBox(spacing=10)
		self.start_hbox.set_border_width(5)
		self.parent.season_note_vbox.add(self.start_hbox)

		self.start_label = gtk.Label("Start Date:")
		self.start_hbox.add(self.start_label)

		self.start_cal = gtk.Calendar()
		self.start_hbox.add(self.start_cal)

		self.end_hbox = gtk.HBox(spacing=10)
		self.end_hbox.set_border_width(5)
		self.parent.season_note_vbox.add(self.end_hbox)

		self.end_label = gtk.Label("End Date:")
		self.end_hbox.add(self.end_label)

		self.end_cal = gtk.Calendar()
		self.end_hbox.add(self.end_cal)

		self.update_button = gtk.Button("Update")
		self.parent.season_note_vbox.pack_start(self.update_button, expand=False)
		self.update_button.connect('clicked', self.update)


	### Callback for the "Update" button on the season notebook page
	###    This writes the currently selected dates into the database, and updates the combobox with the
	###    appropriate date range.
	def update(self, button):
		season_id = self.parent.season_combo.get_id()
		start_date = self.start_cal.get_date()
		end_date = self.end_cal.get_date()
		self.parent.cur.execute("UPDATE seasons SET " + 
                                           "start = DATE('" + 
                                              str(start_date[0]) + "-" + 
                                              str(start_date[1]+1).zfill(2) + "-" + 
                                              str(start_date[2]).zfill(2) + "'), " + 
                                           "end = DATE('" + 
                                              str(end_date[0]) + "-" + 
                                              str(end_date[1]+1).zfill(2) + "-" + 
                                              str(end_date[2]).zfill(2) + "') " + 
                                           "WHERE id = '" + str(season_id) + "'")
		self.parent.db.commit()

		if(start_date[0] == end_date[0]):
			new_name = str(start_date[0])
		else:
			new_name = str(start_date[0]) + "-" + str(end_date[0])

		self.parent.season_combo.repop(new_name)


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
		season_id = self.parent.season_combo.get_id()

		### Decode the starting year month and day from the season entry in the database		
		self.parent.cur.execute("SELECT STRFTIME('%Y',start), STRFTIME('%m',start), STRFTIME('%d',start) " + 
                                           "FROM seasons WHERE id = '" + str(season_id) + "'")
		for row in self.parent.cur:
			if row != None:
				self.set_start(year = row[0], month = row[1], day = row[2])

		### Decode the ending year month and day from the season entry in the database		
		self.parent.cur.execute("SELECT STRFTIME('%Y',end), STRFTIME('%m',end), STRFTIME('%d',end) " + 
                                           "FROM seasons WHERE id = '" + str(season_id) + "'")
		for row in self.parent.cur:
			if row != None:
				self.set_end(year = row[0], month = row[1], day = row[2])


