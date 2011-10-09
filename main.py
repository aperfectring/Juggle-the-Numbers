import pygtk
pygtk.require('2.0')
import gtk
import gobject
import sqlite3
import re
import traceback

class League_Combo:
	def __init__(self, parent):
		self.parent = parent
		
		self.label = gtk.Label("League:")
		self.parent.league_vbox.add(self.label)

		self.combo = gtk.combo_box_new_text()
		self.repop()
		self.parent.league_vbox.add(self.combo)
		self.combo.connect('changed', self.update)

		self.button = gtk.Button("Add League")
		self.parent.league_vbox.add(self.button)
		self.button.connect('clicked', self.add)

	### Callback for when the league combobox is changed
	###    Updates the league notebook page.
	###    Also deletes all entries from the season combobox, then adds the appropriate ones for this league
	def update(self, combobox):
		model = combobox.get_model()
		index = combobox.get_active()
		name = combobox.get_model()[combobox.get_active()][0]

		### Fetches all the league information from the database
		self.parent.cur.execute("SELECT country, confederation, level " + 
                                           "FROM leagues WHERE league_name = '" + model[index][0] + "'")

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
			print row
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

class League_Notebook:
	def __init__(self, parent):
		self.parent = parent

		self.name_hbox = gtk.HBox(spacing=10)
		self.name_hbox.set_border_width(5)
		self.parent.league_note_vbox.pack_start(self.name_hbox, expand=False)

		self.name_label = gtk.Label("Name:")
		self.name_hbox.add(self.name_label)

		self.name_entry = gtk.Entry()
		self.name_hbox.add(self.name_entry)

		self.country_hbox = gtk.HBox(spacing=10)
		self.country_hbox.set_border_width(5)
		self.parent.league_note_vbox.pack_start(self.country_hbox, expand=False)

		self.country_label = gtk.Label("Country:")
		self.country_hbox.add(self.country_label)

		self.oldname_label = gtk.Label()

		self.country_entry = gtk.Entry()
		self.country_hbox.add(self.country_entry)

		self.confed_hbox = gtk.HBox(spacing=10)
		self.confed_hbox.set_border_width(5)
		self.parent.league_note_vbox.pack_start(self.confed_hbox, expand=False)

		self.confed_label = gtk.Label("Confederation:")
		self.confed_hbox.add(self.confed_label)

		self.confed_entry = gtk.Entry()
		self.confed_hbox.add(self.confed_entry)

		self.level_hbox = gtk.HBox(spacing=10)
		self.level_hbox.set_border_width(5)
		self.parent.league_note_vbox.pack_start(self.level_hbox, expand=False)

		self.level_label = gtk.Label("League Level:")
		self.level_hbox.add(self.level_label)

		self.level_entry = gtk.Entry()
		self.level_hbox.add(self.level_entry)

		self.update_button = gtk.Button("Update")
		self.parent.league_note_vbox.pack_end(self.update_button, expand=False)
		self.update_button.connect('clicked', self.update)

	### Callback for the "Update" button on the league notebook page
	###    Commits all data from the league notebook page to the database
	###    Updates the league combobox string to reflect any changes made
	def update(self, button):
		self.parent.cur.execute("UPDATE leagues " + 
                                           "SET country = '" + self.country_entry.get_text() + "', " + 
                                              "league_name = '" + self.name_entry.get_text() + "', " + 
                                              "confederation = '" + self.confed_entry.get_text() + "', " + 
                                              "level = '" + self.level_entry.get_text() + "' " + 
                                           "WHERE league_name = '" + self.oldname_label.get_label() + "'")
		self.parent.db.commit()

		self.parent.league_combo.repop(self.name_entry.get_text())

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

