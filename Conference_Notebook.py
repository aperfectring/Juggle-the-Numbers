
import gtk
import gobject

class Conference_Notebook:
	def __init__(self, parent_box, db_cursor, db_handle, JTN_db, get_season_id):
		self.parent_box = parent_box
		self.db_cursor = db_cursor
		self.db_handle = db_handle
		self.JTN_db = JTN_db
		self.get_season_id = get_season_id
		self.callback_list = []

		self.list_hbox = gtk.HBox(spacing=10)
		self.list_hbox.set_border_width(5)
		self.parent_box.pack_start(self.list_hbox)

		### Widgets for handling the "all confs" section of the window
		all_list_vbox = gtk.VBox(spacing=10)
		all_list_vbox.set_border_width(5)
		self.list_hbox.pack_start(all_list_vbox)

		scrolled_window = gtk.ScrolledWindow()
		all_list_vbox.pack_start(scrolled_window)

		list_store = gtk.ListStore(gobject.TYPE_STRING)

		self.all_view = gtk.TreeView()
		scrolled_window.add(self.all_view)
		self.all_view.set_model(list_store)

		column = gtk.TreeViewColumn("All Confs", gtk.CellRendererText(), text=0)
		column.set_sort_column_id(0)
		self.all_view.append_column(column)

		all_list_hbox = gtk.HBox(spacing=10)
		all_list_hbox.set_border_width(5)
		all_list_vbox.pack_start(all_list_hbox, expand=False)

		self.all_confs_edit_button = gtk.Button("Edit conf")
		all_list_hbox.add(self.all_confs_edit_button)
		self.all_confs_edit_button.connect('clicked', self.edit_conf, self.all_view)
		
		self.all_confs_del_button = gtk.Button("Delete conf")
		all_list_hbox.add(self.all_confs_del_button)
		self.all_confs_del_button.connect('clicked', self.delete_conf, self.all_view)


		### Widgets for moving a team between the "all confs" and the "league confs"
		###    sections of the window.
		self.buttons_vbox = gtk.VBox(spacing=10)
		self.buttons_vbox.set_border_width(5)
		self.list_hbox.pack_start(self.buttons_vbox, expand=False)

		self.add_button = gtk.Button(">")
		self.remove_button = gtk.Button("<")
		self.buttons_vbox.add(self.add_button)
		self.buttons_vbox.add(self.remove_button)
		self.add_button.connect('clicked', self.add_conf)
		self.remove_button.connect('clicked', self.remove_conf)


		### Widgets for handling the "league confs" section of the window.
		league_list_vbox = gtk.VBox(spacing=10)
		league_list_vbox.set_border_width(5)
		self.list_hbox.pack_start(league_list_vbox)

		scrolled_window = gtk.ScrolledWindow()
		league_list_vbox.pack_start(scrolled_window)

		list_store = gtk.ListStore(gobject.TYPE_STRING)

		self.league_view = gtk.TreeView()
		scrolled_window.add(self.league_view)
		self.league_view.set_model(list_store)

		column = gtk.TreeViewColumn("League Confss", gtk.CellRendererText(), text=0)
		column.set_sort_column_id(0)
		self.league_view.append_column(column)

		league_list_hbox = gtk.HBox(spacing=10)
		league_list_hbox.set_border_width(5)
		league_list_vbox.pack_start(league_list_hbox, expand=False)

		self.league_confs_edit_button = gtk.Button("Edit conf")
		league_list_hbox.add(self.league_confs_edit_button)
		self.league_confs_edit_button.connect('clicked', self.edit_conf, self.league_view)

		self.league_confs_del_button = gtk.Button("Delete conf")
		league_list_hbox.add(self.league_confs_del_button)
		self.league_confs_del_button.connect('clicked', self.delete_conf, self.league_view)



		self.confops_hbox = gtk.HBox(spacing=10)
		self.confops_hbox.set_border_width(5)
		self.parent_box.pack_end(self.confops_hbox, expand=False)
		
		self.conf_add_button = gtk.Button("Add conf")
		self.confops_hbox.add(self.conf_add_button)
		self.conf_add_button.connect('clicked', self.edit_conf, self.all_view)

	### Register with the class for callbacks on updates
	def register(self, callback):
		self.callback_list.append(callback)


	def repop(self):
		sid = self.get_season_id()
		all_list = self.all_view.get_model()
		all_list.clear()
		league_list = self.league_view.get_model()
		league_list.clear()

		self.db_cursor.execute("SELECT conf_name, conf_id FROM confs")
		for row in self.db_cursor.fetchall():
			if row:
				self.db_cursor.execute("SELECT * FROM season_confs WHERE (conf_id = '" + str(row[1]) + "' AND season_id = '" + str(sid) + "')")
				if len(self.db_cursor.fetchall()) >= 1:
					league_list.append([row[0]])
				else:
					all_list.append([row[0]])

		for callback in self.callback_list:
			callback()

	def get_conf(self, view):
		all_list = view.get_model()
		if view.get_cursor()[0]:
			itera = all_list.iter_nth_child(None, view.get_cursor()[0][0])
			name = all_list.get_value(itera, 0)
			self.db_cursor.execute("SELECT conf_id FROM confs WHERE conf_name = '" + name + "'")
			row = self.db_cursor.fetchone()
			if row:
				return (name, int(row[0]))
		return (None, None)

	def add_conf(self, button):
		(name, myid) = self.get_conf(self.all_view)
		self.db_cursor.execute("INSERT INTO season_confs (conf_id, season_id) VALUES ('" + str(myid) + "', '" + str(self.get_season_id()) + "')")
		self.JTN_db.commit()
		self.repop()

	def remove_conf(self, button):
		(name, myid) = self.get_conf(self.league_view)
		self.db_cursor.execute("DELETE FROM season_confs WHERE (conf_id = '" + str(myid) + "' AND season_id = '" + str(self.get_season_id()) + "')")
		self.JTN_db.commit()
		self.repop()

	def delete_conf(self, button, view):
		if view == None:
			return
		all_list = view.get_model()
		(name, myid) = self.get_conf(view)

		self.db_cursor.execute("UPDATE team_season SET conf_id = NULL WHERE conf_id = '" + str(myid) + "'")

		self.db_cursor.execute("DELETE FROM season_confs WHERE (conf_id = '" + str(myid) + "')")
		self.db_cursor.execute("DELETE FROM confs WHERE (conf_id = '" + str(myid) + "')")
		self.JTN_db.commit()
		self.repop()

	def edit_conf(self, button, view):
		#Determine if we are editing an already existing conference, or creating a new one
		if button.get_label() == "Edit conf":
			edit = True
		else:
			edit = False

		if view == None:
			return

		all_list = view.get_model()
		# If we are editing a conf, get the id of the current conf
		if edit == True:
			(name, myid) = self.get_conf(view)

		dialog = gtk.Dialog("Edit Conf",
					None,
					gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

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

		if edit == True:
			name_entry.set_text(name)

		response = dialog.run()
		if response == gtk.RESPONSE_ACCEPT:
			if name_entry.get_text() != "":
				if edit == True:
					self.db_cursor.execute("UPDATE confs " +
									"SET conf_name = '" + name_entry.get_text() + "'" +
									"WHERE conf_name = '" + name + "'")
				else:
					self.db_cursor.execute("INSERT INTO confs (conf_name) " +
									"VALUES ('" + name_entry.get_text() + "')")
				self.JTN_db.commit()

				self.repop()

		dialog.destroy()