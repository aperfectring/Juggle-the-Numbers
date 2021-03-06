
import gtk
import gobject

# id, name, city, abbr

class Teams_Notebook:
	def __init__(self, parent_box, JTN_db, get_season_id):
		self.parent_box = parent_box
		self.JTN_db = JTN_db
		self.get_season_id = get_season_id
		self.callback_list = []

		self.list_hbox = gtk.HBox(spacing=10)
		self.list_hbox.set_border_width(5)
		self.parent_box.pack_start(self.list_hbox)


		### Widgets for handling the "all teams" section of the window
		all_list_vbox = gtk.VBox(spacing=10)
		all_list_vbox.set_border_width(5)
		self.list_hbox.pack_start(all_list_vbox)

		scrolled_window = gtk.ScrolledWindow()
		all_list_vbox.pack_start(scrolled_window)

		list_store = gtk.ListStore(gobject.TYPE_STRING)

		self.all_view = gtk.TreeView()
		scrolled_window.add(self.all_view)
		self.all_view.set_model(list_store)

		column = gtk.TreeViewColumn("All Teams", gtk.CellRendererText(), text=0)
		column.set_sort_column_id(0)
		self.all_view.append_column(column)

		all_list_hbox = gtk.HBox(spacing=10)
		all_list_hbox.set_border_width(5)
		all_list_vbox.pack_start(all_list_hbox, expand=False)

		self.all_team_edit_button = gtk.Button("Edit team")
		all_list_hbox.add(self.all_team_edit_button)
		self.all_team_edit_button.connect('clicked', self.edit_team, self.all_view)

		self.all_team_del_button = gtk.Button("Delete team")
		all_list_hbox.add(self.all_team_del_button)
		self.all_team_del_button.connect('clicked', self.delete_team, self.all_view)



		### Widgets for moving a team between the "all teams" and the "league teams"
		###   sections of the window.
		self.buttons_vbox = gtk.VBox(spacing=10)
		self.buttons_vbox.set_border_width(5)
		self.list_hbox.pack_start(self.buttons_vbox, expand=False)

		self.add_button = gtk.Button(">")
		self.remove_button = gtk.Button("<")
		self.buttons_vbox.add(self.add_button)
		self.buttons_vbox.add(self.remove_button)
		self.add_button.connect('clicked', self.add_team)
		self.remove_button.connect('clicked', self.remove_team)



		### Widgets for handling the "league teams" section of the window.
		league_list_vbox = gtk.VBox(spacing=10)
		league_list_vbox.set_border_width(5)
		self.list_hbox.pack_start(league_list_vbox)

		scrolled_window = gtk.ScrolledWindow()
		league_list_vbox.pack_start(scrolled_window)

		list_store = gtk.ListStore(gobject.TYPE_STRING)

		self.league_view = gtk.TreeView()
		scrolled_window.add(self.league_view)
		self.league_view.set_model(list_store)

		column = gtk.TreeViewColumn("League Teams", gtk.CellRendererText(), text=0)
		column.set_sort_column_id(0)
		self.league_view.append_column(column)

		league_list_hbox = gtk.HBox(spacing=10)
		league_list_hbox.set_border_width(5)
		league_list_vbox.pack_start(league_list_hbox, expand=False)

		self.league_team_edit_button = gtk.Button("Edit team")
		league_list_hbox.add(self.league_team_edit_button)
		self.league_team_edit_button.connect('clicked', self.edit_team, self.league_view, True)

		self.league_team_del_button = gtk.Button("Delete team")
		league_list_hbox.add(self.league_team_del_button)
		self.league_team_del_button.connect('clicked', self.delete_team, self.league_view)




		self.teamops_hbox = gtk.HBox(spacing=10)
		self.teamops_hbox.set_border_width(5)
		self.parent_box.pack_end(self.teamops_hbox, expand=False)
		
		self.team_add_button = gtk.Button("Add team")
		self.teamops_hbox.add(self.team_add_button)
		self.team_add_button.connect('clicked', self.edit_team, self.all_view)

	### Register with the class for callbacks on updates
	def register(self, callback):
		self.callback_list.append(callback)


	### Fill the team lists with all teams
	def repop(self):
		sid = self.get_season_id()
		all_list = self.all_view.get_model()
		all_list.clear()
		league_list = self.league_view.get_model()
		league_list.clear()

		cur_teams = self.JTN_db.get_teams_by_season(sid)

		# Checks each team to see if it is in the list
		#    of teams associated with this season
		map(lambda x: league_list.append([x[1]]) \
				if (x[0] in [i[0] for i in cur_teams]) \
				else all_list.append([x[1]]),
			self.JTN_db.get_teams())
					
		map(lambda x:  x(), filter(lambda x: x, self.callback_list))


	### Get the team tuple from the provided view
	def get_team(self, view):
		all_list = view.get_model()
		if view.get_cursor()[0]:
			itera = all_list.iter_nth_child(None, view.get_cursor()[0][0])
			name = all_list.get_value(itera, 0)
			myid = None
			city = ""
			return self.JTN_db.get_team(name = name)
		return (None, None, None, None)

	### Move a team to the "league teams" list
	def add_team(self, button):
		(myid, name, city, abbr) = self.get_team(self.all_view)
		self.JTN_db.add_team(self.get_season_id(), myid)
		self.repop()

	### Remove a team from the "league teams" list
	def remove_team(self, button):
		(myid, name, city, abbr) = self.get_team(self.league_view)
		self.JTN_db.remove_team(self.get_season_id(), myid)
		self.repop()

	### Delete all references to the selected team from the DB
	def delete_team(self, button, view):
		if view == None:
			return
		all_list = view.get_model()
		(myid, name, city, abbr) = self.get_team(view)

		self.JTN_db.delete_team(myid)
		self.repop()

	### Create/edit the details of a team
	def edit_team(self, button, view, has_season = False):
		# Determine if we are editing an already existing team, or creating a new one
		edit = True if (button.get_label() == "Edit team") else False

		if view == None:
			return

		all_list = view.get_model()
		# If we are editing a team, get the details of the current team
		if edit == True:
			(myid, name, city, abbr) = self.get_team(view)
			if name == None:
				return
			conf_id = None
			if has_season == True:
				row = self.JTN_db.get_team_conf(myid, self.get_season_id())
				conf_id = None
				if row:
					conf_id = row[0]


		# Create a dialog window to prompt the user for new information.
		dialog = gtk.Dialog("Edit Team",
				    None,
				    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
				    (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
				     gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

		name_hbox = gtk.HBox(spacing=10)
		name_hbox.set_border_width(5)
		name_hbox.show()
		dialog.vbox.pack_start(name_hbox)
		name_label = gtk.Label("Name:")
		name_label.show()
		name_hbox.pack_start(name_label)
		name_entry = gtk.Entry()
		name_entry.show()
		name_hbox.pack_start(name_entry)

		city_hbox = gtk.HBox(spacing=10)
		city_hbox.set_border_width(5)
		city_hbox.show()
		dialog.vbox.pack_start(city_hbox)
		city_label = gtk.Label("City:")
		city_label.show()
		city_hbox.pack_start(city_label)
		city_entry = gtk.Entry()
		city_entry.show()
		city_hbox.pack_start(city_entry)

		abbr_hbox = gtk.HBox(spacing=10)
		abbr_hbox.set_border_width(5)
		abbr_hbox.show()
		dialog.vbox.pack_start(abbr_hbox)
		abbr_label = gtk.Label("Abbr:")
		abbr_label.show()
		abbr_hbox.pack_start(abbr_label)
		abbr_entry = gtk.Entry()
		abbr_entry.show()
		abbr_hbox.pack_start(abbr_entry)

		if has_season == True:
			conf_hbox = gtk.HBox(spacing=10)
			conf_hbox.set_border_width(5)
			conf_hbox.show()
			dialog.vbox.pack_start(conf_hbox)
			conf_label = gtk.Label("Conf:")
			conf_label.show()
			conf_hbox.pack_start(conf_label)
			conf_combo = gtk.combo_box_new_text()
			conf_combo.append_text("None")

			map(lambda x: conf_combo.append_text(self.JTN_db.get_conf(conf_id = x[1])[1]),
			    self.JTN_db.get_confs_by_season(self.get_season_id()))
			model = conf_combo.get_model()
			conf_combo.set_active(0)
			if conf_id:
				conf_name = self.JTN_db.get_conf(conf_id = conf_id)[1]
				if conf_name:
					map(conf_combo.set_active, filter(lambda x: model[x][0] == conf_name, range(0, len(model))))
			conf_combo.show()
			conf_hbox.pack_start(conf_combo)

		# If we are editing a team, update the widgets to have the current
		#   information for that team
		if edit == True:
			name_entry.set_text(name)
			city_entry.set_text(city)
			if abbr == None:
				abbr = ""
			abbr_entry.set_text(abbr)

		response = dialog.run()
		if response == gtk.RESPONSE_ACCEPT:
			if name_entry.get_text() != "":
				if edit == True:
					self.JTN_db.edit_team(old_name = name,
							      new_name = name_entry.get_text(),
							      city = city_entry.get_text(),
							      abbr = abbr_entry.get_text())
					if has_season == True:
						conf_id = None
						model = conf_combo.get_model()
						if model[conf_combo.get_active()][0] != "None":
							row = self.JTN_db.get_conf(conf_name = model[conf_combo.get_active()][0])
							if row:
								conf_id = row[0]
						self.JTN_db.set_team_conf(myid, self.get_season_id(), conf_id)
						
				else:
					self.JTN_db.create_team(name = name_entry.get_text(),
								city = city_entry.get_text(),
								abbr = abbr_entry.get_text())

				self.repop()

		dialog.destroy()
