import gtk

class League_Combo:
	def __init__(self, parent_box, db_cursor, db_handle):
		self.parent_box = parent_box
		self.db_cursor = db_cursor
		self.db_handle = db_handle
		self.callback_list = []
		
		self.label = gtk.Label("League:")
		self.parent_box.pack_start(self.label, expand=False)

		self.combo = gtk.combo_box_new_text()
		self.parent_box.pack_start(self.combo, expand=False)
		self.combo_changed_id = self.combo.connect('changed', self.update)

		self.button = gtk.Button("Add League")
		self.parent_box.pack_start(self.button, expand=False)
		self.button.connect('clicked', self.add)

	### Register with the class for callbacks on updates
	def register(self, callback):
		self.callback_list.append(callback)

	### Get the currently selected value from the combo box.
	def get_selected(self):
		model = self.combo.get_model()
		index = self.combo.get_active()
		name = None

		if index >= 0:
			name = model[index][0]

		return name
		

	### Callback for when the league combobox is changed
	###    Calls all registered callbacks in the order they were registered
	def update(self, combobox):
		for callback in self.callback_list:
			callback()

		return

	### Callback for the "Add league" button
	###    This will create a "blank" league
	###    This will leave the newly created league as the currently selected one
	def add(self, button):
		text = ""
		try:
			self.db_cursor.execute("INSERT INTO leagues (league_name)VALUES ('" + text + "')")
		except sqlite3.IntegrityError:
			model = self.combo.get_model()

		self.combo.append_text(text)
		model = self.combo.get_model()
		for index in range(0,len(model)):
			if (model[index][0] == text):
				self.combo.set_active(index)

		self.db_handle.commit()

	### Determine the League Unique database ID based on the currently selected league from the combobox
	def get_id(self):
		model = self.combo.get_model()
		index = self.combo.get_active()
		if (index < 0):
			return None
		self.db_cursor.execute("SELECT id FROM leagues WHERE league_name = '" + model[index][0] + "'")
		for row in self.db_cursor:
			if row != None and row[0] != None:
				return row[0]
			else:
				return None

	### Deletes all season combobox entries, then repopulates the combobox with appriopriate ones for this season
	###   Will attempt to select an entry which has the value of select_val, if specified
	def repop(self, select_val = None):
		self.combo.disconnect(self.combo_changed_id)
		model = self.combo.get_model()
		for index in range(0, len(model)):
			self.combo.remove_text(0)

		self.db_cursor.execute("SELECT league_name FROM leagues")
                for row in self.db_cursor:
			self.combo.append_text(row[0])

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