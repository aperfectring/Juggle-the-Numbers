
import gtk
import gobject
import math

class Guru_Notebook:
	def __init__(self, parent, parent_box, JTN_db):
		self.parent = parent
		self.parent_box = parent_box
		self.JTN_db = JTN_db

		self.cal_hbox = gtk.HBox(spacing=10)
		self.cal_hbox.set_border_width(5)
		self.parent_box.pack_start(self.cal_hbox, expand = False)		

		self.start_vbox = gtk.VBox(spacing=10)
		self.start_vbox.set_border_width(5)
		self.cal_hbox.pack_start(self.start_vbox, expand = False)

		self.start_label = gtk.Label("Start date:")
		self.start_vbox.pack_start(self.start_label)

		self.start_cal = gtk.Calendar()
		self.start_vbox.pack_start(self.start_cal, expand = False)

		self.end_vbox = gtk.VBox(spacing=10)
		self.end_vbox.set_border_width(5)
		self.cal_hbox.pack_start(self.end_vbox, expand = False)

		self.end_label = gtk.Label("End date:")
		self.end_vbox.pack_start(self.end_label)

		self.end_cal = gtk.Calendar()
		self.end_vbox.pack_end(self.end_cal, expand = False)


		season_id = self.parent.season_combo.get_id()

		### Set the initial dates for the GURU display
		self.parent.cur.execute("SELECT STRFTIME('%Y',start), STRFTIME('%m',start), STRFTIME('%d',start), STRFTIME('%Y',end), STRFTIME('%m',end), STRFTIME('%d',end) FROM seasons WHERE id = '" + str(season_id) + "'")
		row = self.parent.cur.fetchone()
		if row != None:
			datetime_start_season = datetime.date(int(row[0]), int(row[1]), int(row[2]))
			datetime_end_season = datetime.date(int(row[3]), int(row[4]), int(row[5]))
			datetime_today = datetime.date.today()
			### If today is outside the bounds of the season, use the season start date as
			###   the start of the date range.  Otherwise, use today.
			if datetime_today < datetime_start_season or datetime_today > datetime_end_season:
				datetime_start_range = datetime_start_season
			else:
				datetime_start_range = datetime_today
			### Set the default length of the range to be 7 days.
			datetime_end_range = datetime_start_range + datetime.timedelta(7)
			
			self.start_cal.select_month(datetime_start_range.month-1, datetime_start_range.year)
			self.start_cal.select_day(datetime_start_range.day)

			self.end_cal.select_month(datetime_end_range.month-1, datetime_end_range.year)
			self.end_cal.select_day(datetime_end_range.day)

		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.parent_box.pack_start(scrolled_window)

		list_store = gtk.ListStore(gobject.TYPE_STRING,		# Date
						gobject.TYPE_STRING,	# Home Team
						gobject.TYPE_STRING,	# Away Team
						gobject.TYPE_FLOAT,	# Home Win %
						gobject.TYPE_FLOAT,	# Tie %
						gobject.TYPE_FLOAT,	# Away Win %
						gobject.TYPE_STRING,	# Most Likely Result
						gobject.TYPE_STRING,	# NASL Guru Result Home Win
						gobject.TYPE_FLOAT,	# NASL Guru Expected Points Home Win
						gobject.TYPE_STRING,	# NASL Guru Result Away Win
						gobject.TYPE_FLOAT,	# NASL Guru Expected Points Away Win
						gobject.TYPE_STRING,	# NASL Guru Result Tie
						gobject.TYPE_FLOAT)	# NASL Guru Expected Points Tie

		self.all_view = gtk.TreeView()
		scrolled_window.add(self.all_view)
		self.all_view.set_model(list_store)

		column = gtk.TreeViewColumn("Date", gtk.CellRendererText(), text=0)
		column.set_sort_column_id(0)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Home", gtk.CellRendererText(), text=1)
		column.set_sort_column_id(1)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Away", gtk.CellRendererText(), text=2)
		column.set_sort_column_id(2)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Home Win %", gtk.CellRendererText(), text=3)
		column.set_sort_column_id(3)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Tie %", gtk.CellRendererText(), text=4)
		column.set_sort_column_id(4)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Away Win %", gtk.CellRendererText(), text=5)
		column.set_sort_column_id(5)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Most Likely Result", gtk.CellRendererText(), text=6)
		column.set_sort_column_id(6)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Guru\nBest Result\nHome Win", gtk.CellRendererText(), text=7)
		column.set_sort_column_id(7)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Guru\nExpected Points\nHome Win", gtk.CellRendererText(), text=8)
		column.set_sort_column_id(8)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Guru\nBest Result\nAway Win", gtk.CellRendererText(), text=9)
		column.set_sort_column_id(9)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Guru\nExpected Points\nAway Win", gtk.CellRendererText(), text=10)
		column.set_sort_column_id(10)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Guru\nBest Result\nTie", gtk.CellRendererText(), text=11)
		column.set_sort_column_id(11)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Guru\nExpected Points\nTie", gtk.CellRendererText(), text=12)
		column.set_sort_column_id(12)
		self.all_view.append_column(column)

		self.recalc_button = gtk.Button("Recalculate")
		self.parent_box.pack_start(self.recalc_button, expand = False)
		self.recalc_button.connect('clicked', self.repop)

		self.hg_label = gtk.Label("HG:")
		self.ag_label = gtk.Label("AG:")
		self.hg_spin = gtk.SpinButton()
		self.hg_spin.set_range(0,100)
		self.hg_spin.set_increments(1,1)
		self.ag_spin = gtk.SpinButton()
		self.ag_spin.set_range(0,100)
		self.ag_spin.set_increments(1,1)
		self.goals_hbox = gtk.HBox(spacing=10)
		self.goals_hbox.set_border_width(5)
		self.goals_hbox.pack_start(self.hg_label)
		self.goals_hbox.pack_start(self.hg_spin)
		self.goals_hbox.pack_start(self.ag_label)
		self.goals_hbox.pack_start(self.ag_spin)
		self.parent_box.pack_start(self.goals_hbox, expand = False)
		
		self.prob_label = gtk.Label("Probability:")
		self.prob_entry = gtk.Entry()
		self.prob_recalc_button = gtk.Button("Recalculate Probability")
		self.prob_recalc_button.connect('clicked', self.repop_prob)
		self.prob_hbox = gtk.HBox(spacing=10)
		self.prob_hbox.set_border_width(5)
		self.prob_hbox.pack_start(self.prob_label)
		self.prob_hbox.pack_start(self.prob_entry)
		self.prob_hbox.pack_start(self.prob_recalc_button)
		self.parent_box.pack_start(self.prob_hbox, expand = False)

	def repop_prob(self, button):
		model = self.all_view.get_model()
		if self.all_view.get_cursor()[0]:
			season_id = str(self.parent.season_combo.get_id())
			itera = model.iter_nth_child(None, self.all_view.get_cursor()[0][0])
			home_abbr = model.get_value(itera, 1)
			away_abbr = model.get_value(itera, 2)
			(home_id, home, home_city, home_abbr) = self.JTN_db.get_team(abbr = home_abbr, season_id = season_id)
			(away_id, away, away_city, away_abbr) = self.JTN_db.get_team(abbr = away_abbr, season_id = season_id)

			start_date = self.start_cal.get_date()
			start_date_str = str(start_date[0]) + "-" + str(start_date[1]+1).zfill(2) + "-" + str(start_date[2]).zfill(2)
			league_home_gf = self.JTN_db.fetch_home_goals(season_id, start_date_str)
			league_away_gf = self.JTN_db.fetch_away_goals(season_id, start_date_str)
			hfa_adj = math.sqrt(float(league_home_gf) / float(league_away_gf)) if (league_away_gf != 0) else 1.0

			if(hfa_adj == 0):
				hfa_adj = 0.01
			
			home_gf = float(self.JTN_db.fetch_gf(season_id, int(home_id), start_date_str))
			home_ga = float(self.JTN_db.fetch_ga(season_id, int(home_id), start_date_str))
			home_gp = float(self.JTN_db.fetch_gp(season_id, int(home_id), start_date_str))

			away_gf = float(self.JTN_db.fetch_gf(season_id, int(away_id), start_date_str))
			away_ga = float(self.JTN_db.fetch_ga(season_id, int(away_id), start_date_str))
			away_gp = float(self.JTN_db.fetch_gp(season_id, int(away_id), start_date_str))
			
			home_exp_gf = self.parent.model_note.basic_model_exp_goals_cal(home_gf, away_ga, home_gp, away_gp, hfa_adj)
			away_exp_gf = self.parent.model_note.basic_model_exp_goals_cal(away_gf, home_ga, away_gp, home_gp, 1/hfa_adj)

			home_prob = self.JTN_db.poisson_pmf(self.hg_spin.get_value(), home_exp_gf)
			away_prob = self.JTN_db.poisson_pmf(self.ag_spin.get_value(), away_exp_gf)
			prob = home_prob * away_prob
			self.prob_entry.set_text(str(prob))
		

	def clear(self):
		self.all_view.get_model().clear()

	### Recalculate the GURU data for games in the specified date range (inclusive)
	def repop(self, button):
		start_date = self.start_cal.get_date()
		end_date = self.end_cal.get_date()
		all_list = self.all_view.get_model()
		all_list.clear()
		self.prob_entry.set_text("")
		season_id = self.parent.season_combo.get_id()

		start_date_str = str(start_date[0]) + "-" + str(start_date[1]+1).zfill(2) + "-" + str(start_date[2]).zfill(2)
		end_date_str = str(end_date[0]) + "-" + str(end_date[1]+1).zfill(2) + "-" + str(end_date[2]).zfill(2)

		### Calculate the HFA adjustment for the starting date of the range
		league_home_gf = self.JTN_db.fetch_home_goals(season_id, start_date_str)
		league_away_gf = self.JTN_db.fetch_away_goals(season_id, start_date_str)
		hfa_adj = math.sqrt(float(league_home_gf) / float(league_away_gf)) if (league_away_gf != 0) else 1.0
		
		if(hfa_adj == 0):
			hfa_adj = 0.01



		### For each game within the date range
		self.parent.cur.execute("SELECT home_id, away_id, date FROM games WHERE (season_id = '" + str(season_id) + "' AND date >= DATE('" + start_date_str + "') AND date <= DATE('" + end_date_str + "')) ORDER BY date")
		for row in self.parent.cur.fetchall():

			### Calculate the win-tie-loss chances for the specified game
			(home_id, home_name, home_city, home_abbr) = self.JTN_db.get_team(team_id = row[0])
			(away_id, away_name, away_city, away_abbr) = self.JTN_db.get_team(team_id = row[1])

			if home_abbr == None:
				home_abbr = " "
			if away_abbr == None:
				away_abbr = " "

			text = row[2] + " " + home_abbr + "-" + away_abbr

			home_gf = float(self.JTN_db.fetch_gf(season_id, int(row[0]), start_date_str))
			home_ga = float(self.JTN_db.fetch_ga(season_id, int(row[0]), start_date_str))
			home_gp = float(self.JTN_db.fetch_gp(season_id, int(row[0]), start_date_str))

			away_gf = float(self.JTN_db.fetch_gf(season_id, int(row[1]), start_date_str))
			away_ga = float(self.JTN_db.fetch_ga(season_id, int(row[1]), start_date_str))
			away_gp = float(self.JTN_db.fetch_gp(season_id, int(row[1]), start_date_str))

			home_exp_gf = self.parent.model_note.basic_model_exp_goals_cal(home_gf, away_ga, home_gp, away_gp, hfa_adj)
			away_exp_gf = self.parent.model_note.basic_model_exp_goals_cal(away_gf, home_ga, away_gp, home_gp, 1/hfa_adj)
			(home_win_chance, tie_chance, away_win_chance) = self.parent.model_note.basic_model_game_calc(home_exp_gf, away_exp_gf)

			### Calculate the most likely number of goals scored for the home team
			goal_prob = []
			index = 0
			goal_calc = self.JTN_db.poisson_pmf(index, home_exp_gf)
			prev_goal_calc = goal_calc
			goal_prob.append(goal_calc)
			while prev_goal_calc <= goal_calc:
				prev_goal_calc = goal_calc
				index = index + 1
				goal_calc = self.JTN_db.poisson_pmf(index, home_exp_gf)
			
			home_max_prob = index - 1

			### Calculate the most likely number of goals scored for the away team
			goal_prob = []
			index = 0
			goal_calc = self.JTN_db.poisson_pmf(index, away_exp_gf)
			prev_goal_calc = goal_calc
			goal_prob.append(goal_calc)
			while prev_goal_calc <= goal_calc:
				prev_goal_calc = goal_calc
				index = index + 1
				goal_calc = self.JTN_db.poisson_pmf(index, away_exp_gf)

			away_max_prob = index - 1

			max_prob_str = str(home_max_prob) + " - " + str(away_max_prob)

			### Calculate the best expected points values for GURU for each possible scenario:
			###    home win, tie, away win
			exp_guru_pts_home = []
			exp_guru_pts_tie = []
			exp_guru_pts_away = []
			for home_goals in range(0,10):
				exp_guru_pts_home.append([])
				exp_guru_pts_tie.append([])
				exp_guru_pts_away.append([])
				for away_goals in range(0,10):
					exp_guru_pts_home[home_goals].append(0.0)
					exp_guru_pts_tie[home_goals].append(0.0)
					exp_guru_pts_away[home_goals].append(0.0)
					if home_goals == away_goals:
						exp_guru_pts_tie[home_goals][away_goals] += 2 * tie_chance + self.JTN_db.poisson_pmf(home_goals, home_exp_gf) + self.JTN_db.poisson_pmf(away_goals, away_exp_gf)
					elif home_goals > away_goals:
						exp_guru_pts_home[home_goals][away_goals] += 2 * home_win_chance + self.JTN_db.poisson_pmf(home_goals, home_exp_gf) + self.JTN_db.poisson_pmf(away_goals, away_exp_gf)
					else:
						exp_guru_pts_away[home_goals][away_goals] += 2 * away_win_chance + self.JTN_db.poisson_pmf(home_goals, home_exp_gf) + self.JTN_db.poisson_pmf(away_goals, away_exp_gf)
			max_exp_guru_pts_home = [max(exp_guru_pts_home[x]) for x in range(10)]
			max_exp_guru_pts_away = [max(exp_guru_pts_away[x]) for x in range(10)]
			max_exp_guru_pts_tie  = [max(exp_guru_pts_tie[x])  for x in range(10)]

			### Determine the best GURU result for a home win
			max_exp_guru_pts_home_hg = max_exp_guru_pts_home.index(max(max_exp_guru_pts_home))
			max_exp_guru_pts_home_ag = exp_guru_pts_home[max_exp_guru_pts_home_hg].index(max(exp_guru_pts_home[max_exp_guru_pts_home_hg]))
			max_exp_guru_pts_home_str = str(max_exp_guru_pts_home_hg) + " - " + str(max_exp_guru_pts_home_ag)

			### Determine the best GURU result for a tie
			max_exp_guru_pts_tie_hg = max_exp_guru_pts_tie.index(max(max_exp_guru_pts_tie))
			max_exp_guru_pts_tie_ag = exp_guru_pts_tie[max_exp_guru_pts_tie_hg].index(max(exp_guru_pts_tie[max_exp_guru_pts_tie_hg]))
			max_exp_guru_pts_tie_str = str(max_exp_guru_pts_tie_hg) + " - " + str(max_exp_guru_pts_tie_ag)

			### Determine the best GURU result for an away win
			max_exp_guru_pts_away_hg = max_exp_guru_pts_away.index(max(max_exp_guru_pts_away))
			max_exp_guru_pts_away_ag = exp_guru_pts_away[max_exp_guru_pts_away_hg].index(max(exp_guru_pts_away[max_exp_guru_pts_away_hg]))
			max_exp_guru_pts_away_str = str(max_exp_guru_pts_away_hg) + " - " + str(max_exp_guru_pts_away_ag)


			### Put this massive amount of data calculated into the treeview.
			all_list.append((row[2], home_abbr, away_abbr, home_win_chance*100, tie_chance*100, away_win_chance*100, max_prob_str, max_exp_guru_pts_home_str, max(max_exp_guru_pts_home), max_exp_guru_pts_away_str, max(max_exp_guru_pts_away), max_exp_guru_pts_tie_str, max(max_exp_guru_pts_tie)))