class Season_Combo:
	def __init__(self, parent):
		self.parent = parent
		self.label = gtk.Label("Season:")
		self.parent.season_vbox.add(self.label)

		self.combo = gtk.combo_box_new_text()
		self.repop()
		self.parent.season_vbox.add(self.combo)
		self.combo.connect('changed', self.update)

		self.button = gtk.Button("Add Season")
		self.parent.season_vbox.add(self.button)
		self.button.connect('clicked', self.add)

	### Callback handler for when the season combobox changes
	###   Updates the season notebook page
	def update(self, combobox):
		### We will get this callback when we are deleting all entries in the season combobox, so we
		###   only want to actually try to update the notebook page if we are changing to a valid
		###   index
		index = self.combo.get_active()
		if(index < 0):
			return

		season_id = self.get_id()

		### Decode the starting year month and day from the season entry in the database		
		self.parent.cur.execute("SELECT STRFTIME('%Y',start), STRFTIME('%m',start), STRFTIME('%d',start) " + 
                                           "FROM seasons WHERE id = '" + str(season_id) + "'")
		for row in self.parent.cur:
			if row != None:
				self.parent.season_note.set_start(year = row[0], month = row[1], day = row[2])

		### Decode the ending year month and day from the season entry in the database		
		self.parent.cur.execute("SELECT STRFTIME('%Y',end), STRFTIME('%m',end), STRFTIME('%d',end) " + 
                                           "FROM seasons WHERE id = '" + str(season_id) + "'")
		for row in self.parent.cur:
			if row != None:
				self.parent.season_note.set_end(year = row[0], month = row[1], day = row[2])

		self.parent.teams_note.repop()

	### Callback for when the "Add season" button is clicked"
	###    This will create a "blank" season, which has no start or end date
	###    This will leave the created season as the selected one
	def add(self, button):
		league_id = self.parent.league_combo.get_id()
		self.parent.cur.execute("INSERT INTO seasons (league) VALUES ('" + str(league_id) + "')")
		self.parent.db.commit()
		self.repop('')

	### Determine the Season Unique database ID based on the currently selected season from the combobox	
	def get_id(self):
		model = self.combo.get_model()
		index = self.combo.get_active()
		season_text = model[index][0]
		season_start = None
		season_end = None

		### Since seasons are named based on start-end, the names are only unique within a season
		###   so we need to limit our search within the currently selected season.
		league_id = self.parent.league_combo.get_id()

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
			self.parent.cur.execute("SELECT id FROM seasons " + 
                                                   "WHERE STRFTIME('%Y',end) = '" + season_end + "' " + 
                                                   "AND STRFTIME('%Y',start) = '" + season_start + "' " + 
                                                   "AND league = '" + str(league_id) + "'")
		else:
			self.parent.cur.execute("SELECT id FROM seasons WHERE end IS NULL AND start IS NULL")

		for row in self.parent.cur:
			if row != None and row[0] != None:
				return row[0]
			else:
				return None

	### Deletes all season combobox entries, then repopulates the combobox with appriopriate ones for this season
	###   Will attempt to select an entry which has the value of select_val, if specified
	def repop(self, select_val = None):
		league_id = self.parent.league_combo.get_id()
		model = self.combo.get_model()
		for index in range(0, len(model)):
			self.combo.remove_text(0)

		self.parent.cur.execute("SELECT STRFTIME('%Y', start), STRFTIME('%Y', end) " + 
                                           "FROM seasons " + 
                                           "WHERE league = '" + str(league_id) + "' " + 
                                           "ORDER BY end DESC")
		for row in self.parent.cur:
			if row != None and row[0] != None and row[1] != None:
				if row[0] == row[1]:
					self.combo.append_text(row[0])
				else:
					self.combo.append_text(row[0] + "-" + row[1])
			elif row != None:
				self.combo.append_text("")
		model = self.combo.get_model()
		if select_val != None:
			for index in range(0, len(model)):
				if model[index][0] == select_val:
					self.combo.set_active(index)
					return
		if(len(model)>0):
			self.combo.set_active(0)
		return						

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

	def set_start(self, year = None, month = None, day = None):
		if (month != None) and (year != None):
			self.start_cal.select_month(int(month)-1, int(year))
			if(day != None):
				self.start_cal.select_day(int(day))

	def set_end(self, year = None, month = None, day = None):
		if (month != None) and (year != None):
			self.end_cal.select_month(int(month)-1, int(year))
			if(day != None):
				self.end_cal.select_day(int(day))

