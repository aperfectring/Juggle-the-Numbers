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

### Calculate the Poisson distribution CDF for given values of k and lambda
def poisson_cdf(k, lamb):
	pois_sum = 0
	for i in range(0,k+1):
		pois_sum += poisson_pmf(i, lamb)
	return pois_sum

### Calculate the Poisson distribution PMF for given values of k and lambda
def poisson_pmf(k, lamb):
	return math.pow(lamb, k) / math.factorial(k) * math.exp(-lamb)



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


	### Repopulate the table from the DB
	def repop(self):
		season_id = self.parent.season_combo.get_id()
		conf_id = self.parent.conf_combo.get_id()

		all_list = self.all_view.get_model()
		all_list.clear()

		team_list = []

		if conf_id == None:
			self.parent.cur.execute("SELECT team_id FROM team_season WHERE (season_id = '" + str(season_id) + "')")
		else:
			self.parent.cur.execute("SELECT team_id FROM team_season WHERE (season_id = '" + str(season_id) + "' AND conf_id = '" + str(conf_id) + "')")
		for row in self.parent.cur.fetchall():
			team_list.append(get_team_from_id(self.parent.cur, row[0]))
		team_list.sort()

		for row in team_list:
			team_id = row[3]
			self.parent.cur.execute("SELECT team_name FROM teams WHERE id = '" + str(row[3]) + "'")
			team_name = self.parent.cur.fetchone()[0]

			games_played = self.fetch_gp(team_id, self.parent.date_cal.get_date())
			goals_scored = self.fetch_gf(team_id, self.parent.date_cal.get_date())
			goals_against = self.fetch_ga(team_id, self.parent.date_cal.get_date())
			num_tied = self.fetch_ties(team_id, self.parent.date_cal.get_date())
			num_won = self.fetch_wins(team_id, self.parent.date_cal.get_date())
			num_lost = self.fetch_loss(team_id, self.parent.date_cal.get_date())

			goal_ratio = 100 if goals_against == 0 else (float(goals_scored) / float(goals_against))

			all_list.append( (team_name, games_played, num_won, num_lost, num_tied, goals_scored, goals_against, goals_scored - goals_against, goal_ratio, 3*num_won + num_tied) )

	### Fetch the games played by the team up to and including the specified date
	def fetch_gp(self, team, date = None):
		if date == None:
			date_today = datetime.date.today()
			date = date_today.isoformat()
		season_id = self.parent.season_combo.get_id()
		self.parent.cur.execute("SELECT COUNT(*) FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "' AND (home_id = '" + str(team) + "' OR away_id = '" + str(team) + "'))")
		games_played = self.parent.cur.fetchone()[0]
		return games_played

	### Fetch the ties by the team up to and including the specified date
	def fetch_ties(self, team, date = None):
		if date == None:
			date_today = datetime.date.today()
			date = date_today.isoformat()
		season_id = self.parent.season_combo.get_id()
		self.parent.cur.execute("SELECT COUNT(*) FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "' AND (home_id = '" + str(team) + "' OR away_id = '" + str(team) + "') AND home_goals = away_goals)")
		num_tied = self.parent.cur.fetchone()[0]
		return num_tied

	### Fetch the wins by the team up to and including the specified date
	def fetch_wins(self, team, date = None):
		if date == None:
			date_today = datetime.date.today()
			date = date_today.isoformat()
		season_id = self.parent.season_combo.get_id()
		self.parent.cur.execute("SELECT COUNT(*) FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "' AND ((home_id = '" + str(team) + "' AND home_goals > away_goals) OR (away_id = '" + str(team) + "') AND home_goals < away_goals))")
		num_won = self.parent.cur.fetchone()[0]
		return num_won

	### Fetch the losses by the team up to and including the specified date
	def fetch_loss(self, team, date = None):
		if date == None:
			date_today = datetime.date.today()
			date = date_today.isoformat()
		season_id = self.parent.season_combo.get_id()
		self.parent.cur.execute("SELECT COUNT(*) FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "' AND ((home_id = '" + str(team) + "' AND home_goals < away_goals) OR (away_id = '" + str(team) + "') AND home_goals > away_goals))")
		num_lost = self.parent.cur.fetchone()[0]
		return num_lost

	### Fetch the points earned by the team up to and including the specified date
	def fetch_pts(self, team, date = None):
		num_tied = self.fetch_ties(team, date)
		num_won = self.fetch_wins(team, date)
		return (3 * num_won + num_tied)

	### Fetch the goals scored by the team up to and including the specified date
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

	### Fetch the goals against the team up to and including the specified date
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

	### Fetch the goals scored by home teams up to and including the specified date
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

	### Fetch the goals scored by away teams up to and including the specified date
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

		self.calc_thread = threading.Thread(target=self.repop)

		self.calc_progress = gtk.ProgressBar()
		self.parent.model_note_vbox.pack_start(self.calc_progress, expand = False)

		self.hfa_label = gtk.Label("HFA Adjust Value:")
		self.hfa_entry = gtk.Entry()
		self.hfa_hbox = gtk.HBox(spacing=10)
		self.hfa_hbox.set_border_width(5)
		self.hfa_hbox.pack_start(self.hfa_label)
		self.hfa_hbox.pack_start(self.hfa_entry)
		self.parent.model_note_vbox.pack_start(self.hfa_hbox, expand = False)

		self.calc_button = gtk.Button("Recalculate")
		self.parent.model_note_vbox.pack_start(self.calc_button, expand = False)
		self.calc_button.connect('clicked', self.do_recalc)

		self.export_button = gtk.Button("Export")
		self.parent.model_note_vbox.pack_start(self.export_button, expand = False)
		self.export_button.connect('clicked', self.export_text)

		self.thread_sig = threading.Event()
		self.calc_progress.set_visible(False)

	### Export the table+models in the format expected by the JuggleTheNumbers website
	def export_text(self, button):
		model = self.parent.league_combo.combo.get_model()
		index = self.parent.league_combo.combo.get_active()
		f = open('outfile', 'w')
		f.write('<br />\n')
		f.write('<table cellspacing="0" cellpadding="3" id="'+str(model[index][0])+'">\n')
		f.write('  <thead><tr><td>Team</td><td>PPG</td><td>Pts</td><td>1-O Pts</td><td>GP</td><td>W</td><td>L</td><td>T</td><td>GF</td><td>GA</td><td>GD</td><td>GF:GA</td><td>EAP</td></tr></thead>\n')

		season_id = self.parent.season_combo.get_id()
		conf_id = self.parent.conf_combo.get_id()
		if conf_id == None:
			self.parent.cur.execute("SELECT team_id FROM team_season WHERE (season_id = '" + str(season_id) + "')")
		else:
			self.parent.cur.execute("SELECT team_id FROM team_season WHERE (season_id = '" + str(season_id) + "' AND conf_id = '" + str(conf_id) + "')")


		for team in self.parent.cur.fetchall():
			(name, city, abbr, myid) = get_team_from_id(self.parent.cur, team[0])
			pts = self.parent.table_note.fetch_pts(myid)
			gp = self.parent.table_note.fetch_gp(myid)
			ppg = round(float(pts)/float(gp),2)
			basic = self.fetch_basic(name)
			wins = self.parent.table_note.fetch_wins(myid)
			loss = self.parent.table_note.fetch_loss(myid)
			ties = self.parent.table_note.fetch_ties(myid)
			gf = self.parent.table_note.fetch_gf(myid)
			ga = self.parent.table_note.fetch_ga(myid)
			gd = gf - ga
			if(ga != 0):
				gfga = '{0:.2f}'.format(float(gf) / float(ga))
			else:
				gfga = 'N/A'
			eap = self.fetch_eap(name)

			f.write("  <tr><td>"+str(abbr)+"</td><td>"+'{0:.2f}'.format(ppg)+"</td><td>"+str(pts)+"</td><td>"+'{0:.2f}'.format(basic)+"</td><td>"+str(gp)+"</td><td>"+str(wins)+"</td><td>"+str(loss)+"</td><td>"+str(ties)+"</td><td>"+str(gf)+"</td><td>"+str(ga)+"</td><td>"+str(gd)+"</td><td>"+str(gfga)+"</td><td>"+'{0:.2f}'.format(eap)+"</td></tr>\n")
		f.write("</table>\n")
		f.write('<script type="text/javascript">\n')
		model = self.parent.league_combo.combo.get_model()
		index = self.parent.league_combo.combo.get_active()
		f.write("var "+str(model[index][0])+" = new SortableTable(document.getElementById('"+str(model[index][0])+"'), 100);\n")
		f.write("</script>\n")
		f.close()

	### Fetch the basic model value for the team specified
	def fetch_basic(self, name):
		all_model = self.all_view.get_model()
		myiter = all_model.get_iter_first()
		while (myiter != None):
			if(all_model.get(myiter, 0)[0] == name):
				return all_model.get(myiter, 1)[0]
			myiter = all_model.iter_next(myiter)
		return None
		
	### Fetch the EAP model value for the team specified
	def fetch_eap(self, name):
		all_model = self.all_view.get_model()
		myiter = all_model.get_iter_first()
		while (myiter != None):
			if(all_model.get(myiter, 0)[0] == name):
				return all_model.get(myiter, 2)[0]
			myiter = all_model.iter_next(myiter)
		return None
		

	### Clear the model table.
	def clear(self):
		self.all_view.get_model().clear()
		self.calc_progress.set_visible(False)

	### Restart the calculation thread.  Kill any previously started threads before starting a new one.
	def kick_thread(self):
		if self.calc_thread.is_alive():
			self.thread_sig.set()
			self.calc_thread.join()
			self.thread_sig.clear()
		self.calc_thread = threading.Thread(target=self.repop)
		self.calc_thread.start()
		
	def do_recalc(self, button):
		kickthr = threading.Thread(target=self.kick_thread)
		kickthr.start()
	### Callback from the notebook to kick off the model calculation
	#def do_recalc(self, notebook, page_NOUSE, page_num):
	#	if notebook.get_tab_label(notebook.get_nth_page(page_num)).get_text() == "Model":
	#		kickthr = threading.Thread(target=self.kick_thread)
	#		kickthr.start()

	### Recalculate the models for all teams
	def repop(self):
		gtk.gdk.threads_enter()
		self.calc_progress.set_visible(True)
		self.calc_progress.set_fraction(0)
		self.calc_progress.set_text("Calculating...")		
		gtk.gdk.threads_leave()
		basic_pts = self.basic_model_calc(self.parent.date_cal.get_date())
		if self.thread_sig.wait(0.01):
			return
		eap_ppg = self.eap_model_calc(self.parent.date_cal.get_date())
		if self.thread_sig.wait(0.01):
			return


		gtk.gdk.threads_enter()
		season_id = self.parent.season_combo.get_id()
		conf_id = self.parent.conf_combo.get_id()
		all_list = self.all_view.get_model()
		all_list.clear()
		gtk.gdk.threads_leave()

		if conf_id == None:
			self.parent.cur.execute("SELECT team_id FROM team_season WHERE (season_id = '" + str(season_id) + "')")
		else:
			self.parent.cur.execute("SELECT team_id FROM team_season WHERE (season_id = '" + str(season_id) + "' AND conf_id = '" + str(conf_id) + "')")
		gtk.gdk.threads_enter()

		team_list = []
		for team in self.parent.cur.fetchall():
			team_list.append(get_team_from_id(self.parent.cur, team[0]))
		team_list.sort()

		for team in team_list:
			all_list.append( (team[0], basic_pts[team[3]], eap_ppg[team[3]]) )

		self.calc_progress.set_fraction(1)
		self.calc_progress.set_text("Calculation Complete")		
		self.calc_progress.set_visible(False)
		gtk.gdk.threads_leave()


	### Calculate the chance that a team will win a game based on expected goals.
	###   This function can also calculate the probability of a team winning the aggregate given
	###   x and y goals were scored previously, where x and y are the goals scored by the team
	###   and their opposition in prior games of the set.
	def win_chance_calc(self, team_goals_base, opp_goals_base, team_exp_gf, opp_exp_gf):
		team_goals_adj = opp_goals_base - min(team_goals_base, opp_goals_base)
		opp_goals_adj = team_goals_base - min(team_goals_base, opp_goals_base)

		win_chance = 0.0
		for i in range(0,opp_goals_adj):
			win_chance += poisson_pmf(i, opp_exp_gf)

		for i in range(0,100):
			win_chance += poisson_pmf(i + opp_goals_adj, opp_exp_gf) * (1 - poisson_cdf(i + team_goals_adj, team_exp_gf))

		return win_chance

	### Calculate the chance that a team will tie a game based on expected goals.
	###   This function can also calculate the probability of a team tying the aggregate given
	###   x and y goals were scored previously, where x and y are the goals scored by the team
	###   and their opposition in prior games of the set.
	def tie_chance_calc(self, team_goals_base, opp_goals_base, team_exp_gf, opp_exp_gf):
		team_goals_adj = opp_goals_base - min(team_goals_base, opp_goals_base)
		opp_goals_adj = team_goals_base - min(team_goals_base, opp_goals_base)

		tie_chance = 0.0
		for i in range(0,100):
			tie_chance += poisson_pmf(i + team_goals_adj, team_exp_gf) * poisson_pmf(i + opp_goals_adj, opp_exp_gf)

		return tie_chance

	### Calculates the expected goals from basic stats.
	def basic_model_exp_goals_cal(self, home_gf, away_ga, home_gp, away_gp, hfa_adj):
		if(home_gp == 0) or (away_gp == 0):
			return 0.0
		return (home_gf + away_ga) / (home_gp + away_gp) * hfa_adj

	### Calculates the basic model results for a single game (used by other widgets)
	def basic_model_game_calc(self, home_exp_gf, away_exp_gf):
		tie_chance = self.tie_chance_calc(0, 0, home_exp_gf, away_exp_gf)
		home_win_chance = self.win_chance_calc(0, 0, home_exp_gf, away_exp_gf)
		away_win_chance = self.win_chance_calc(0, 0, away_exp_gf, home_exp_gf)
		return (home_win_chance, tie_chance, away_win_chance)
	
	### Calculates the basic model for all unplayed games, and all games after the specified date
	def basic_model_calc(self, date = None):
		gtk.gdk.threads_enter()
		league_home_gf = self.parent.table_note.fetch_home_goals(date)
		league_away_gf = self.parent.table_note.fetch_away_goals(date)
		gtk.gdk.threads_leave()

		### Calculate the home field advantage adjustment
		if(league_away_gf != 0):
			hfa_adj = math.sqrt(float(league_home_gf) / float(league_away_gf))
		else:
			hfa_adj = 1.0

		if(hfa_adj == 0):
			hfa_adj = 0.01

		self.hfa_entry.set_text(str(hfa_adj))

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

		### Fetch all of the basic stats for each team
		gtk.gdk.threads_enter()
		self.parent.cur.execute("SELECT team_id FROM team_season WHERE season_id = '" + str(season_id) + "'")
		for team in self.parent.cur.fetchall():
			team_points[team[0]] = self.parent.table_note.fetch_pts(int(team[0]), date)
			team_gf[team[0]] = float(self.parent.table_note.fetch_gf(int(team[0]), date))
			team_ga[team[0]] = float(self.parent.table_note.fetch_ga(int(team[0]), date))
			team_gp[team[0]] = float(self.parent.table_note.fetch_gp(int(team[0]), date))
		gtk.gdk.threads_leave()

		### Iterate through all of the unplayed games + games after the specified date, and
		###   calculate the chance of win-tie-loss for each team.  Calculate the expected points
		###   for each team, and add those values into the points already earned.
		self.parent.cur.execute("SELECT home_id, away_id, date FROM games WHERE (season_id = '" + str(season_id) + "' AND (date > '" + date + "' OR played = 'FALSE'))")

		game_arr = self.parent.cur.fetchall()
		for game in game_arr:
			home = game[0]
			away = game[1]
			gtk.gdk.threads_enter()
			if self.thread_sig.wait(0.01):
				gtk.gdk.threads_leave()
				return
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

	### Calculate the EAP model based on the standings at the provided date.
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

class Results_Notebook:
	def __init__(self, parent):
		self.parent = parent

		season_id = self.parent.season_combo.get_id()
		#### There are enough strings here for 52 games in the season, AND their background colors.
		####    This is much more than we need, but better to be safe than sorry.
		list_store = gtk.ListStore(gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING)
		self.all_view = gtk.TreeView()

		column = gtk.TreeViewColumn("Team", gtk.CellRendererText(), text=0)
		self.all_view.append_column(column)

		self.list_hbox = gtk.HBox(spacing=10)
		self.list_hbox.set_border_width(5)
		self.parent.results_note_vbox.pack_start(self.list_hbox)

		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.list_hbox.pack_start(scrolled_window)

		
		scrolled_window.add(self.all_view)

		self.all_view.set_model(list_store)


	### Repopulate the results table from the DB
	def repop(self):
		season_id = self.parent.season_combo.get_id()
		
		all_list = self.all_view.get_model()
		all_list.clear()

		for column in self.all_view.get_columns():
			self.all_view.remove_column(column)

		column = gtk.TreeViewColumn("Team", gtk.CellRendererText(), text=0)
		self.all_view.append_column(column)

		### Add columns to the treeview for each game in the season for each team.
		self.parent.cur.execute("SELECT team_id FROM team_season WHERE season_id = '" + str(season_id) + "'")
		row = self.parent.cur.fetchone()
		if row:
			team_id = row[0]
		else:
			team_id = 0

		self.parent.cur.execute("SELECT COUNT(*) FROM games WHERE (season_id = '" + str(season_id) + "' AND (home_id = '" + str(team_id) + "' OR away_id = '" + str(team_id) + "'))")
		row = self.parent.cur.fetchone()
		if row:
			for n in range(0,row[0]):
				column = gtk.TreeViewColumn(str(n+1), gtk.CellRendererText(), text=(n*2+1), background=(n*2+2))
				self.all_view.append_column(column)

		team_list = []
		### For each team in the league...
		self.parent.cur.execute("SELECT team_id FROM team_season WHERE season_id = '" + str(season_id) + "'")
		for row in self.parent.cur.fetchall():
			team_list.append(get_team_from_id(self.parent.cur, row[0]))
		team_list.sort()

		for row in team_list:
			team_id = row[3]
			(name, city, abbr, team_id) = get_team_from_id(self.parent.cur, team_id)
			team_row = [name]

			### Fetch the results for each game for the current team (sorted by date)
			self.parent.cur.execute("SELECT home_id, home_goals, away_id, away_goals, played FROM games WHERE (season_id = '" + str(season_id) + "' AND (home_id = '" + str(team_id) + "' OR away_id = '" + str(team_id) + "')) ORDER BY date")

			for game in self.parent.cur.fetchall():
				other_team_id = game[0]
				if game[0] == team_id:
					other_team_id = game[2]
					other_goals = game[3]
					goals = game[1]
					prefix = ""
				else:
					other_team_id = game[0]
					other_goals = game[1]
					goals = game[3]
					prefix = "@"
				
				(other_team_name, other_team_city, other_team_abbr, other_team_id) = get_team_from_id(self.parent.cur, other_team_id)
				if other_team_abbr != None:
					other_team_abbr = prefix + other_team_abbr
				else:
					other_team_abbr = prefix
				text = other_team_abbr + "\n"
				if game[4] == "TRUE":
					text += str(game[1])
				else:
					text += " "
				text += "-"
				if game[4] == "TRUE":
					text += str(game[3])
				else:
					text += " "
				team_row.append(text)

				if game[4] == "FALSE":
					bg = "#FFFFFF"
				elif goals > other_goals:
					bg = "#80FF80"
				elif goals < other_goals:
					bg = "#FF8080"
				else:
					bg = "#FFFF80"
				team_row.append(bg)

			### Add the results for all of the games into the treeview
			for n in range(len(team_row),all_list.get_n_columns()):
				team_row.append("")
			all_list.append(team_row)

class Guru_Notebook:
	def __init__(self, parent):
		self.parent = parent

		self.cal_hbox = gtk.HBox(spacing=10)
		self.cal_hbox.set_border_width(5)
		self.parent.guru_note_vbox.pack_start(self.cal_hbox, expand = False)		

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
		self.parent.guru_note_vbox.pack_start(scrolled_window)

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
		self.parent.guru_note_vbox.pack_start(self.recalc_button, expand = False)
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
		self.parent.guru_note_vbox.pack_start(self.goals_hbox, expand = False)
		
		self.prob_label = gtk.Label("Probability:")
		self.prob_entry = gtk.Entry()
		self.prob_recalc_button = gtk.Button("Recalculate Probability")
		self.prob_recalc_button.connect('clicked', self.repop_prob)
		self.prob_hbox = gtk.HBox(spacing=10)
		self.prob_hbox.set_border_width(5)
		self.prob_hbox.pack_start(self.prob_label)
		self.prob_hbox.pack_start(self.prob_entry)
		self.prob_hbox.pack_start(self.prob_recalc_button)
		self.parent.guru_note_vbox.pack_start(self.prob_hbox, expand = False)

	def repop_prob(self, button):
		model = self.all_view.get_model()
		if self.all_view.get_cursor()[0]:
			season_id = str(self.parent.season_combo.get_id())
			itera = model.iter_nth_child(None, self.all_view.get_cursor()[0][0])
			home_abbr = model.get_value(itera, 1)
			away_abbr = model.get_value(itera, 2)
			(home, home_city, home_abbr, home_id) = get_team_from_abbr(self.parent.cur, home_abbr, season_id)
			(away, away_city, away_abbr, away_id) = get_team_from_abbr(self.parent.cur, away_abbr, season_id)

			start_date = self.start_cal.get_date()
			start_date_str = str(start_date[0]) + "-" + str(start_date[1]+1).zfill(2) + "-" + str(start_date[2]).zfill(2)
			league_home_gf = self.parent.table_note.fetch_home_goals(start_date_str)
			league_away_gf = self.parent.table_note.fetch_away_goals(start_date_str)
			if(league_away_gf != 0):
				hfa_adj = math.sqrt(float(league_home_gf) / float(league_away_gf))
			else:
				hfa_adj = 1.0

			if(hfa_adj == 0):
				hfa_adj = 0.01
			
			home_gf = float(self.parent.table_note.fetch_gf(int(home_id), start_date_str))
			home_ga = float(self.parent.table_note.fetch_ga(int(home_id), start_date_str))
			home_gp = float(self.parent.table_note.fetch_gp(int(home_id), start_date_str))

			away_gf = float(self.parent.table_note.fetch_gf(int(away_id), start_date_str))
			away_ga = float(self.parent.table_note.fetch_ga(int(away_id), start_date_str))
			away_gp = float(self.parent.table_note.fetch_gp(int(away_id), start_date_str))
			
			home_exp_gf = self.parent.model_note.basic_model_exp_goals_cal(home_gf, away_ga, home_gp, away_gp, hfa_adj)
			away_exp_gf = self.parent.model_note.basic_model_exp_goals_cal(away_gf, home_ga, away_gp, home_gp, 1/hfa_adj)

			home_prob = poisson_pmf(self.hg_spin.get_value(), home_exp_gf)
			away_prob = poisson_pmf(self.ag_spin.get_value(), away_exp_gf)
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

		start_date_str = str(start_date[0]) + "-" + str(start_date[1]+1).zfill(2) + "-" + str(start_date[2]).zfill(2)
		end_date_str = str(end_date[0]) + "-" + str(end_date[1]+1).zfill(2) + "-" + str(end_date[2]).zfill(2)

		### Calculate the HFA adjustment for the starting date of the range
		league_home_gf = self.parent.table_note.fetch_home_goals(start_date_str)
		league_away_gf = self.parent.table_note.fetch_away_goals(start_date_str)
		if(league_away_gf != 0):
			hfa_adj = math.sqrt(float(league_home_gf) / float(league_away_gf))
		else:
			hfa_adj = 1.0

		if(hfa_adj == 0):
			hfa_adj = 0.01


		season_id = self.parent.season_combo.get_id()

		### For each game within the date range
		self.parent.cur.execute("SELECT home_id, away_id, date FROM games WHERE (season_id = '" + str(season_id) + "' AND date >= DATE('" + start_date_str + "') AND date <= DATE('" + end_date_str + "')) ORDER BY date")
		for row in self.parent.cur.fetchall():

			### Calculate the win-tie-loss chances for the specified game
			(home_name, home_city, home_abbr, home_id) = get_team_from_id(self.parent.cur, row[0])
			(away_name, away_city, away_abbr, away_id) = get_team_from_id(self.parent.cur, row[1])

			if home_abbr == None:
				home_abbr = " "
			if away_abbr == None:
				away_abbr = " "

			text = row[2] + " " + home_abbr + "-" + away_abbr

			home_gf = float(self.parent.table_note.fetch_gf(int(row[0]), start_date_str))
			home_ga = float(self.parent.table_note.fetch_ga(int(row[0]), start_date_str))
			home_gp = float(self.parent.table_note.fetch_gp(int(row[0]), start_date_str))

			away_gf = float(self.parent.table_note.fetch_gf(int(row[1]), start_date_str))
			away_ga = float(self.parent.table_note.fetch_ga(int(row[1]), start_date_str))
			away_gp = float(self.parent.table_note.fetch_gp(int(row[1]), start_date_str))

			home_exp_gf = self.parent.model_note.basic_model_exp_goals_cal(home_gf, away_ga, home_gp, away_gp, hfa_adj)
			away_exp_gf = self.parent.model_note.basic_model_exp_goals_cal(away_gf, home_ga, away_gp, home_gp, 1/hfa_adj)
			(home_win_chance, tie_chance, away_win_chance) = self.parent.model_note.basic_model_game_calc(home_exp_gf, away_exp_gf)

			### Calculate the most likely number of goals scored for the home team
			goal_prob = []
			index = 0
			goal_calc = poisson_pmf(index, home_exp_gf)
			prev_goal_calc = goal_calc
			goal_prob.append(goal_calc)
			while prev_goal_calc <= goal_calc:
				prev_goal_calc = goal_calc
				index = index + 1
				goal_calc = poisson_pmf(index, home_exp_gf)
			
			home_max_prob = index - 1

			### Calculate the most likely number of goals scored for the away team
			goal_prob = []
			index = 0
			goal_calc = poisson_pmf(index, away_exp_gf)
			prev_goal_calc = goal_calc
			goal_prob.append(goal_calc)
			while prev_goal_calc <= goal_calc:
				prev_goal_calc = goal_calc
				index = index + 1
				goal_calc = poisson_pmf(index, away_exp_gf)

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
						exp_guru_pts_tie[home_goals][away_goals] += 2 * tie_chance + poisson_pmf(home_goals, home_exp_gf) + poisson_pmf(away_goals, away_exp_gf)
					elif home_goals > away_goals:
						exp_guru_pts_home[home_goals][away_goals] += 2 * home_win_chance + poisson_pmf(home_goals, home_exp_gf) + poisson_pmf(away_goals, away_exp_gf)
					else:
						exp_guru_pts_away[home_goals][away_goals] += 2 * away_win_chance + poisson_pmf(home_goals, home_exp_gf) + poisson_pmf(away_goals, away_exp_gf)
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

		self.table_note = Table_Notebook(self)

		# When the Teams Notebook updates,
		# the Table Notebook needs to be repopulated.
		self.teams_note.register(self.table_note.repop())

		self.model_note = Model_Notebook(self)

		# When the Teams Notebook updates,
		# the Model Notebook needs to be repopulated.
		self.teams_note.register(self.model_note.repop())

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
		self.results_note = Results_Notebook(self)

		# When the Games Notebook is updated,
		# the Results Notebook needs to be repopulated
		self.games_note.register(self.results_note.repop)

		self.guru_note_vbox = gtk.VBox(spacing=10)
		self.guru_note_vbox.set_border_width(5)
		self.notebook.append_page(self.guru_note_vbox, gtk.Label("Guru"))
		self.guru_note = Guru_Notebook(self)

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
