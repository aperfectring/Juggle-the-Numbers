
import gtk
import gobject

class Table_Notebook:
	def __init__(self, parent_box, get_season_id, get_conf_id, get_date, JTN_db):
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

		map(team_list.append, self.JTN_db.get_teams(season_id = season_id, conf_id = conf_id))
		team_list.sort()

		for row in team_list:
			team_id = row[0]
			team_name = row[1]

			games_played = self.JTN_db.fetch_gp(season_id, team_id, self.get_date())
			goals_scored = self.JTN_db.fetch_gf(season_id, team_id, self.get_date())
			goals_against = self.JTN_db.fetch_ga(season_id, team_id, self.get_date())
			num_tied = self.JTN_db.fetch_ties(season_id, team_id, self.get_date())
			num_won = self.JTN_db.fetch_wins(season_id, team_id, self.get_date())
			num_lost = self.JTN_db.fetch_loss(season_id, team_id, self.get_date())

			goal_ratio = 100 if goals_against == 0 else (float(goals_scored) / float(goals_against))

			all_list.append( (team_name, games_played, num_won, num_lost, num_tied, goals_scored, goals_against, goals_scored - goals_against, goal_ratio, 3*num_won + num_tied) )

