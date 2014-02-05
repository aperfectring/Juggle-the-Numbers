
import gtk
import gobject

class Table_Notebook:
	def __init__(self, parent, parent_box, get_season_id, get_conf_id, get_date, JTN_db):
		self.parent = parent
		self.parent_box = parent_box
		self.get_season_id = get_season_id
		self.get_conf_id = get_conf_id
		self.get_date = get_date
		self.JTN_db = JTN_db

		self.list_hbox = gtk.HBox(spacing=10)
		self.list_hbox.set_border_width(5)
		self.parent_box.pack_start(self.list_hbox)

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
		season_id = self.get_season_id()
		conf_id = self.get_conf_id()

		all_list = self.all_view.get_model()
		all_list.clear()

		team_list = []

		for row in self.JTN_db.get_teams(season_id = season_id, conf_id = conf_id):
			team_list.append(row)
		team_list.sort()

		for row in team_list:
			team_id = row[0]
			team_name = row[1]

			games_played = self.fetch_gp(team_id, self.get_date())
			goals_scored = self.fetch_gf(team_id, self.get_date())
			goals_against = self.fetch_ga(team_id, self.get_date())
			num_tied = self.fetch_ties(team_id, self.get_date())
			num_won = self.fetch_wins(team_id, self.get_date())
			num_lost = self.fetch_loss(team_id, self.get_date())

			goal_ratio = 100 if goals_against == 0 else (float(goals_scored) / float(goals_against))

			all_list.append( (team_name, games_played, num_won, num_lost, num_tied, goals_scored, goals_against, goals_scored - goals_against, goal_ratio, 3*num_won + num_tied) )

	### Fetch the games played by the team up to and including the specified date
	def fetch_gp(self, team, date = None):
		if date == None:
			date_today = datetime.date.today()
			date = date_today.isoformat()
		season_id = self.get_season_id()
		self.parent.cur.execute("SELECT COUNT(*) FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "' AND (home_id = '" + str(team) + "' OR away_id = '" + str(team) + "'))")
		games_played = self.parent.cur.fetchone()[0]
		return games_played

	### Fetch the ties by the team up to and including the specified date
	def fetch_ties(self, team, date = None):
		if date == None:
			date_today = datetime.date.today()
			date = date_today.isoformat()
		season_id = self.get_season_id()
		self.parent.cur.execute("SELECT COUNT(*) FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "' AND (home_id = '" + str(team) + "' OR away_id = '" + str(team) + "') AND home_goals = away_goals)")
		num_tied = self.parent.cur.fetchone()[0]
		return num_tied

	### Fetch the wins by the team up to and including the specified date
	def fetch_wins(self, team, date = None):
		if date == None:
			date_today = datetime.date.today()
			date = date_today.isoformat()
		season_id = self.get_season_id()
		self.parent.cur.execute("SELECT COUNT(*) FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "' AND ((home_id = '" + str(team) + "' AND home_goals > away_goals) OR (away_id = '" + str(team) + "') AND home_goals < away_goals))")
		num_won = self.parent.cur.fetchone()[0]
		return num_won

	### Fetch the losses by the team up to and including the specified date
	def fetch_loss(self, team, date = None):
		if date == None:
			date_today = datetime.date.today()
			date = date_today.isoformat()
		season_id = self.get_season_id()
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
		season_id = self.get_season_id()
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
		season_id = self.get_season_id()
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
		season_id = self.get_season_id()
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
		season_id = self.get_season_id()
		self.parent.cur.execute("SELECT SUM(away_goals) FROM games WHERE (season_id = '" + str(season_id) + "' AND played = 'TRUE' AND date <= '" + date + "')")
		goal_row = self.parent.cur.fetchone()
		goals = 0
		if goal_row[0]:
			goals = goal_row[0]
		return goals