class Teams_Notebook:
	def __init__(self, parent):
		self.parent = parent

		self.list_hbox = gtk.HBox(spacing=10)
		self.list_hbox.set_border_width(5)
		self.parent.teams_note_vbox.pack_start(self.list_hbox)

		scrolled_window = gtk.ScrolledWindow()
		self.list_hbox.pack_start(scrolled_window)

		list_store = gtk.ListStore(gobject.TYPE_STRING)

		self.all_view = gtk.TreeView()
		scrolled_window.add(self.all_view)
		self.all_view.set_model(list_store)

		column = gtk.TreeViewColumn("All Teams", gtk.CellRendererText(), text=0)
		self.all_view.append_column(column)

		self.buttons_vbox = gtk.VBox(spacing=10)
		self.buttons_vbox.set_border_width(5)
		self.list_hbox.pack_start(self.buttons_vbox, expand=False)

		self.add_button = gtk.Button(">")
		self.remove_button = gtk.Button("<")
		self.buttons_vbox.add(self.add_button)
		self.buttons_vbox.add(self.remove_button)
		self.add_button.connect('clicked', self.add_team)
		self.remove_button.connect('clicked', self.remove_team)

		scrolled_window = gtk.ScrolledWindow()
		self.list_hbox.pack_start(scrolled_window)

		list_store = gtk.ListStore(gobject.TYPE_STRING)

		self.league_view = gtk.TreeView()
		scrolled_window.add(self.league_view)
		self.league_view.set_model(list_store)

		column = gtk.TreeViewColumn("League Teams", gtk.CellRendererText(), text=0)
		self.league_view.append_column(column)

		self.teamops_hbox = gtk.HBox(spacing=10)
		self.teamops_hbox.set_border_width(5)
		self.parent.teams_note_vbox.pack_end(self.teamops_hbox, expand=False)
		
		self.team_add_button = gtk.Button("Add team")
		self.teamops_hbox.add(self.team_add_button)
		self.team_add_button.connect('clicked', self.edit_team)

		self.team_edit_button = gtk.Button("Edit team")
		self.teamops_hbox.add(self.team_edit_button)
		self.team_edit_button.connect('clicked', self.edit_team)

		self.team_del_button = gtk.Button("Delete team")
		self.teamops_hbox.add(self.team_del_button)

		self.repop()

#		self.city_hbox = gtk.HBox(spacing=10)
#		self.city_hbox.set_border_width(5)
#		self.parent.teams_note_vbox.pack_start(self.city_hbox, expand=False)

#		self.city_label = gtk.Label("City:")
#		self.city_hbox.add(self.city_label)

#		self.city_entry = gtk.Entry()
#		self.city_hbox.add(self.city_entry)

