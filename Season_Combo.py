
import gtk
import re

class Season_Combo:
	def __init__(self, parent_box, db_cursor, db_handle, get_league_id):
		self.parent_box = parent_box
		self.db_cursor = db_cursor
		self.db_handle = db_handle
		self.callback_list = []
		self.get_league_id = get_league_id

		self.label = gtk.Label("Season:")
		self.parent_box.pack_start(self.label, expand=False)

		self.combo = gtk.combo_box_new_text()
		self.parent_box.pack_start(self.combo, expand=False)
		self.combo_changed_id = self.combo.connect('changed', self.update)

		self.button = gtk.Button("Add Season")
		self.parent_box.pack_start(self.button, expand=False)
		self.button.connect('clicked', self.add)

	### Register with the class for callbacks on updates
	def register(self, callback):
		self.callback_list.append(callback)

	### Callback handler for when the season combobox changes
	###   Updates the season notebook page
	def update(self, combobox):
		for callback in self.callback_list:
			callback()



	### Callback for when the "Add season" button is clicked"
	###    This will create a "blank" season, which has no start or end date
	###    This will leave the created season as the selected one
	def add(self, button):
		league_id = self.get_league_id()
		self.db_cursor.execute("INSERT INTO seasons (league) VALUES ('" + str(league_id) + "')")
		self.db_handle.commit()
		self.repop('')

	### Determine the Season Unique database ID based on the currently selected season from the combobox	
	def get_id(self):
		model = self.combo.get_model()
		index = self.combo.get_active()
		if index < 0:
			return None
		season_text = model[index][0]
		season_start = None
		season_end = None

		### Since seasons are named based on start-end, the names are only unique within a season
		###   so we need to limit our search within the currently selected season.
		league_id = self.get_league_id()

		### Figure out the starting and ending year of the season
		if(season_text != ''):
			seasons = re.split('-', season_text)
			season_start = seasons[0]
			if(len(seasons) > 1):
				season_end = seasons[1]
		if(season_end == None):
			season_end = season_start

		### Query the database to get the ID
		if(season_start != None):
			self.db_cursor.execute("SELECT id FROM seasons " + 
                                                   "WHERE STRFTIME('%Y',end) = '" + season_end + "' " + 
                                                   "AND STRFTIME('%Y',start) = '" + season_start + "' " + 
                                                   "AND league = '" + str(league_id) + "'")
		else:
			self.db_cursor.execute("SELECT id FROM seasons WHERE end IS NULL AND start IS NULL")

		for row in self.db_cursor:
			if row != None and row[0] != None:
				return row[0]
			else:
				return None

	### Deletes all season combobox entries, then repopulates the combobox with appriopriate ones for this season
	###   Will attempt to select an entry which has the value of select_val, if specified
	def repop(self, select_val = None):
		self.combo.disconnect(self.combo_changed_id)
		league_id = self.get_league_id()
		model = self.combo.get_model()
		for index in range(0, len(model)):
			self.combo.remove_text(0)

		self.db_cursor.execute("SELECT STRFTIME('%Y', start), STRFTIME('%Y', end) " + 
                                           "FROM seasons " + 
                                           "WHERE league = '" + str(league_id) + "' " + 
                                           "ORDER BY end DESC")
		for row in self.db_cursor:
			if row != None and row[0] != None and row[1] != None:
				if row[0] == row[1]:
					self.combo.append_text(row[0])
				else:
					self.combo.append_text(row[0] + "-" + row[1])
			elif row != None:
				self.combo.append_text("")
		model = self.combo.get_model()
		self.combo_changed_id = self.combo.connect('changed', self.update)
		if select_val != None:
			for index in range(0, len(model)):
				if model[index][0] == select_val:
					self.combo.set_active(index)
					return
		if(len(model)>0):
			self.combo.set_active(0)
		return						