
import gtk

class League_Notebook:
	def __init__(self, parent_box, db_cursor, db_handle, selected_league_func):
		self.parent_box = parent_box
		self.db_cursor = db_cursor
		self.db_handle = db_handle
		self.callback_list = []
		self.selected_league_func = selected_league_func

		### Create and add all of the widgets for the notebook page.
		self.name_hbox = gtk.HBox(spacing=10)
		self.name_hbox.set_border_width(5)
		self.parent_box.pack_start(self.name_hbox, expand=False)

		self.name_label = gtk.Label("Name:")
		self.name_hbox.add(self.name_label)

		self.name_entry = gtk.Entry()
		self.name_hbox.add(self.name_entry)

		self.country_hbox = gtk.HBox(spacing=10)
		self.country_hbox.set_border_width(5)
		self.parent_box.pack_start(self.country_hbox, expand=False)

		self.country_label = gtk.Label("Country:")
		self.country_hbox.add(self.country_label)

		self.oldname_label = gtk.Label()

		self.country_entry = gtk.Entry()
		self.country_hbox.add(self.country_entry)

		self.confed_hbox = gtk.HBox(spacing=10)
		self.confed_hbox.set_border_width(5)
		self.parent_box.pack_start(self.confed_hbox, expand=False)

		self.confed_label = gtk.Label("Confederation:")
		self.confed_hbox.add(self.confed_label)

		self.confed_entry = gtk.Entry()
		self.confed_hbox.add(self.confed_entry)

		self.level_hbox = gtk.HBox(spacing=10)
		self.level_hbox.set_border_width(5)
		self.parent_box.pack_start(self.level_hbox, expand=False)

		self.level_label = gtk.Label("League Level:")
		self.level_hbox.add(self.level_label)

		self.level_entry = gtk.Entry()
		self.level_hbox.add(self.level_entry)

		self.update_button = gtk.Button("Update")
		self.parent_box.pack_end(self.update_button, expand=False)
		self.update_button.connect('clicked', self.update)


	### Register with the class for callbacks on updates
	def register(self, callback):
		self.callback_list.append(callback)


	def repop(self):
		name = self.selected_league_func()

		self.db_cursor.execute("SELECT country, confederation, level " +
						"FROM leagues WHERE league_name = '" +
						name +
						"'")
		for row in self.db_cursor:
			if row:
				self.set(name = name, country = row[0], confed = row[1], level = row[2])

	### Callback for the "Update" button on the league notebook page
	###    Commits all data from the league notebook page to the database
	###    Updates the league combobox string to reflect any changes made
	def update(self, button):
		self.db_cursor.execute("UPDATE leagues " + 
                                           "SET country = '" + self.country_entry.get_text() + "', " + 
                                              "league_name = '" + self.name_entry.get_text() + "', " + 
                                              "confederation = '" + self.confed_entry.get_text() + "', " + 
                                              "level = '" + self.level_entry.get_text() + "' " + 
                                           "WHERE league_name = '" + self.oldname_label.get_label() + "'")
		self.db_handle.commit()

		for callback in self.callback_list:
			callback(self.name_entry.get_text())

	def set(self, name = "", confed = "", level = "", country = ""):

		if name == None:
			name = ""
		self.name_entry.set_text(name)
		self.oldname_label.set_label(name)

		if country == None:
			country = ""
		if confed == None:
			confed = ""
		if level == None:
			level = ""

		self.country_entry.set_text(country)
		self.confed_entry.set_text(confed)
		self.level_entry.set_text(str(level))

		return


