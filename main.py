import pygtk
pygtk.require('2.0')
import gtk
import gobject
import sqlite3
import re
import traceback
import datetime
import math
import threading

def get_team_from_name(cur, name):
	cur.execute("SELECT city, id FROM teams WHERE team_name = '" + name + "'")
	city = None
	myid = None
	for row in cur:
		if row:
			city = row[0]
			myid = row[1]
	return (name, city, myid)

style_text_array = [
		"Standard format",
		"AET and PKs format",
		"Golden goal AET format",
		"Home+Away Game 1 format",
		"Home+Away Game 2 format"
		]

def poisson_cdf(k, lamb):
	pois_sum = 0
	for i in range(0,k+1):
		pois_sum += poisson_pmf(i, lamb)
	return pois_sum

def poisson_pmf(k, lamb):
	return math.pow(lamb, k) / math.factorial(k) * math.exp(-lamb)


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
		self.parent.games_note.repop()

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
		if index < 0:
			return None
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
		# self.team_del_button.connect('clicked', self.delete_team)

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
			return get_team_from_name(self.parent.cur, name)
		return (None, None, None)

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

class Games_Notebook:
	def __init__(self, parent):
		self.parent = parent

		self.list_hbox = gtk.HBox(spacing=10)
		self.list_hbox.set_border_width(5)
		self.parent.games_note_vbox.pack_start(self.list_hbox)

		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		self.list_hbox.pack_start(scrolled_window)

		list_store = gtk.ListStore(gobject.TYPE_STRING,		# Date
						gobject.TYPE_STRING,	# Home
						gobject.TYPE_STRING,	# Home goals
						gobject.TYPE_STRING,	# Home PKs
						gobject.TYPE_STRING,	# Away
						gobject.TYPE_STRING,	# Away goals
						gobject.TYPE_STRING,	# Away PKs
						gobject.TYPE_STRING,	# AET
						gobject.TYPE_STRING,	# PKs
						gobject.TYPE_STRING,	# Style
						gobject.TYPE_STRING)	# Played

		self.all_view = gtk.TreeView()
		scrolled_window.add(self.all_view)
		self.all_view.set_model(list_store)

		column = gtk.TreeViewColumn("Date", gtk.CellRendererText(), text=0)
		column.set_sort_column_id(0)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Home", gtk.CellRendererText(), text=1)
		column.set_sort_column_id(1)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Home Goals", gtk.CellRendererText(), text=2)
		column.set_sort_column_id(2)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Home PK Goals", gtk.CellRendererText(), text=3)
		column.set_sort_column_id(3)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Away", gtk.CellRendererText(), text=4)
		column.set_sort_column_id(4)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Away Goals", gtk.CellRendererText(), text=5)
		column.set_sort_column_id(5)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Away PK Goals", gtk.CellRendererText(), text=6)
		column.set_sort_column_id(6)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("AET", gtk.CellRendererText(), text=7)
		column.set_sort_column_id(7)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("PKs", gtk.CellRendererText(), text=8)
		column.set_sort_column_id(8)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Style", gtk.CellRendererText(), text=9)
		column.set_sort_column_id(9)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Played", gtk.CellRendererText(), text=10)
		column.set_sort_column_id(10)
		self.all_view.append_column(column)

		self.gameops_hbox = gtk.HBox(spacing=10)
		self.gameops_hbox.set_border_width(5)
		self.parent.games_note_vbox.pack_end(self.gameops_hbox, expand=False)
		
		self.game_add_button = gtk.Button("Add game")
		self.gameops_hbox.add(self.game_add_button)
		self.game_add_button.connect('clicked', self.edit_game)

		self.game_edit_button = gtk.Button("Edit game")
		self.gameops_hbox.add(self.game_edit_button)
		self.game_edit_button.connect('clicked', self.edit_game)

		self.game_del_button = gtk.Button("Delete game")
		self.gameops_hbox.add(self.game_del_button)

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
		self.parent.cur.execute("SELECT date, " + 
						"home_id, home_goals, home_pks, " + 
						"away_id, away_goals, away_pks, " +
						"aet, pks, game_style, played " +
					"FROM games WHERE (season_id='" + str(sid) + "')")
		for row in self.parent.cur.fetchall():
			self.parent.cur.execute("SELECT team_name FROM teams WHERE (id='" + str(row[1]) + "')")
			for team_names in self.parent.cur.fetchall():
				home_text = team_names[0]

			self.parent.cur.execute("SELECT team_name FROM teams WHERE (id='" + str(row[4]) + "')")
			for team_names in self.parent.cur.fetchall():
				away_text = team_names[0]

			all_list.append( (row[0], home_text, row[2], row[3], away_text, row[5], row[6], row[7], row[8], style_text_array[row[9]], row[10]) )

		self.parent.table_note.repop()
		self.parent.model_note.clear()

	def get_game(self, view):
		all_list = view.get_model()
		if view.get_cursor()[0]:
			itera = all_list.iter_nth_child(None, view.get_cursor()[0][0])
			date = all_list.get_value(itera, 0)
			home = all_list.get_value(itera, 1)
			home_goals = all_list.get_value(itera, 2)
			home_pks = all_list.get_value(itera, 3)
			away = all_list.get_value(itera, 4)
			away_goals = all_list.get_value(itera, 5)
			away_pks = all_list.get_value(itera, 6)
			aet = all_list.get_value(itera, 7)
			pks = all_list.get_value(itera, 8)
			style = all_list.get_value(itera, 9)
			played = all_list.get_value(itera, 10)
		else:
			date = None
			home = None
			home_goals = None
			home_pks = None
			away = None
			away_goals = None
			away_pks = None
			aet = None
			pks = None
			style = None
			played = None
		return (date,	home, home_goals, home_pks,
				away, away_goals, away_pks,
				aet, pks, style, played)

	def pop_team_combo(self, combo):
		row = None
		self.parent.cur.execute("SELECT team_id FROM team_season WHERE (season_id='" + str(self.parent.season_combo.get_id()) + "')")
		for row in self.parent.cur.fetchall():
			self.parent.cur.execute("SELECT team_name FROM teams WHERE (id='" + str(row[0]) + "')")
			for name in self.parent.cur.fetchall():
				combo.append_text(name[0])
		if row:
			combo.set_active(0)

	def edit_game(self, button):
		if button.get_label() == "Edit game":
			edit = True
		else:
			edit = False

		all_list = self.all_view.get_model()
		if edit == True:
			(date,
				home, home_goals, home_pks,
				away, away_goals, away_pks,
				aet, pks, style, played) = self.get_game(self.all_view)
			if date == None:
				edit = False


		dialog = gtk.Dialog("Edit Game",
				    self.parent.window,
				    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
				    (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
				     gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))


		########## DATE ###########
		date_vbox = gtk.VBox(spacing=10)
		date_vbox.set_border_width(5)
		date_vbox.show()
		dialog.vbox.pack_start(date_vbox)
		date_label = gtk.Label("Date:")
		date_label.show()
		date_vbox.pack_start(date_label)
		date_cal = gtk.Calendar()
		date_cal.show()
		date_vbox.add(date_cal)


		######### HOME TEAM STUFF #############
		home_hbox = gtk.HBox(spacing=10)
		home_hbox.set_border_width(5)
		home_hbox.show()
		dialog.vbox.pack_start(home_hbox)

		home_label = gtk.Label("Home team:")
		home_label.show()
		home_hbox.pack_start(home_label)
		home_combo = gtk.combo_box_new_text()
		home_combo.show()
		self.pop_team_combo(home_combo)
		home_hbox.add(home_combo)

		homegoals_label = gtk.Label("Home goals:")
		homegoals_label.show()
		home_hbox.pack_start(homegoals_label)
		homegoals_spin = gtk.SpinButton()
		homegoals_spin.set_range(0,100)
		homegoals_spin.set_increments(1,1)
		homegoals_spin.show()
		home_hbox.pack_start(homegoals_spin)
		
		homepks_label = gtk.Label("Home PK goals:")
		homepks_label.show()
		home_hbox.pack_start(homepks_label)
		homepks_spin = gtk.SpinButton()
		homepks_spin.set_range(0,100)
		homepks_spin.set_increments(1,1)
		homepks_spin.show()
		home_hbox.pack_start(homepks_spin)


		######### AWAY TEAM STUFF #############
		away_hbox = gtk.HBox(spacing=10)
		away_hbox.set_border_width(5)
		away_hbox.show()
		dialog.vbox.pack_start(away_hbox)

		away_label = gtk.Label("Away team:")
		away_label.show()
		away_hbox.pack_start(away_label)
		away_combo = gtk.combo_box_new_text()
		away_combo.show()
		self.pop_team_combo(away_combo)
		away_hbox.add(away_combo)

		awaygoals_label = gtk.Label("Away goals:")
		awaygoals_label.show()
		away_hbox.pack_start(awaygoals_label)
		awaygoals_spin = gtk.SpinButton()
		awaygoals_spin.set_range(0,100)
		awaygoals_spin.set_increments(1,1)
		awaygoals_spin.show()
		away_hbox.pack_start(awaygoals_spin)
		
		awaypks_label = gtk.Label("Away PK goals:")
		awaypks_label.show()
		away_hbox.pack_start(awaypks_label)
		awaypks_spin = gtk.SpinButton()
		awaypks_spin.set_range(0,100)
		awaypks_spin.set_increments(1,1)
		awaypks_spin.show()
		away_hbox.pack_start(awaypks_spin)


		############# Extra Time Stuff ###############
		et_hbox = gtk.HBox(spacing=10)
		et_hbox.set_border_width(5)
		et_hbox.show()
		dialog.vbox.pack_start(et_hbox)

		played_check = gtk.CheckButton("Game has been played")
		played_check.show()
		et_hbox.pack_start(played_check)

		aet_check = gtk.CheckButton("Went to AET")
		aet_check.show()
		et_hbox.pack_start(aet_check)

		pk_check = gtk.CheckButton("Went to PKs")
		pk_check.show()
		et_hbox.pack_start(pk_check)

		style_combo = gtk.combo_box_new_text()
		for this_text in style_text_array:
			style_combo.append_text(this_text)
		style_combo.set_active(0)
		style_combo.show()
		et_hbox.pack_start(style_combo)


		season_id_text = str(self.parent.season_combo.get_id())

		###### Populate the widgets with the retrieved data
		if edit == True:
			datetime_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
			date_cal.select_month(datetime_obj.month - 1, datetime_obj.year)
			date_cal.select_day(datetime_obj.day)
			model = home_combo.get_model()
			for index in range(0,len(model)):
				if model[index][0] == home:
					home_combo.set_active(index)
			homegoals_spin.set_value(int(home_goals))
			homepks_spin.set_value(int(home_pks))

			model = away_combo.get_model()
			for index in range(0,len(model)):
				if model[index][0] == away:
					away_combo.set_active(index)
			awaygoals_spin.set_value(int(away_goals))
			awaypks_spin.set_value(int(away_pks))

			aet_check.set_active(True if (aet == "TRUE") else False)
			pk_check.set_active(True if (pks == "TRUE") else False)
			played_check.set_active(True if (played == "TRUE") else False)
			model = style_combo.get_model()
			for index in range(0,len(model)):
				if model[index][0] == style:
					style_combo.set_active(index)
		else:
			## Get the latest date of a game in the list
			self.parent.cur.execute("SELECT date FROM games WHERE season_id = '" + season_id_text + "' ORDER BY date DESC")
			this_val = self.parent.cur.fetchone()
			if this_val != None:
				start_date = this_val[0]
				datetime_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
				date_cal.select_month(datetime_obj.month - 1, datetime_obj.year)
				date_cal.select_day(datetime_obj.day)
			else:
				begin_date = self.parent.season_note.start_cal.get_date()
				date_cal.select_month(begin_date[1], begin_date[0])
				date_cal.select_day(begin_date[2])

		response = dialog.run()
		if response == gtk.RESPONSE_ACCEPT:
			newdate = date_cal.get_date()
			date_text = str(newdate[0]) + "-" + str(newdate[1]+1).zfill(2) + "-" + str(newdate[2]).zfill(2)
			model = home_combo.get_model()
			index = home_combo.get_active()
			home_text = model[index][0]
			home_goals_text = str(homegoals_spin.get_value_as_int())
			home_pks_text = str(homepks_spin.get_value_as_int())
			model = away_combo.get_model()
			index = away_combo.get_active()
			away_text = model[index][0]
			away_goals_text = str(awaygoals_spin.get_value_as_int())
			away_pks_text = str(awaypks_spin.get_value_as_int())
			aet_text = "TRUE" if (aet_check.get_active() == True) else "FALSE"
			pks_text = "TRUE" if (pk_check.get_active() == True) else "FALSE"
			played_text = "TRUE" if (played_check.get_active() == True) else "FALSE"
			model = style_combo.get_model()
			index = style_combo.get_active()
			style_text = model[index][0]
			style_num_text = str(index)

			(home_text, home_city_text, home_id) = get_team_from_name(self.parent.cur, home_text)
			(away_text, away_city_text, away_id) = get_team_from_name(self.parent.cur, away_text)
			home_id_text = str(home_id)
			away_id_text = str(away_id)


			if home_text != away_text:
				if edit == True:
					(home, orig_home_city_text, orig_home_id) = get_team_from_name(self.parent.cur, home)
					(away, orig_away_city_text, orig_away_id) = get_team_from_name(self.parent.cur, away)
					orig_home_id_text = str(orig_home_id)
					orig_away_id_text = str(orig_away_id)
					self.parent.cur.execute("UPDATE games SET " +
									"date = '"       + date_text       + "', " +
									"home_id = '"    + home_id_text    + "', " +
									"home_goals = '" + home_goals_text + "', " +
									"home_pks = '"   + home_pks_text   + "', " +
									"away_id = '"    + away_id_text    + "', " +
									"away_goals = '" + away_goals_text + "', " +
									"away_pks = '"   + away_pks_text   + "', " +
									"aet = '"        + aet_text        + "', " +
									"pks = '"        + pks_text        + "', " +
									"game_style = '" + style_num_text  + "', "  +
									"played = '"     + played_text     + "' "  +
								"WHERE (season_id = '" + season_id_text + "' AND " +
									"home_id = '" + orig_home_id_text + "' AND " +
									"away_id = '" + orig_away_id_text + "' AND " +
									"date = '"    + date + "')")
				else:
					self.parent.cur.execute("INSERT INTO games (season_id, date, " + 
											"home_id, home_goals, home_pks, " + 
											"away_id, away_goals, away_pks, " +
											"aet, pks, game_style, played) " +
										"VALUES (" +
											"'" + season_id_text  + "', " +
											"'" + date_text       + "', " +
											"'" + home_id_text    + "', " +
											"'" + home_goals_text + "', " +
											"'" + home_pks_text   + "', " +
											"'" + away_id_text    + "', " +
											"'" + away_goals_text + "', " +
											"'" + away_pks_text   + "', " +
											"'" + aet_text        + "', " +
											"'" + pks_text        + "', " +
											"'" + style_num_text  + "', " +
											"'" + played_text     + "')")
										

				self.parent.db.commit()
				self.repop()

		#	if name_entry.get_text() != "":
		#		if edit == True:
		#			self.parent.cur.execute("UPDATE teams " + 
		#			                           "SET team_name = '" + name_entry.get_text() + "', " + 
		#			                              "city = '" + city_entry.get_text() + "' " + 
		#			                           "WHERE team_name = '" + name + "'")
		#		else:
		#			self.parent.cur.execute("INSERT INTO teams (team_name, city) " + 
		#			                           "VALUES ('" + name_entry.get_text() + "', '" +
		#			                              city_entry.get_text() + "')")


		dialog.destroy()


