import pygtk
pygtk.require('2.0')
import gtk
import gobject
import sqlite3
import re
import traceback

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

		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect('destroy', lambda w: gtk.main_quit())

		self.window_vbox = gtk.VBox(spacing=10)
		self.window_vbox.set_border_width(5)
		self.window.add(self.window_vbox)

		self.combo_hbox = gtk.HBox(spacing=10)
		self.window_vbox.add(self.combo_hbox)

		self.league_vbox = gtk.VBox(spacing=5)
		self.combo_hbox.add(self.league_vbox)

		self.league_label = gtk.Label("League:")
		self.league_vbox.add(self.league_label)

		self.league_combo = gtk.combo_box_new_text()
		self.cur.execute("SELECT league_name FROM leagues")
                for row in self.cur:
			print row
			self.league_combo.append_text(row[0])
		self.league_vbox.add(self.league_combo)
		self.league_combo.connect('changed', self.league_combo_changed)

		self.league_button = gtk.Button("Add League")
		self.league_vbox.add(self.league_button)
		self.league_button.connect('clicked', self.league_button_clicked)

		self.season_vbox = gtk.VBox(spacing=5)
		self.combo_hbox.add(self.season_vbox)

		self.season_label = gtk.Label("Season:")
		self.season_vbox.add(self.season_label)

		self.season_combo = gtk.combo_box_new_text()
		self.season_vbox.add(self.season_combo)
		self.season_combo.connect('changed', self.season_combo_changed)

		self.season_button = gtk.Button("Add Season")
		self.season_vbox.add(self.season_button)
		self.season_button.connect('clicked', self.season_button_clicked)

		self.notebook = gtk.Notebook()
		self.window_vbox.add(self.notebook)

		self.team_vbox = gtk.VBox(spacing=5)
		self.combo_hbox.add(self.team_vbox)

		self.team_label = gtk.Label("Team:")
		self.team_vbox.add(self.team_label)

		self.team_combo = gtk.combo_box_new_text()
		self.team_vbox.add(self.team_combo)

		self.team_button = gtk.Button("Add Team")
		self.team_vbox.add(self.team_button)

		#########  League Notebook Page  #########
		self.league_note_vbox = gtk.VBox(spacing=10)
		self.league_note_vbox.set_border_width(5)
		self.notebook.append_page(self.league_note_vbox, gtk.Label("League"))

		self.league_name_hbox = gtk.HBox(spacing=10)
		self.league_name_hbox.set_border_width(5)
		self.league_note_vbox.pack_start(self.league_name_hbox, expand=False)

		self.league_name_label = gtk.Label("Name:")
		self.league_name_hbox.add(self.league_name_label)

		self.league_name_entry = gtk.Entry()
		self.league_name_hbox.add(self.league_name_entry)

		self.league_country_hbox = gtk.HBox(spacing=10)
		self.league_country_hbox.set_border_width(5)
		self.league_note_vbox.pack_start(self.league_country_hbox, expand=False)

		self.league_country_label = gtk.Label("Country:")
		self.league_country_hbox.add(self.league_country_label)

		self.league_country_oldname = gtk.Label()

		self.league_country_entry = gtk.Entry()
		self.league_country_hbox.add(self.league_country_entry)

		self.league_confed_hbox = gtk.HBox(spacing=10)
		self.league_confed_hbox.set_border_width(5)
		self.league_note_vbox.pack_start(self.league_confed_hbox, expand=False)

		self.league_confed_label = gtk.Label("Confederation:")
		self.league_confed_hbox.add(self.league_confed_label)

		self.league_confed_entry = gtk.Entry()
		self.league_confed_hbox.add(self.league_confed_entry)

		self.league_level_hbox = gtk.HBox(spacing=10)
		self.league_level_hbox.set_border_width(5)
		self.league_note_vbox.pack_start(self.league_level_hbox, expand=False)

		self.league_level_label = gtk.Label("League Level:")
		self.league_level_hbox.add(self.league_level_label)

		self.league_level_entry = gtk.Entry()
		self.league_level_hbox.add(self.league_level_entry)

		self.league_note_update = gtk.Button("Update")
		self.league_note_vbox.pack_end(self.league_note_update, expand=False)
		self.league_note_update.connect('clicked', self.league_update_clicked)
		
		#########  Season Notebook Page  #########
		self.season_note_vbox = gtk.VBox(spacing=10)
		self.season_note_vbox.set_border_width(5)
		self.notebook.append_page(self.season_note_vbox, gtk.Label("Season"))

		self.season_start_hbox = gtk.HBox(spacing=10)
		self.season_start_hbox.set_border_width(5)
		self.season_note_vbox.add(self.season_start_hbox)

		self.season_start_label = gtk.Label("Start Date:")
		self.season_start_hbox.add(self.season_start_label)

		self.season_start_cal = gtk.Calendar()
		self.season_start_hbox.add(self.season_start_cal)

		self.season_end_hbox = gtk.HBox(spacing=10)
		self.season_end_hbox.set_border_width(5)
		self.season_note_vbox.add(self.season_end_hbox)

		self.season_end_label = gtk.Label("Start Date:")
		self.season_end_hbox.add(self.season_end_label)

		self.season_end_cal = gtk.Calendar()
		self.season_end_hbox.add(self.season_end_cal)

		self.season_note_update = gtk.Button("Update")
		self.season_note_vbox.pack_start(self.season_note_update, expand=False)
		self.season_note_update.connect('clicked', self.season_update_clicked)

		########### Team Notebook Page #############
		self.team_note_vbox = gtk.VBox(spacing=10)
		self.team_note_vbox.set_border_width(5)
		self.notebook.append_page(self.team_note_vbox, gtk.Label("Team"))

		self.team_name_hbox = gtk.HBox(spacing=10)
		self.team_name_hbox.set_border_width(5)
		self.team_note_vbox.pack_start(self.team_name_hbox, expand=False)

		self.team_name_label = gtk.Label("Name:")
		self.team_name_hbox.add(self.team_name_label)

		self.team_name_combo_entry = gtk.ComboBoxEntry()
		self.team_name_hbox.add(self.team_name_combo_entry)

		self.team_city_hbox = gtk.HBox(spacing=10)
		self.team_city_hbox.set_border_width(5)
		self.team_note_vbox.pack_start(self.team_city_hbox, expand=False)

		self.team_city_label = gtk.Label("City:")
		self.team_city_hbox.add(self.team_city_label)

		self.team_city_entry = gtk.Entry()
		self.team_city_hbox.add(self.team_city_entry)

		self.team_note_update = gtk.Button("Update")
		self.team_note_vbox.pack_end(self.team_note_update, expand=False)

		self.window.show_all()
		return

	### Determine the League Unique database ID based on the currently selected league from the combobox
	def get_league_id(self):
		model = self.league_combo.get_model()
		index = self.league_combo.get_active()
		self.cur.execute("SELECT id FROM leagues WHERE league_name = '" + model[index][0] + "'")
		for row in self.cur:
			if row != None and row[0] != None:
				return row[0]
			else:
				return None

	### Determine the Season Unique database ID based on the currently selected season from the combobox	
	def get_season_id(self):
		model = self.season_combo.get_model()
		index = self.season_combo.get_active()
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
			self.cur.execute("SELECT id FROM seasons " + 
                                            "WHERE STRFTIME('%Y',end) = '" + season_end + "' " + 
                                            "AND STRFTIME('%Y',start) = '" + season_start + "' " + 
                                            "AND league = '" + str(league_id) + "'")
		else:
			self.cur.execute("SELECT id FROM seasons WHERE end IS NULL AND start IS NULL")

		for row in self.cur:
			if row != None and row[0] != None:
				return row[0]
			else:
				return None

	### Callback handler for when the season combobox changes
	###   Updates the season notebook page
	def season_combo_changed(self, combobox):
		### We will get this callback when we are deleting all entries in the season combobox, so we
		###   only want to actually try to update the notebook page if we are changing to a valid
		###   index
		index = self.season_combo.get_active()
		if(index < 0):
			return

		season_id = self.get_season_id()

		### Decode the starting year month and day from the season entry in the database		
		self.cur.execute("SELECT STRFTIME('%Y',start), STRFTIME('%m',start), STRFTIME('%d',start) " + 
                                    "FROM seasons WHERE id = '" + str(season_id) + "'")
		for row in self.cur:
			if row != None:
				year = row[0]
				month = row[1]
				day = row[2]
		if (month != None) and (year != None):
			self.season_start_cal.select_month(int(month)-1, int(year))
			if(day != None):
				self.season_start_cal.select_day(int(day))

		### Decode the ending year month and day from the season entry in the database		
		self.cur.execute("SELECT STRFTIME('%Y',end), STRFTIME('%m',end), STRFTIME('%d',end) " + 
                                    "FROM seasons WHERE id = '" + str(season_id) + "'")
		for row in self.cur:
			if row != None:
				year = row[0]
				month = row[1]
				day = row[2]
		if (month != None) and (year != None):
			self.season_end_cal.select_month(int(month)-1, int(year))
			if(day != None):
				self.season_end_cal.select_day(int(day))

	### Callback for when the "Add season" button is clicked"
	###    This will create a "blank" season, which has no start or end date
	###    This will leavue the created season as the selected one
	def season_button_clicked(self, button):
		league_id = self.get_league_id()
		self.cur.execute("INSERT INTO seasons (league) VALUES ('" + str(league_id) + "')")
		self.db.commit()
		self.repop_season_combo('')

	### Callback for the "Update" button on the season notebook page
	###    This writes the currently selected dates into the database, and updates the combobox with the
	###    appropriate date range.
	def season_update_clicked(self, button):
		season_id = self.get_season_id()
		start_date = self.season_start_cal.get_date()
		end_date = self.season_end_cal.get_date()
		self.cur.execute("UPDATE seasons SET " + 
                                    "start = DATE('" + 
                                       str(start_date[0]) + "-" + 
                                       str(start_date[1]+1).zfill(2) + "-" + 
                                       str(start_date[2]).zfill(2) + "'), " + 
                                    "end = DATE('" + 
                                       str(end_date[0]) + "-" + 
                                       str(end_date[1]+1).zfill(2) + "-" + 
                                       str(end_date[2]).zfill(2) + "') " + 
                                    "WHERE id = '" + str(season_id) + "'")
		self.db.commit()

		model = self.season_combo.get_model()
		index = self.season_combo.get_active()
		if(start_date[0] == end_date[0]):
			model[index][0] = str(start_date[0])
		else:
			model[index][0] = str(start_date[0]) + "-" + str(end_date[0])

	### Callback for when the league combobox is changed
	###    Updates the league notebook page.
	###    Also deletes all entries from the season combobox, then adds the appropriate ones for this league
	def league_combo_changed(self, combobox):
		model = combobox.get_model()
		index = combobox.get_active()
		self.league_name_entry.set_text(model[index][0])
		self.league_country_oldname.set_label(model[index][0])

		### Fetches all the league information from the database
		self.cur.execute("SELECT country, confederation, level " + 
                                    "FROM leagues WHERE league_name = '" + model[index][0] + "'")
		self.league_country_entry.set_text("")
		self.league_confed_entry.set_text("")
		self.league_level_entry.set_text("")
                for row in self.cur:
			if row != None:
				if row[0] != None:
					self.league_country_entry.set_text(row[0])
				if row[1] != None:
					self.league_confed_entry.set_text(row[1])
				if row[2] != None:
					self.league_level_entry.set_text(str(row[2]))

		### Delete all season combobox entries, then populate the combobox with appropriate ones for this league
		self.repop_season_combo()
		return

	### Deletes all season combobox entries, then repopulates the combobox with appriopriate ones for this season
	###   Will attempt to select an entry which has the value of select_val, if specified
	def repop_season_combo(self, select_val = None):
		league_id = self.get_league_id()
		model = self.season_combo.get_model()
		for index in range(0, len(model)):
			self.season_combo.remove_text(0)

		self.cur.execute("SELECT STRFTIME('%Y', start), STRFTIME('%Y', end) " + 
                                    "FROM seasons " + 
                                    "WHERE league = '" + str(league_id) + "' " + 
                                    "ORDER BY end DESC")
		for row in self.cur:
			if row != None and row[0] != None and row[1] != None:
				if row[0] == row[1]:
					self.season_combo.append_text(row[0])
				else:
					self.season_combo.append_text(row[0] + "-" + row[1])
			elif row != None:
				self.season_combo.append_text("")
		model = self.season_combo.get_model()
		if select_val != None:
			for index in range(0, len(model)):
				if model[index][0] == select_val:
					self.season_combo.set_active(index)
					return
		if(len(model)>0):
			self.season_combo.set_active(0)
		return						

	### Callback for the "Update" button on the league notebook page
	###    Commits all data from the league notebook page to the database
	###    Updates the league combobox string to reflect any changes made
	def league_update_clicked(self, button):
		self.cur.execute("UPDATE leagues " + 
                                    "SET country = '" + self.league_country_entry.get_text() + "', " + 
                                       "league_name = '" + self.league_name_entry.get_text() + "', " + 
                                       "confederation = '" + self.league_confed_entry.get_text() + "', " + 
                                       "level = '" + self.league_level_entry.get_text() + "' " + 
                                    "WHERE league_name = '" + self.league_country_oldname.get_label() + "'")
		self.db.commit()

		index = self.league_combo.get_active()
		model = self.league_combo.get_model()
		model[index][0] = self.league_name_entry.get_text()
		

	### Callback for the "Add league" button
	###    This will create a "blank" league
	###    This will leave the newly created league as the currently selected one
	def league_button_clicked(self, button):
		text = ""
		try:
			self.cur.execute("INSERT INTO leagues (league_name)VALUES ('" + text + "')")
		except sqlite3.IntegrityError:
			model = self.league_combo.get_model()

		self.league_combo.append_text(text)
		model = self.league_combo.get_model()
		for index in range(0,len(model)):
			if (model[index][0] == text):
				self.league_combo.set_active(index)

		self.db.commit()

	def main(self):
		gtk.main()

if __name__ == "__main__":
	base = Base()
	base.main()
