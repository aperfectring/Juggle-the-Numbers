#!/usr/bin/python


import pygtk
pygtk.require('2.0')
import gtk
import gobject
import re
import traceback
import datetime
import math
import threading
import sys

### Import local modules
import League_Combo
import League_Notebook
import Season_Combo
import Season_Notebook
import JTN_db
import Conference_Combo
import Conference_Notebook
import Date_Calendar
import Teams_Notebook
import Games_Notebook
import Table_Notebook
import Model_Notebook
import Results_Notebook
import Guru_Notebook

### Gets team information tuple based on the team_id number
def get_team_from_id(cur, myid):
	cur.execute("SELECT team_name, city, abbr FROM teams WHERE id = '" + str(myid) + "'")
	name = None
	city = None
	abbr = None
	for row in cur:
		if row:
			name = row[0]
			city = row[1]
			abbr = row[2]
	return (name, city, abbr, myid)

### Gets team information tuple based on the team name
def get_team_from_name(cur, name):
	cur.execute("SELECT city, id, abbr FROM teams WHERE team_name = '" + name + "'")
	city = None
	myid = None
	abbr = None
	for row in cur:
		if row:
			city = row[0]
			myid = row[1]
			abbr = row[2]
	return (name, city, abbr, myid)

### Gets team information tuple based on the team name
def get_team_from_abbr(cur, abbr, season_id = None):
	cur.execute("SELECT city, id, team_name FROM teams WHERE abbr = '" + abbr + "'")
	city = None
	myid = None
	name = None
	for row in cur.fetchall():
		if row:
			if season_id:
				cur.execute("SELECT * FROM team_season WHERE team_id = '" + str(row[1]) + "' AND season_id = '" + season_id + "'")
				if len(cur.fetchall()) > 0:
					city = row[0]
					myid = row[1]
					name = row[2]
			else:
				city = row[0]
				myid = row[1]
				name = row[2]

	return (name, city, abbr, myid)




