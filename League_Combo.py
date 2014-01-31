import gtk

class League_Combo:
	def __init__(self, parent):
		self.parent = parent
		
		self.label = gtk.Label("League:")
		self.parent.league_vbox.pack_start(self.label, expand=False)

		self.combo = gtk.combo_box_new_text()
		self.parent.league_vbox.pack_start(self.combo, expand=False)
		self.combo.connect('changed', self.update)

		self.button = gtk.Button("Add League")
		self.parent.league_vbox.pack_start(self.button, expand=False)
		self.button.connect('clicked', self.add)

	### Callback for when the league combobox is changed
	###    Updates the league notebook page.
	###    Also deletes all entries from the season combobox, then adds the appropriate ones for this league
	def update(self, combobox):
		model = combobox.get_model()
		index = combobox.get_active()

		if index >= 0:
			name = model[index][0]

			### Fetches all the league information from the database
			self.parent.cur.execute("SELECT country, confederation, level " + 
        	                                   "FROM leagues WHERE league_name = '" + name + "'")

			for row in self.parent.cur:
				if row:
					self.parent.league_note.set(name = name, country = row[0], confed = row[1], level = row[2])


		### Delete all season combobox entries, then populate the combobox with appropriate ones for this league
		self.parent.season_combo.repop()
		return

	### Callback for the "Add league" button
	###    This will create a "blank" league
	###    This will leave the newly created league as the currently selected one
	def add(self, button):
		text = ""
		try:
			self.parent.cur.execute("INSERT INTO leagues (league_name)VALUES ('" + text + "')")
		except sqlite3.IntegrityError:
			model = self.combo.get_model()

		self.combo.append_text(text)
		model = self.combo.get_model()
		for index in range(0,len(model)):
			if (model[index][0] == text):
				self.combo.set_active(index)

		self.parent.db.commit()

	### Determine the League Unique database ID based on the currently selected league from the combobox
	def get_id(self):
		model = self.combo.get_model()
		index = self.combo.get_active()
		if (index < 0):
			return None
		self.parent.cur.execute("SELECT id FROM leagues WHERE league_name = '" + model[index][0] + "'")
		for row in self.parent.cur:
			if row != None and row[0] != None:
				return row[0]
			else:
				return None

	### Deletes all season combobox entries, then repopulates the combobox with appriopriate ones for this season
	###   Will attempt to select an entry which has the value of select_val, if specified
	def repop(self, select_val = None):
		model = self.combo.get_model()
		for index in range(0, len(model)):
			self.combo.remove_text(0)

		self.parent.cur.execute("SELECT league_name FROM leagues")
                for row in self.parent.cur:
			self.combo.append_text(row[0])

		model = self.combo.get_model()
		if select_val != None:
			for index in range(0, len(model)):
				if model[index][0] == select_val:
					self.combo.set_active(index)
					return
		if(len(model)>0):
			self.combo.set_active(0)
		return						