#		self.update_button = gtk.Button("Update")
#		self.parent.teams_note_vbox.pack_end(self.update_button, expand=False)

	def repop(self):
		sid = self.parent.season_combo.get_id()
		all_list = self.all_view.get_model()
		all_list.clear()
		league_list = self.league_view.get_model()
		league_list.clear()
		self.parent.cur.execute("SELECT team_name,id FROM teams")
		for row in self.parent.cur.fetchall():
			if row:
				self.parent.cur.execute("SELECT * FROM team_season WHERE (team_id = '" + str(row[1]) + "' AND season_id='" + str(sid) + "')")
				#  WHERE (team_id = '" + str(row[1]) + "')"
				# "' AND season_id='" + str(sid) + 
				if len(self.parent.cur.fetchall()) >= 1:
					league_list.append([row[0]])
				else:
					all_list.append([row[0]])


	def get_team(self, view):
		all_list = view.get_model()
		if view.get_cursor()[0]:
			itera = all_list.iter_nth_child(None, view.get_cursor()[0][0])
			name = all_list.get_value(itera, 0)
			myid = None
			city = ""
			self.parent.cur.execute("SELECT city, id FROM teams WHERE team_name = '" + name + "'")
			for row in self.parent.cur:
				if row:
					city = row[0]
					myid = row[1]
		return (name, city, myid)

	def add_team(self, button):
		(name, city, myid) = self.get_team(self.all_view)
		self.parent.cur.execute("INSERT INTO team_season (team_id, season_id) VALUES ('" + str(myid) + "', '" + str(self.parent.season_combo.get_id()) + "')")
		self.parent.db.commit()
		self.repop()

	def remove_team(self, button):
		(name, city, myid) = self.get_team(self.league_view)
		self.parent.cur.execute("DELETE FROM team_season WHERE (team_id='" + str(myid) + "' AND season_id='" + str(self.parent.season_combo.get_id()) + "')")
		self.parent.db.commit()
		self.repop()

	def edit_team(self, button):
		if button.get_label() == "Edit team":
			edit = True
		else:
			edit = False

		all_list = self.all_view.get_model()
		if edit == True:
			(name, city, myid) = self.get_team(self.all_view)


		dialog = gtk.Dialog("Edit Team",
				    self.parent.window,
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

		if edit == True:
			name_entry.set_text(name)
			city_entry.set_text(city)

		response = dialog.run()
		if response == gtk.RESPONSE_ACCEPT:
			if name_entry.get_text() != "":
				if edit == True:
					self.parent.cur.execute("UPDATE teams " + 
					                           "SET team_name = '" + name_entry.get_text() + "', " + 
					                              "city = '" + city_entry.get_text() + "' " + 
					                           "WHERE team_name = '" + name + "'")
				else:
					self.parent.cur.execute("INSERT INTO teams (team_name, city) " + 
					                           "VALUES ('" + name_entry.get_text() + "', '" +
					                              city_entry.get_text() + "')")
				self.parent.db.commit()

				self.repop()

		dialog.destroy()

class Base:
	def __init__(self):
		self.db = sqlite3.connect("test.sqlite")
		self.cur = self.db.cursor()
		self.cur.execute("CREATE TABLE IF NOT EXISTS leagues (" +
                                    "league_name STRING UNIQUE, " +
                                    "id INTEGER PRIMARY KEY ASC, " + 
                                    "country STRING, " + 
                                    "confederation STRING, " + 
                                    "level INTEGER)")
		self.cur.execute("CREATE TABLE IF NOT EXISTS seasons (" + 
                                    "start DATE, " + 
                                    "end DATE, " + 
                                    "id INTEGER PRIMARY KEY ASC, " + 
                                    "league INTEGER)")
		self.cur.execute("CREATE TABLE IF NOT EXISTS teams (" +
		                    "id INTEGER PRIMARY KEY ASC, " +
		                    "team_name STRING UNIQUE, " +
		                    "city STRING)")
		self.cur.execute("CREATE TABLE IF NOT EXISTS team_season (" +
		                    "team_id INTEGER, " +
		                    "season_id INTEGER)")

		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect('destroy', lambda w: gtk.main_quit())

		self.window_vbox = gtk.VBox(spacing=10)
		self.window_vbox.set_border_width(5)
		self.window.add(self.window_vbox)

		self.combo_hbox = gtk.HBox(spacing=10)
		self.window_vbox.add(self.combo_hbox)

		self.league_vbox = gtk.VBox(spacing=5)
		self.combo_hbox.add(self.league_vbox)

		self.league_combo = League_Combo(self)

		self.season_vbox = gtk.VBox(spacing=5)
		self.combo_hbox.add(self.season_vbox)

		self.season_combo = Season_Combo(self)

		self.notebook = gtk.Notebook()
		self.window_vbox.add(self.notebook)

		#### Add Notebook Pages ####
		self.league_note_vbox = gtk.VBox(spacing=10)
		self.league_note_vbox.set_border_width(5)
		self.notebook.append_page(self.league_note_vbox, gtk.Label("League"))

		self.league_note = League_Notebook(self)
		
		self.season_note_vbox = gtk.VBox(spacing=10)
		self.season_note_vbox.set_border_width(5)
		self.notebook.append_page(self.season_note_vbox, gtk.Label("Season"))

		self.season_note = Season_Notebook(self)

		self.teams_note_vbox = gtk.VBox(spacing=10)
		self.teams_note_vbox.set_border_width(5)
		self.notebook.append_page(self.teams_note_vbox, gtk.Label("Teams"))

		self.teams_note = Teams_Notebook(self)

		#### Update the combo boxes so the notebooks show the right data ####
		self.league_combo.update(self.league_combo.combo)
		self.season_combo.update(self.season_combo.combo)

		self.window.show_all()
		return



	def main(self):
		gtk.main()

if __name__ == "__main__":
	base = Base()
	base.main()