class Table_Notebook:
	def __init__(self, parent):
		self.parent = parent

		self.list_hbox = gtk.HBox(spacing=10)
		self.list_hbox.set_border_width(5)
		self.parent.table_note_vbox.pack_start(self.list_hbox)

		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
		self.list_hbox.pack_start(scrolled_window)

		list_store = gtk.ListStore(gobject.TYPE_STRING,		# Team
						gobject.TYPE_INT,	# GP
						gobject.TYPE_INT,	# W
						gobject.TYPE_INT,	# L
						gobject.TYPE_INT,	# D
						gobject.TYPE_INT,	# GF
						gobject.TYPE_INT,	# GA
						gobject.TYPE_INT,	# GD
						gobject.TYPE_FLOAT,	# GF:GA
						gobject.TYPE_INT)	# Pts

		self.all_view = gtk.TreeView()
		scrolled_window.add(self.all_view)
		self.all_view.set_model(list_store)

		column = gtk.TreeViewColumn("Team", gtk.CellRendererText(), text=0)
		column.set_sort_column_id(0)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("GP", gtk.CellRendererText(), text=1)
		column.set_sort_column_id(1)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("W", gtk.CellRendererText(), text=2)
		column.set_sort_column_id(2)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("L", gtk.CellRendererText(), text=3)
		column.set_sort_column_id(3)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("D", gtk.CellRendererText(), text=4)
		column.set_sort_column_id(4)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("GF", gtk.CellRendererText(), text=5)
		column.set_sort_column_id(5)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("GA", gtk.CellRendererText(), text=6)
		column.set_sort_column_id(6)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("GD", gtk.CellRendererText(), text=7)
		column.set_sort_column_id(7)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("GF:GA", gtk.CellRendererText(), text=8)
		column.set_sort_column_id(8)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Pts", gtk.CellRendererText(), text=9)
		column.set_sort_column_id(9)
		self.all_view.append_column(column)

		self.repop()

	def repop(self):
		season_id = self.parent.season_combo.get_id()

		all_list = self.all_view.get_model()
		all_list.clear()

		self.parent.cur.execute("SELECT team_id FROM team_season WHERE season_id = '" + str(season_id) + "'")
		for row in self.parent.cur.fetchall():
			team_id = row[0]
			self.parent.cur.execute("SELECT team_name FROM teams WHERE id = '" + str(row[0]) + "'")
			team_name = self.parent.cur.fetchone()[0]

			games_played = self.fetch_gp(team_id)
			goals_scored = self.fetch_gf(team_id)
			goals_against = self.fetch_ga(team_id)
			num_tied = self.fetch_ties(team_id)
			num_won = self.fetch_wins(team_id)
			num_lost = self.fetch_loss(team_id)

			goal_ratio = 100 if goals_against == 0 else (float(goals_scored) / float(goals_against))

			all_list.append( (team_name, games_played, num_won, num_lost, num_tied, goals_scored, goals_against, goals_scored - goals_against, goal_ratio, 3*num_won + num_tied) )

	def fetch_gp(self, team, date = None):
		if date == None:
			date_today = datetime.date.today()
			date = date_today.isoformat()
		season_id = self.parent.season_combo.get_id()
		self.parent.cur.execute("SELECT COUNT(*) FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "' AND (home_id = '" + str(team) + "' OR away_id = '" + str(team) + "'))")
		games_played = self.parent.cur.fetchone()[0]
		return games_played

	def fetch_ties(self, team, date = None):
		if date == None:
			date_today = datetime.date.today()
			date = date_today.isoformat()
		season_id = self.parent.season_combo.get_id()
		self.parent.cur.execute("SELECT COUNT(*) FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "' AND (home_id = '" + str(team) + "' OR away_id = '" + str(team) + "') AND home_goals = away_goals)")
		num_tied = self.parent.cur.fetchone()[0]
		return num_tied

	def fetch_wins(self, team, date = None):
		if date == None:
			date_today = datetime.date.today()
			date = date_today.isoformat()
		season_id = self.parent.season_combo.get_id()
		self.parent.cur.execute("SELECT COUNT(*) FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "' AND ((home_id = '" + str(team) + "' AND home_goals > away_goals) OR (away_id = '" + str(team) + "') AND home_goals < away_goals))")
		num_won = self.parent.cur.fetchone()[0]
		return num_won

	def fetch_loss(self, team, date = None):
		if date == None:
			date_today = datetime.date.today()
			date = date_today.isoformat()
		season_id = self.parent.season_combo.get_id()
		self.parent.cur.execute("SELECT COUNT(*) FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "' AND ((home_id = '" + str(team) + "' AND home_goals < away_goals) OR (away_id = '" + str(team) + "') AND home_goals > away_goals))")
		num_lost = self.parent.cur.fetchone()[0]
		return num_lost

	def fetch_pts(self, team, date = None):
		num_tied = self.fetch_ties(team, date)
		num_won = self.fetch_wins(team, date)
		return (3 * num_won + num_tied)

	def fetch_gf(self, team, date = None):
		if date == None:
			date_today = datetime.date.today()
			date = date_today.isoformat()
		season_id = self.parent.season_combo.get_id()
		goals_scored = 0
		self.parent.cur.execute("SELECT SUM(home_goals) FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "' AND home_id = '" + str(team) + "')")
		goal_row = self.parent.cur.fetchone()
		if goal_row[0]:
			goals_scored = goal_row[0]
		self.parent.cur.execute("SELECT SUM(away_goals) FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "' AND away_id = '" + str(team) + "')")
		goal_row = self.parent.cur.fetchone()
		if goal_row[0]:
			goals_scored += goal_row[0]
		return goals_scored

	def fetch_ga(self, team, date = None):
		if date == None:
			date_today = datetime.date.today()
			date = date_today.isoformat()
		season_id = self.parent.season_combo.get_id()
		goals_against = 0
		self.parent.cur.execute("SELECT SUM(away_goals) FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "' AND home_id = '" + str(team) + "')")
		goal_row = self.parent.cur.fetchone()
		if goal_row[0]:
			goals_against = goal_row[0]
		self.parent.cur.execute("SELECT SUM(home_goals) FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "' AND away_id = '" + str(team) + "')")
		goal_row = self.parent.cur.fetchone()
		if goal_row[0]:
			goals_against += goal_row[0]
		return goals_against

	def fetch_home_goals(self, date = None):
		if date == None:
			date_today = datetime.date.today()
			date = date_today.isoformat()
		season_id = self.parent.season_combo.get_id()
		self.parent.cur.execute("SELECT SUM(home_goals) FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "')")
		goal_row = self.parent.cur.fetchone()
		goals = 0
		if goal_row[0]:
			goals = goal_row[0]
		return goals

	def fetch_away_goals(self, date = None):
		if date == None:
			date_today = datetime.date.today()
			date = date_today.isoformat()
		season_id = self.parent.season_combo.get_id()
		self.parent.cur.execute("SELECT SUM(away_goals) FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "')")
		goal_row = self.parent.cur.fetchone()
		goals = 0
		if goal_row[0]:
			goals = goal_row[0]
		return goals

class Model_Notebook:
	def __init__(self, parent):
		self.parent = parent
		
		self.list_hbox = gtk.HBox(spacing=10)
		self.list_hbox.set_border_width(5)
		self.parent.model_note_vbox.pack_start(self.list_hbox)

		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
		self.list_hbox.pack_start(scrolled_window)

		list_store = gtk.ListStore(gobject.TYPE_STRING,		# Team
						gobject.TYPE_FLOAT,	# Basic
						gobject.TYPE_FLOAT)	# EAP

		self.all_view = gtk.TreeView()
		scrolled_window.add(self.all_view)
		self.all_view.set_model(list_store)

		column = gtk.TreeViewColumn("Team", gtk.CellRendererText(), text=0)
		column.set_sort_column_id(0)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Basic", gtk.CellRendererText(), text=1)
		column.set_sort_column_id(1)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("EAP", gtk.CellRendererText(), text=2)
		column.set_sort_column_id(2)
		self.all_view.append_column(column)

		self.parent.notebook.connect('switch-page', self.do_recalc)
		self.calc_thread = None

		self.calc_progress = gtk.ProgressBar()
		self.parent.model_note_vbox.pack_start(self.calc_progress)

	def clear(self):
		self.all_view.get_model().clear()

	def do_recalc(self, notebook, page_NOUSE, page_num):
		if notebook.get_tab_label(notebook.get_nth_page(page_num)).get_text() == "Model":
			if not self.calc_thread or not self.calc_thread.is_alive():
				self.calc_thread = threading.Thread(target=self.repop)
			if not self.calc_thread.is_alive():
				self.calc_thread.start()

	def repop(self):
		gtk.gdk.threads_enter()
		self.calc_progress.set_fraction(0)
		self.calc_progress.set_text("Calculating...")		
		gtk.gdk.threads_leave()
		basic_pts = self.basic_model_calc("2011-07-01")
		eap_ppg = self.eap_model_calc("2011-07-01")

#		basic_pts_new = self.basic_model_calc()

#		summ = 0
#		for key in basic_pts.keys():
#			summ += math.pow(basic_pts[key] - basic_pts_new[key],2)
#		print "Avg:",math.sqrt(summ/len(basic_pts))

		gtk.gdk.threads_enter()
		season_id = self.parent.season_combo.get_id()
		all_list = self.all_view.get_model()
		all_list.clear()
		gtk.gdk.threads_leave()

		self.parent.cur.execute("SELECT team_id FROM team_season WHERE season_id = '" + str(season_id) + "'")
		gtk.gdk.threads_enter()
		for team in self.parent.cur.fetchall():
			self.parent.cur.execute("SELECT team_name FROM teams WHERE id = '" + str(team[0]) + "'")
			team_name = self.parent.cur.fetchone()[0]
			all_list.append( (team_name, basic_pts[team[0]], eap_ppg[team[0]]) )

		self.calc_progress.set_fraction(1)
		self.calc_progress.set_text("Calculation Complete")		
		gtk.gdk.threads_leave()


	def win_chance_calc(self, team_goals_base, opp_goals_base, team_exp_gf, opp_exp_gf):
		team_goals_adj = opp_goals_base - min(team_goals_base, opp_goals_base)
		opp_goals_adj = team_goals_base - min(team_goals_base, opp_goals_base)

		win_chance = 0.0
		for i in range(0,opp_goals_adj):
			win_chance += poisson_pmf(i, opp_exp_gf)

		for i in range(0,100):
			win_chance += poisson_pmf(i + opp_goals_adj, opp_exp_gf) * (1 - poisson_cdf(i + team_goals_adj, team_exp_gf))

		return win_chance

	def tie_chance_calc(self, team_goals_base, opp_goals_base, team_exp_gf, opp_exp_gf):
		team_goals_adj = opp_goals_base - min(team_goals_base, opp_goals_base)
		opp_goals_adj = team_goals_base - min(team_goals_base, opp_goals_base)

		tie_chance = 0.0
		for i in range(0,100):
			tie_chance += poisson_pmf(i + team_goals_adj, team_exp_gf) * poisson_pmf(i + opp_goals_adj, opp_exp_gf)

		return tie_chance

	def basic_model_calc(self, date = None):
		gtk.gdk.threads_enter()
		league_home_gf = self.parent.table_note.fetch_home_goals(date)
		league_away_gf = self.parent.table_note.fetch_away_goals(date)
		gtk.gdk.threads_leave()

		if(league_away_gf != 0):
			hfa_adj = math.sqrt(float(league_home_gf) / float(league_away_gf))
		else:
			hfa_adj = 1.0

		if(hfa_adj == 0):
			hfa_adj = 0.01

		gtk.gdk.threads_enter()
		season_id = self.parent.season_combo.get_id()
		if date == None:
			date_today = datetime.date.today()
			date = date_today.isoformat()
		gtk.gdk.threads_leave()

		team_points = {}
		team_gf = {}
		team_ga = {}
		team_gp = {}

		gtk.gdk.threads_enter()
		self.parent.cur.execute("SELECT team_id FROM team_season WHERE season_id = '" + str(season_id) + "'")
		for team in self.parent.cur.fetchall():
			team_points[team[0]] = self.parent.table_note.fetch_pts(int(team[0]), date)
			team_gf[team[0]] = float(self.parent.table_note.fetch_gf(int(team[0]), date))
			team_ga[team[0]] = float(self.parent.table_note.fetch_ga(int(team[0]), date))
			team_gp[team[0]] = float(self.parent.table_note.fetch_gp(int(team[0]), date))
		gtk.gdk.threads_leave()

		self.parent.cur.execute("SELECT home_id, away_id FROM games WHERE (season_id = '" + str(season_id) + "' AND (date > '" + date + "' OR played = 'FALSE'))")

		game_arr = self.parent.cur.fetchall()
		for game in game_arr:
			home = game[0]
			away = game[1]
			gtk.gdk.threads_enter()
			if(team_gp[home] == 0) or (team_gp[away] == 0):
				home_exp_gf = 0.0
				away_exp_gf = 0.0
			else:
				home_exp_gf = (team_gf[home] + team_ga[away]) /	(team_gp[home] + team_gp[away]) * hfa_adj
				away_exp_gf = (team_gf[away] + team_ga[home]) /	(team_gp[home] + team_gp[away]) / hfa_adj

			self.calc_progress.set_fraction(float(game_arr.index(game))/float(len(game_arr)))
			gtk.gdk.threads_leave()

			tie_chance = self.tie_chance_calc(0, 0, home_exp_gf, away_exp_gf)
			home_win_chance = self.win_chance_calc(0, 0, home_exp_gf, away_exp_gf)
			away_win_chance = self.win_chance_calc(0, 0, away_exp_gf, home_exp_gf)

			team_points[home] += 3.0 * home_win_chance + tie_chance
			team_points[away] += 3.0 * away_win_chance + tie_chance

		return team_points

	def eap_model_calc(self, date = None):
		gtk.gdk.threads_enter()
		season_id = self.parent.season_combo.get_id()
		gtk.gdk.threads_leave()
		if date == None:
			date_today = datetime.date.today()
			date = date_today.isoformat()

		team_ppg = {}
		self.parent.cur.execute("SELECT team_id FROM team_season WHERE season_id = '" + str(season_id) + "'")
		for team in self.parent.cur.fetchall():
			gtk.gdk.threads_enter()
			team_gp = float(self.parent.table_note.fetch_gp(int(team[0]), date))
			team_gf = float(self.parent.table_note.fetch_gf(int(team[0]), date))
			team_ga = float(self.parent.table_note.fetch_ga(int(team[0]), date))
			if(team_gp != 0):
				exp_gf = team_gf / team_gp
				exp_ga = team_ga / team_gp
			else:
				exp_gf = 0
				exp_ga = 0
			gtk.gdk.threads_leave()

			tie_chance = self.tie_chance_calc(0, 0, exp_gf, exp_ga)
			win_chance = self.win_chance_calc(0, 0, exp_gf, exp_ga)

			team_ppg[team[0]] = 3.0 * win_chance + tie_chance

		return team_ppg

class Base:
	def __init__(self):
		gtk.gdk.threads_init()

		self.db = sqlite3.connect("test.sqlite", check_same_thread = False)
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
		self.cur.execute("CREATE TABLE IF NOT EXISTS games (" +
				    "season_id INTEGER, " +
				    "date DATE, " +
				    "home_id INTEGER, " +
				    "home_goals INTEGER, " +
				    "home_pks INTEGER, " +
				    "away_id INTEGER, " +
				    "away_goals INTEGER, " +
				    "away_pks INTEGER, " +
				    "aet BOOL, " +
				    "pks BOOL, " +
				    "played BOOL, " +
				    "game_style INTEGER, " +
				    "id INTEGER PRIMARY KEY ASC)")

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

		self.games_note_vbox = gtk.VBox(spacing=10)
		self.games_note_vbox.set_border_width(5)
		self.notebook.append_page(self.games_note_vbox, gtk.Label("Games"))

		self.table_note_vbox = gtk.VBox(spacing=10)
		self.table_note_vbox.set_border_width(5)
		self.notebook.append_page(self.table_note_vbox, gtk.Label("Table"))

		self.model_note_vbox = gtk.VBox(spacing=10)
		self.model_note_vbox.set_border_width(5)
		self.notebook.append_page(self.model_note_vbox, gtk.Label("Model"))

		self.table_note = Table_Notebook(self)

		self.model_note = Model_Notebook(self)

		self.games_note = Games_Notebook(self)

		#### Update the combo boxes so the notebooks show the right data ####
		self.league_combo.update(self.league_combo.combo)
		self.season_combo.update(self.season_combo.combo)

		self.window.show_all()
		return



	def main(self):
		gtk.gdk.threads_enter()
		gtk.main()
		gtk.gdk.threads_leave()

if __name__ == "__main__":
	base = Base()
	base.main()