class Attendance_Notebook:
	def __init__(self, parent):
		self.parent = parent

		self.home_combo = gtk.combo_box_new_text()
		self.parent.atten_note_vbox.pack_start(self.home_combo, expand = False)
		self.home_combo.append_text("Home")
		self.home_combo.append_text("Away")
		self.home_combo.set_active(0)

		self.atten_hbox = gtk.HBox(spacing=10)
		self.atten_hbox.set_border_width(5)
		self.parent.atten_note_vbox.pack_start(self.atten_hbox, expand = False)

		self.oa_vbox = gtk.VBox(spacing=10)
		self.oa_vbox.set_border_width(5)
		self.atten_hbox.pack_start(self.oa_vbox)

		### Overall played
		self.oa_played_hbox = gtk.HBox(spacing=10)
		self.oa_played_hbox.set_border_width(5)
		self.oa_vbox.pack_start(self.oa_played_hbox, expand = False)

		self.oa_played_label = gtk.Label("Games Played:")
		self.oa_played_hbox.pack_start(self.oa_played_label)

		self.oa_played_entry = gtk.Entry()
		self.oa_played_entry.set_editable(False)
		self.oa_played_entry.set_width_chars(4)
		self.oa_played_hbox.pack_start(self.oa_played_entry)

		### Overall Attendance Count
		self.oa_count_hbox = gtk.HBox(spacing=10)
		self.oa_count_hbox.set_border_width(5)
		self.oa_vbox.pack_start(self.oa_count_hbox, expand = False)

		self.oa_count_label = gtk.Label("Total:")
		self.oa_count_hbox.pack_start(self.oa_count_label)

		self.oa_count_entry = gtk.Entry()
		self.oa_count_entry.set_editable(False)
		self.oa_count_entry.set_width_chars(10)
		self.oa_count_hbox.pack_start(self.oa_count_entry)

		### Overall Average Attendance
		self.oa_avg_hbox = gtk.HBox(spacing=10)
		self.oa_avg_hbox.set_border_width(5)
		self.oa_vbox.pack_start(self.oa_avg_hbox, expand = False)

		self.oa_avg_label = gtk.Label("Average:")
		self.oa_avg_hbox.pack_start(self.oa_avg_label)

		self.oa_avg_entry = gtk.Entry()
		self.oa_avg_entry.set_editable(False)
		self.oa_avg_entry.set_width_chars(6)
		self.oa_avg_hbox.pack_start(self.oa_avg_entry)

		### Overall Median Attendance
		self.oa_median_hbox = gtk.HBox(spacing=10)
		self.oa_median_hbox.set_border_width(5)
		self.oa_vbox.pack_start(self.oa_median_hbox, expand = False)

		self.oa_median_label = gtk.Label("Median:")
		self.oa_median_hbox.pack_start(self.oa_median_label)

		self.oa_median_entry = gtk.Entry()
		self.oa_median_entry.set_editable(False)
		self.oa_median_entry.set_width_chars(6)
		self.oa_median_hbox.pack_start(self.oa_median_entry)

		### Overall Max Attendance
		self.oa_max_hbox = gtk.HBox(spacing=10)
		self.oa_max_hbox.set_border_width(5)
		self.oa_vbox.pack_start(self.oa_max_hbox, expand = False)

		self.oa_max_label = gtk.Label("Max:")
		self.oa_max_hbox.pack_start(self.oa_max_label)

		self.oa_max_entry = gtk.Entry()
		self.oa_max_entry.set_editable(False)
		self.oa_max_entry.set_width_chars(7)
		self.oa_max_hbox.pack_start(self.oa_max_entry)

		### Overall Min Attendance
		self.oa_min_hbox = gtk.HBox(spacing=10)
		self.oa_min_hbox.set_border_width(5)
		self.oa_vbox.pack_start(self.oa_min_hbox, expand = False)

		self.oa_min_label = gtk.Label("Min:")
		self.oa_min_hbox.pack_start(self.oa_min_label)

		self.oa_min_entry = gtk.Entry()
		self.oa_min_entry.set_editable(False)
		self.oa_min_entry.set_width_chars(6)
		self.oa_min_hbox.pack_start(self.oa_min_entry)

		### Overall stddev Attendance
		self.oa_stddev_hbox = gtk.HBox(spacing=10)
		self.oa_stddev_hbox.set_border_width(5)
		self.oa_vbox.pack_start(self.oa_stddev_hbox, expand = False)

		self.oa_stddev_label = gtk.Label("Standard Deviation:")
		self.oa_stddev_hbox.pack_start(self.oa_stddev_label)

		self.oa_stddev_entry = gtk.Entry()
		self.oa_stddev_entry.set_editable(False)
		self.oa_stddev_entry.set_width_chars(6)
		self.oa_stddev_hbox.pack_start(self.oa_stddev_entry)

		self.oa_hsep = gtk.HSeparator()
		self.oa_vbox.pack_start(self.oa_hsep, expand = False)

		### Overall Range Attendance
		self.oa_range_label = gtk.Label("Games Within Range")
		self.oa_vbox.pack_start(self.oa_range_label, expand = False)

		self.oa_range_hbox = gtk.HBox(spacing=10)
		self.oa_range_hbox.set_border_width(5)
		self.oa_vbox.pack_start(self.oa_range_hbox, expand = False)

		self.oa_min_range_label = gtk.Label("Min:")
		self.oa_range_hbox.pack_start(self.oa_min_range_label)

		self.oa_min_range_spin = gtk.SpinButton()
		self.oa_min_range_spin.set_range(-1000000,1000000)
		self.oa_min_range_spin.set_increments(100,1000)
		self.oa_min_range_spin.set_value(0)
		self.oa_min_range_spin.set_width_chars(8)
		self.oa_range_hbox.pack_start(self.oa_min_range_spin)

		self.oa_max_range_label = gtk.Label("Max:")
		self.oa_range_hbox.pack_start(self.oa_max_range_label)

		self.oa_max_range_spin = gtk.SpinButton()
		self.oa_max_range_spin.set_range(-1000000,1000000)
		self.oa_max_range_spin.set_increments(100,1000)
		self.oa_max_range_spin.set_value(1000000)
		self.oa_max_range_spin.set_width_chars(7)
		self.oa_range_hbox.pack_start(self.oa_max_range_spin)

		self.oa_range_count_hbox = gtk.HBox(spacing=10)
		self.oa_range_count_hbox.set_border_width(5)
		self.oa_vbox.pack_start(self.oa_range_count_hbox, expand = False)

		self.oa_range_count_num_label = gtk.Label("Count:")
		self.oa_range_count_hbox.pack_start(self.oa_range_count_num_label)

		self.oa_range_count_num_entry = gtk.Entry()
		self.oa_range_count_num_entry.set_editable(False)
		self.oa_range_count_num_entry.set_width_chars(4)
		self.oa_range_count_hbox.pack_start(self.oa_range_count_num_entry)

		self.oa_range_count_percent_label = gtk.Label("Percentage:")
		self.oa_range_count_hbox.pack_start(self.oa_range_count_percent_label)

		self.oa_range_count_percent_entry = gtk.Entry()
		self.oa_range_count_percent_entry.set_editable(False)
		self.oa_range_count_percent_entry.set_width_chars(7)
		self.oa_range_count_hbox.pack_start(self.oa_range_count_percent_entry)

		self.vsep = gtk.VSeparator()
		self.atten_hbox.pack_start(self.vsep, expand = False)

		self.pt_vbox = gtk.VBox(spacing=10)
		self.pt_vbox.set_border_width(5)
		self.atten_hbox.pack_start(self.pt_vbox)

		### Per Team drop-menu
		self.pt_team_combo = gtk.combo_box_new_text()
		self.pt_vbox.pack_start(self.pt_team_combo, expand = False)

		### Per Team played
		self.pt_played_hbox = gtk.HBox(spacing=10)
		self.pt_played_hbox.set_border_width(5)
		self.pt_vbox.pack_start(self.pt_played_hbox, expand = False)

		self.pt_played_label = gtk.Label("Games Played:")
		self.pt_played_hbox.pack_start(self.pt_played_label)

		self.pt_played_entry = gtk.Entry()
		self.pt_played_entry.set_editable(False)
		self.pt_played_entry.set_width_chars(4)
		self.pt_played_hbox.pack_start(self.pt_played_entry)

		### Per Team Attendance Count
		self.pt_count_hbox = gtk.HBox(spacing=10)
		self.pt_count_hbox.set_border_width(5)
		self.pt_vbox.pack_start(self.pt_count_hbox, expand = False)

		self.pt_count_label = gtk.Label("Total:")
		self.pt_count_hbox.pack_start(self.pt_count_label)

		self.pt_count_entry = gtk.Entry()
		self.pt_count_entry.set_editable(False)
		self.pt_count_entry.set_width_chars(10)
		self.pt_count_hbox.pack_start(self.pt_count_entry)

		### Per Team Average Attendance
		self.pt_avg_hbox = gtk.HBox(spacing=10)
		self.pt_avg_hbox.set_border_width(5)
		self.pt_vbox.pack_start(self.pt_avg_hbox, expand = False)

		self.pt_avg_label = gtk.Label("Average:")
		self.pt_avg_hbox.pack_start(self.pt_avg_label)

		self.pt_avg_entry = gtk.Entry()
		self.pt_avg_entry.set_editable(False)
		self.pt_avg_entry.set_width_chars(6)
		self.pt_avg_hbox.pack_start(self.pt_avg_entry)

		### Per Team Median Attendance
		self.pt_median_hbox = gtk.HBox(spacing=10)
		self.pt_median_hbox.set_border_width(5)
		self.pt_vbox.pack_start(self.pt_median_hbox, expand = False)

		self.pt_median_label = gtk.Label("Median:")
		self.pt_median_hbox.pack_start(self.pt_median_label)

		self.pt_median_entry = gtk.Entry()
		self.pt_median_entry.set_editable(False)
		self.pt_median_entry.set_width_chars(6)
		self.pt_median_hbox.pack_start(self.pt_median_entry)

		### Per Team Max Attendance
		self.pt_max_hbox = gtk.HBox(spacing=10)
		self.pt_max_hbox.set_border_width(5)
		self.pt_vbox.pack_start(self.pt_max_hbox, expand = False)

		self.pt_max_label = gtk.Label("Max:")
		self.pt_max_hbox.pack_start(self.pt_max_label)

		self.pt_max_entry = gtk.Entry()
		self.pt_max_entry.set_editable(False)
		self.pt_max_entry.set_width_chars(7)
		self.pt_max_hbox.pack_start(self.pt_max_entry)

		### Per Team Min Attendance
		self.pt_min_hbox = gtk.HBox(spacing=10)
		self.pt_min_hbox.set_border_width(5)
		self.pt_vbox.pack_start(self.pt_min_hbox, expand = False)

		self.pt_min_label = gtk.Label("Min:")
		self.pt_min_hbox.pack_start(self.pt_min_label)

		self.pt_min_entry = gtk.Entry()
		self.pt_min_entry.set_editable(False)
		self.pt_min_entry.set_width_chars(6)
		self.pt_min_hbox.pack_start(self.pt_min_entry)

		### Per Team stddev Attendance
		self.pt_stddev_hbox = gtk.HBox(spacing=10)
		self.pt_stddev_hbox.set_border_width(5)
		self.pt_vbox.pack_start(self.pt_stddev_hbox, expand = False)

		self.pt_stddev_label = gtk.Label("Standard Deviation:")
		self.pt_stddev_hbox.pack_start(self.pt_stddev_label)

		self.pt_stddev_entry = gtk.Entry()
		self.pt_stddev_entry.set_editable(False)
		self.pt_stddev_entry.set_width_chars(6)
		self.pt_stddev_hbox.pack_start(self.pt_stddev_entry)

		self.pt_hsep = gtk.HSeparator()
		self.pt_vbox.pack_start(self.pt_hsep, expand = False)

		### Per Team Range Attendance
		self.pt_range_label = gtk.Label("Games Within Range")
		self.pt_vbox.pack_start(self.pt_range_label, expand = False)

		self.pt_range_hbox = gtk.HBox(spacing=10)
		self.pt_range_hbox.set_border_width(5)
		self.pt_vbox.pack_start(self.pt_range_hbox, expand = False)

		self.pt_min_range_label = gtk.Label("Min:")
		self.pt_range_hbox.pack_start(self.pt_min_range_label)

		self.pt_min_range_spin = gtk.SpinButton()
		self.pt_min_range_spin.set_range(-1000000,1000000)
		self.pt_min_range_spin.set_increments(100,1000)
		self.pt_min_range_spin.set_value(0)
		self.pt_min_range_spin.set_width_chars(8)
		self.pt_range_hbox.pack_start(self.pt_min_range_spin)

		self.pt_max_range_label = gtk.Label("Max:")
		self.pt_range_hbox.pack_start(self.pt_max_range_label)

		self.pt_max_range_spin = gtk.SpinButton()
		self.pt_max_range_spin.set_range(-1000000,1000000)
		self.pt_max_range_spin.set_increments(100,1000)
		self.pt_max_range_spin.set_value(1000000)
		self.pt_max_range_spin.set_width_chars(7)
		self.pt_range_hbox.pack_start(self.pt_max_range_spin)

		self.pt_range_count_hbox = gtk.HBox(spacing=10)
		self.pt_range_count_hbox.set_border_width(5)
		self.pt_vbox.pack_start(self.pt_range_count_hbox, expand = False)

		self.pt_range_count_num_label = gtk.Label("Count:")
		self.pt_range_count_hbox.pack_start(self.pt_range_count_num_label)

		self.pt_range_count_num_entry = gtk.Entry()
		self.pt_range_count_num_entry.set_editable(False)
		self.pt_range_count_num_entry.set_width_chars(4)
		self.pt_range_count_hbox.pack_start(self.pt_range_count_num_entry)

		self.pt_range_count_percent_label = gtk.Label("Percentage:")
		self.pt_range_count_hbox.pack_start(self.pt_range_count_percent_label)

		self.pt_range_count_percent_entry = gtk.Entry()
		self.pt_range_count_percent_entry.set_editable(False)
		self.pt_range_count_percent_entry.set_width_chars(7)
		self.pt_range_count_hbox.pack_start(self.pt_range_count_percent_entry)

		self.recalc_button = gtk.Button("Recalculate")
		self.parent.atten_note_vbox.pack_start(self.recalc_button, expand = False)
		self.recalc_button.connect('clicked', self.repop_button)

	### Add the appropriate teams (from the team_season table) to the specified combo box.
	def pop_team_combo(self, combo):
		row = None
		team_list = []
		self.parent.cur.execute("SELECT team_id FROM team_season WHERE (season_id='" + str(self.parent.season_combo.get_id()) + "')")
		for row in self.parent.cur.fetchall():
			self.parent.cur.execute("SELECT abbr FROM teams WHERE (id='" + str(row[0]) + "')")
			for name in self.parent.cur.fetchall():
				#combo.append_text(name[0])
				team_list.append(name[0])
		team_list.sort()
		for name in team_list:
			combo.append_text(name)

		if row:
			combo.set_active(0)

	def repop_button(self, button):
		self.repop()

	def repop(self):
		season_id = self.parent.season_combo.get_id()
		conf_id = self.parent.conf_combo.get_id()

		model = self.pt_team_combo.get_model()
		if len(model) > 0:
			index = self.pt_team_combo.get_active()
			per_team_info = get_team_from_abbr(self.parent.cur, model[index][0], str(season_id))
			for index in range(0, len(model)):
				self.pt_team_combo.remove_text(0)
		else:
			per_team_info = (None, None, None, None)

		model = self.home_combo.get_model()
		index = self.home_combo.get_active()
		if model[index][0] == "Home":
			calc_col_text = "home_id"
			oth_col_text = "away_id"
		else:
			calc_col_text = "away_id"
			oth_col_text = "home_id"

		date = self.parent.date_cal.get_date()
			
		oa_game_list = []
		if date == None:
			date_today = datetime.date.today()
			date = date_today.isoformat()
		if conf_id == None:
			self.parent.cur.execute("SELECT attendance FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "' AND attendance NOT NULL )")
		else:
			self.parent.cur.execute("SELECT attendance FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "' AND attendance NOT NULL AND " + calc_col_text + " IN (SELECT team_id FROM team_season WHERE (season_id = '" + str(season_id) + "' AND conf_id = '" + str(conf_id) + "') ) )")
		for row in self.parent.cur.fetchall():
			if row[0] != '':
				oa_game_list.append(int(row[0]))
		oa_game_list.sort()
		if len(oa_game_list) > 0:
			oa_attendance = sum(oa_game_list)
		else:
			oa_attendance = 0
		oa_games_played = len(oa_game_list)

		if oa_games_played == 0:
			oa_median = 0
			oa_max = 0
			oa_min = 0
			oa_average = 0
			oa_stddev = 0
			oa_range_count_num = 0
			oa_range_count_percent = 0.0
		elif oa_games_played % 2 == 0:
			oa_median = int(round(float(oa_game_list[oa_games_played / 2] + oa_game_list[oa_games_played / 2 - 1])/2,0))
		else:
			oa_median = oa_game_list[oa_games_played / 2]

		if oa_games_played != 0:
			oa_max = max(oa_game_list)
			oa_min = min(oa_game_list)

			oa_dev_list = []
			oa_average = float(oa_attendance)/float(oa_games_played)
			oa_range_min = self.oa_min_range_spin.get_value()
			oa_range_max = self.oa_max_range_spin.get_value()
			if oa_range_min < 0:
				oa_range_min = oa_average + oa_range_min
				oa_range_max = oa_average + oa_range_max
			oa_range_count_num = 0
			for game in oa_game_list:
				oa_dev_list.append(pow(float(game) - float(int(oa_average)), 2))
				if game >= oa_range_min:
					if game <= oa_range_max:
						oa_range_count_num += 1
			oa_stddev = pow(sum(oa_dev_list)/oa_games_played , 0.5)
			oa_range_count_percent = float(oa_range_count_num) / float(oa_games_played) * float(100)
			

		self.oa_played_entry.set_text(str(oa_games_played))
		self.oa_count_entry.set_text(str(oa_attendance))
		self.oa_avg_entry.set_text(str(int(round(oa_average,0))))
		self.oa_median_entry.set_text(str(oa_median))
		self.oa_max_entry.set_text(str(oa_max))
		self.oa_min_entry.set_text(str(oa_min))
		self.oa_stddev_entry.set_text(str(int(round(oa_stddev,0))))
		self.oa_range_count_num_entry.set_text(str(oa_range_count_num))
		self.oa_range_count_percent_entry.set_text("{}%".format(round(oa_range_count_percent,1)))

		if per_team_info[3]:
			pt_game_list = []
			if conf_id == None:
				self.parent.cur.execute("SELECT attendance FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "' AND attendance NOT NULL AND " + calc_col_text + " = '" + str(per_team_info[3]) + "')")
			else:
				self.parent.cur.execute("SELECT attendance FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "' AND attendance NOT NULL AND " + calc_col_text + " = '" + str(per_team_info[3]) + "' AND " + oth_col_text + " IN (SELECT team_id FROM team_season WHERE (season_id = '" + str(season_id) + "' AND conf_id = '" + str(conf_id) + "') ) )")

			for row in self.parent.cur.fetchall():
				if row[0] != '':
					pt_game_list.append(row[0])
			pt_game_list.sort()
			if len(pt_game_list) > 0:
				pt_attendance = sum(pt_game_list)
			else:
				pt_attendance = 0
			pt_games_played = len(pt_game_list)

			if pt_games_played == 0:
				pt_median = 0
				pt_max = 0
				pt_min = 0
				pt_average = 0
				pt_stddev = 0
				pt_range_count_num = 0
				pt_range_count_percent = 0.0
			elif pt_games_played % 2 == 0:
				pt_median = (pt_game_list[pt_games_played / 2] + pt_game_list[pt_games_played / 2 - 1])/2
			else:
				pt_median = pt_game_list[pt_games_played / 2]

			if pt_games_played != 0:
				pt_max = max(pt_game_list)
				pt_min = min(pt_game_list)

				pt_dev_list = []
				pt_average = float(pt_attendance)/float(pt_games_played)
				pt_range_min = self.pt_min_range_spin.get_value()
				pt_range_max = self.pt_max_range_spin.get_value()
				if pt_range_min < 0:
					pt_range_min = pt_average + pt_range_min
					pt_range_max = pt_average + pt_range_max
				pt_range_count_num = 0
				for game in pt_game_list:
					pt_dev_list.append(pow(float(game) - float(int(pt_average)), 2))
					if game >= pt_range_min:
						if game <= pt_range_max:
							pt_range_count_num += 1
				pt_stddev = pow(sum(pt_dev_list)/pt_games_played , 0.5)
				pt_range_count_percent = float(pt_range_count_num) / float(pt_games_played) * float(100)
			
		else:
			pt_games_played = 0
			pt_attendance = 0
			pt_median = 0
			pt_max = 0
			pt_min = 0
			pt_average = 0
			pt_stddev = 0
			pt_range_count_num = 0
			pt_range_count_percent = 0.0

		self.pt_played_entry.set_text(str(pt_games_played))
		self.pt_count_entry.set_text(str(pt_attendance))
		self.pt_avg_entry.set_text(str(int(round(pt_average,0))))
		self.pt_median_entry.set_text(str(pt_median))
		self.pt_max_entry.set_text(str(pt_max))
		self.pt_min_entry.set_text(str(pt_min))
		self.pt_stddev_entry.set_text(str(int(round(pt_stddev,0))))
		self.pt_range_count_num_entry.set_text(str(pt_range_count_num))
		self.pt_range_count_percent_entry.set_text("{}%".format(round(pt_range_count_percent,1)))




		self.pop_team_combo(self.pt_team_combo)
		model = self.pt_team_combo.get_model()
		self.pt_team_combo.set_active(0)

		if per_team_info:
			for index in range(0,len(model)):
				if model[index][0] == per_team_info[2]:
					self.pt_team_combo.set_active(index)

	### Fetch the games played by the team up to and including the specified date
	def fetch_gp(self, team, date = None):
		if date == None:
			date_today = datetime.date.today()
			date = date_today.isoformat()
		season_id = self.parent.season_combo.get_id()
		self.parent.cur.execute("SELECT COUNT(*) FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "' AND home_id = '" + str(team) + "' AND attendance NOT NULL )")
		games_played = self.parent.cur.fetchone()[0]
		return games_played

	def fetch_att(self, team, date = None):
		if date == None:
			date_today = datetime.date.today()
			date = date_today.isoformat()
		season_id = self.parent.season_combo.get_id()
		self.parent.cur.execute("SELECT SUM(attendance) FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "' AND home_id = '" + str(team) + "' AND attendance NOT NULL )")
		attendance = self.parent.cur.fetchone()[0]
		if attendance:
			return attendance
		return 0

class Base:
	def __init__(self, dbname = None):
		gtk.gdk.threads_init()

		self.JTN_db = JTN_db.JTN_db()
		(self.db, self.cur) = self.JTN_db.open(dbname)

		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect('destroy', lambda w: gtk.main_quit())

		self.window_vbox = gtk.VBox(spacing=10)
		self.window_vbox.set_border_width(5)
		self.window.add(self.window_vbox)

		self.combo_hbox = gtk.HBox(spacing=10)
		self.window_vbox.pack_start(self.combo_hbox, expand = False)
		self.combo_vbox = gtk.VBox(spacing=5)
		self.combo_hbox.pack_start(self.combo_vbox, expand = False)

		self.league_vbox = gtk.VBox(spacing=5)
		self.combo_vbox.add(self.league_vbox)

		self.league_combo = League_Combo.League_Combo(self.league_vbox, self.JTN_db)
		
		self.season_vbox = gtk.VBox(spacing=5)
		self.combo_vbox.add(self.season_vbox)

		self.season_combo = Season_Combo.Season_Combo(self.season_vbox, self.JTN_db, self.league_combo.get_id)

		# When the League Combo selection changes,
		# the Season Combo needs to be repopulated
		self.league_combo.register(self.season_combo.repop)

		self.conference_vbox = gtk.VBox(spacing=5)
		self.combo_vbox.add(self.conference_vbox)

		self.conf_combo = Conference_Combo.Conference_Combo(self.conference_vbox, self.JTN_db, self.season_combo.get_id)

		self.date_vbox = gtk.VBox(spacing=5)
		self.combo_hbox.pack_start(self.date_vbox, expand=False)
		self.date_cal = Date_Calendar.Date_Calendar(self.date_vbox)

		self.notebook = gtk.Notebook()
		self.window_vbox.add(self.notebook)

		#### Add Notebook Pages ####
		self.league_note_vbox = gtk.VBox(spacing=10)
		self.league_note_vbox.set_border_width(5)
		self.notebook.append_page(self.league_note_vbox, gtk.Label("League"))

		self.league_note = League_Notebook.League_Notebook(self.league_note_vbox, self.JTN_db, self.league_combo.get_selected)

		# When the League Combo selection changes,
		# the League Notebook needs to be repopulated
		self.league_combo.register(self.league_note.repop)

		# When the League Notebook updates the DB,
		# the League Combo needs to be repopulated
		self.league_note.register(self.league_combo.repop)

		self.season_note_vbox = gtk.VBox(spacing=10)
		self.season_note_vbox.set_border_width(5)
		self.notebook.append_page(self.season_note_vbox, gtk.Label("Season"))

		self.season_note = Season_Notebook.Season_Notebook(self.season_note_vbox, self.JTN_db, self.season_combo.get_id)

		# When the Season Combo selection changes,
		# the Season Notebook needs to be repopulated
		self.season_combo.register(self.season_note.repop)

		# When the Season Notebook updates the DB,
		# the Season Combo needs to be repopulated
		self.season_note.register(self.season_combo.repop)

		self.confs_note_vbox = gtk.VBox(spacing=10)
		self.confs_note_vbox.set_border_width(5)
		self.notebook.append_page(self.confs_note_vbox, gtk.Label("Confs"))

		self.conf_note = Conference_Notebook.Conference_Notebook(self.confs_note_vbox, self.JTN_db, self.season_combo.get_id)

		# When the Season Combo selection changes,
		# the Conference Notebook needs to be repopulated
		self.season_combo.register(self.conf_note.repop)

		# When the Conference Notebook updates (repop),
		# the Conference Combo needs to be repopulated
		self.conf_note.register(self.conf_combo.repop)

		self.teams_note_vbox = gtk.VBox(spacing=10)
		self.teams_note_vbox.set_border_width(5)
		self.notebook.append_page(self.teams_note_vbox, gtk.Label("Teams"))

		self.teams_note = Teams_Notebook.Teams_Notebook(self.teams_note_vbox, self.JTN_db, self.season_combo.get_id)

		# When the Conference Combo selection changes,
		# the Teams Notebook needs to be repopulated
		self.conf_combo.register(self.teams_note.repop)

		self.games_note_vbox = gtk.VBox(spacing=10)
		self.games_note_vbox.set_border_width(5)
		self.notebook.append_page(self.games_note_vbox, gtk.Label("Games"))

		self.table_note_vbox = gtk.VBox(spacing=10)
		self.table_note_vbox.set_border_width(5)
		self.notebook.append_page(self.table_note_vbox, gtk.Label("Table"))

		self.model_note_vbox = gtk.VBox(spacing=10)
		self.model_note_vbox.set_border_width(5)
		self.notebook.append_page(self.model_note_vbox, gtk.Label("Model"))

		self.table_note = Table_Notebook.Table_Notebook(self.table_note_vbox, self.season_combo.get_id, self.conf_combo.get_id, self.date_cal.get_date, self.JTN_db)

		# When the Teams Notebook updates,
		# the Table Notebook needs to be repopulated.
		self.teams_note.register(self.table_note.repop)

		self.model_note = Model_Notebook.Model_Notebook(self.model_note_vbox, self.season_combo.get_id, self.conf_combo.get_id, self.date_cal.get_date, self.JTN_db)

		# When the Teams Notebook updates,
		# the Model Notebook needs to be repopulated.
		self.teams_note.register(self.model_note.clear)

		self.games_note = Games_Notebook.Games_Notebook(self.games_note_vbox, self.JTN_db, self.season_combo.get_id)

		# When the Conference Combo selection changes,
		# the Games Notebook needs to be repopulated
		self.conf_combo.register(self.games_note.repop)

		# When the Date Calendar selection changes,
		# the Games Notebook needs to be repopulated
		self.date_cal.register(self.games_note.repop)

		# When the Games Notebook is updated,
		# the Table Notebook needs to be repopulated
		self.games_note.register(self.table_note.repop)

		# When the Games Notebook is updated,
		# the Model Notebook needs to be repopulated
		self.games_note.register(self.model_note.clear)

		self.results_note_vbox = gtk.VBox(spacing=10)
		self.results_note_vbox.set_border_width(5)
		self.notebook.append_page(self.results_note_vbox, gtk.Label("Results"))
		self.results_note = Results_Notebook.Results_Notebook(self.results_note_vbox, self.season_combo.get_id, self.JTN_db)

		# When the Games Notebook is updated,
		# the Results Notebook needs to be repopulated
		self.games_note.register(self.results_note.repop)

		self.guru_note_vbox = gtk.VBox(spacing=10)
		self.guru_note_vbox.set_border_width(5)
		self.notebook.append_page(self.guru_note_vbox, gtk.Label("Guru"))
		self.guru_note = Guru_Notebook.Guru_Notebook(self)

		# When the Games Notebook is updated,
		# the Guru Notebook needs to be repopulated
		self.games_note.register(self.guru_note.clear)

		self.atten_note_vbox = gtk.VBox(spacing=10)
		self.atten_note_vbox.set_border_width(5)
		self.notebook.append_page(self.atten_note_vbox, gtk.Label("Attendance"))
		self.atten_note = Attendance_Notebook(self)

		# When the Games Notebook is updated,
		# the Attendance Notebook needs to be repopulated
		self.games_note.register(self.atten_note.repop)


		self.league_combo.repop()
		self.window.show_all()
		self.model_note.calc_progress.set_visible(False)

		return



	def main(self):
		gtk.gdk.threads_enter()
		gtk.main()
		gtk.gdk.threads_leave()

if __name__ == "__main__":
	if len(sys.argv) > 1:
		base = Base(sys.argv[1])
	else:
		base = Base()
	base.main()
