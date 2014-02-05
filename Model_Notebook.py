
import gtk
import gobject
import threading
import math

### Calculate the Poisson distribution CDF for given values of k and lambda
def poisson_cdf(k, lamb):
	return sum(map(lambda x:poisson_pmf(x,lamb), range(0,k+1)))

### Calculate the Poisson distribution PMF for given values of k and lambda
def poisson_pmf(k, lamb):
	return math.pow(lamb, k) / math.factorial(k) * math.exp(-lamb)

class Model_Notebook:
	def __init__(self, parent, JTN_db):
		self.parent = parent
		self.JTN_db = JTN_db
		
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
			(myid, name, city, abbr) = self.JTN_db.get_team(team_id = team[0])
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

		if season_id:
			team_list = []
			map(team_list.append, self.JTN_db.get_teams(season_id = season_id, conf_id = conf_id))
			team_list.sort()
			map(lambda x: all_list.append( (x[1], basic_pts[x[0]], eap_ppg[x[0]]) ), team_list)

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

		win_chance = sum(map(lambda x: poisson_pmf(x, opp_exp_gf), range(0,opp_goals_adj)))

		win_chance += sum(map(lambda x: poisson_pmf(x + opp_goals_adj, opp_exp_gf) * (1 - poisson_cdf(x + team_goals_adj, team_exp_gf)), range(0,100)))

		return win_chance

	### Calculate the chance that a team will tie a game based on expected goals.
	###   This function can also calculate the probability of a team tying the aggregate given
	###   x and y goals were scored previously, where x and y are the goals scored by the team
	###   and their opposition in prior games of the set.
	def tie_chance_calc(self, team_goals_base, opp_goals_base, team_exp_gf, opp_exp_gf):
		team_goals_adj = opp_goals_base - min(team_goals_base, opp_goals_base)
		opp_goals_adj = team_goals_base - min(team_goals_base, opp_goals_base)

		tie_chance = 0.0
		tie_chance = sum(map(lambda x: poisson_pmf(x + team_goals_adj, team_exp_gf) * poisson_pmf(x + opp_goals_adj, opp_exp_gf), range(0,100)))

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
