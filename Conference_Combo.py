
import gtk

class Conference_Combo:
	def __init__(self, parent_box, JTN_db, get_season_id):
		self.parent_box = parent_box
		self.JTN_db = JTN_db
		self.callback_list = []
		self.get_season_id = get_season_id

		self.label = gtk.Label("Conference:")
		self.parent_box.pack_start(self.label, expand=False)

		self.combo = gtk.combo_box_new_text()
		self.parent_box.pack_start(self.combo, expand=False)
		self.combo_changed_id = self.combo.connect('changed', self.update)

	### Register with the class for callbacks on updates
	def register(self, callback):
		self.callback_list.append(callback)

	### Update the combo box with the appropriate conferences for the current league/season
	def repop(self):
		self.combo.disconnect(self.combo_changed_id)
		season_id = self.get_season_id()
		model = self.combo.get_model()
		for index in range(0, len(model)):
			self.combo.remove_text(0)

		self.combo.append_text("Whole League")

		for row in self.JTN_db.get_confs(season_id):
			(conf_id, conf_name) = self.JTN_db.get_conf(conf_id = row[1])
			if conf_name != None:
				self.combo.append_text(conf_name)

		self.combo_changed_id = self.combo.connect('changed', self.update)
		self.combo.set_active(0)

	### Callback which triggers the recalculation of other widgets when the combo box is changed.
	def update(self, button):
		for callback in self.callback_list:
			callback()


	### Fetch the unique ID of the currently selected conference
	def get_id(self):
		model = self.combo.get_model()
		index = self.combo.get_active()
		if index < 0:
			return None
		conf_text = model[index][0]

		if conf_text == "Whole League":
			return None

		
		(conf_id, conf_name) = self.JTN_db.get_conf(conf_name = conf_text)
		return conf_id
