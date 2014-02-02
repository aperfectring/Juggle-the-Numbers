
import gtk

class Conference_Combo:
	def __init__(self, parent):
		self.parent = parent
		self.label = gtk.Label("Conference:")
		self.parent.conference_vbox.pack_start(self.label, expand=False)

		self.combo = gtk.combo_box_new_text()
		self.parent.conference_vbox.pack_start(self.combo, expand=False)
		self.combo.connect('changed', self.update)

	### Update the combo box with the appropriate conferences for the current league/season
	def repop(self):
		season_id = self.parent.season_combo.get_id()
		model = self.combo.get_model()
		for index in range(0, len(model)):
			self.combo.remove_text(0)

		self.combo.append_text("Whole League")

		self.parent.cur.execute("SELECT conf_id FROM season_confs WHERE season_id = '" + str(season_id) + "'")
		for row in self.parent.cur.fetchall():
			self.parent.cur.execute("SELECT conf_name FROM confs WHERE conf_id = '" + str(row[0]) + "'")
			conf_name = self.parent.cur.fetchone()
			if conf_name != None:
				self.combo.append_text(conf_name[0])

		self.combo.set_active(0)

	### Callback which triggers the recalculation of other widgets when the combo box is changed.
	def update(self, button):

		self.parent.teams_note.repop()
		self.parent.games_note.repop()

	### Fetch the unique ID of the currently selected conference
	def get_id(self):
		model = self.combo.get_model()
		index = self.combo.get_active()
		if index < 0:
			return None
		conf_text = model[index][0]

		if conf_text == "Whole League":
			return None

		self.parent.cur.execute("SELECT conf_id FROM confs WHERE conf_name = '" + str(conf_text) + "'")
		row = self.parent.cur.fetchone()
		if row != None:
			return row[0]
		return None
