
import gtk
import gobject

class Results_Notebook:
	def __init__(self, parent_box, get_season_id, JTN_db):
		self.parent_box = parent_box
		self.get_season_id = get_season_id
		self.JTN_db = JTN_db
		

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
		self.parent_box.pack_start(self.list_hbox)

		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.list_hbox.pack_start(scrolled_window)

		
		scrolled_window.add(self.all_view)

		self.all_view.set_model(list_store)


	### Repopulate the results table from the DB
	def repop(self):
		season_id = self.get_season_id()
		
		all_list = self.all_view.get_model()
		all_list.clear()

		for column in self.all_view.get_columns():
			self.all_view.remove_column(column)

		column = gtk.TreeViewColumn("Team", gtk.CellRendererText(), text=0)
		self.all_view.append_column(column)

		### Add columns to the treeview for each game in the season for each team.
		row = self.JTN_db.get_teams(season_id = season_id)
		team_id = row[0][0] if len(row) else 0

		count = len(self.JTN_db.get_all_games(season_id = season_id, any_team = team_id))
		for n in range(0,count):
			column = gtk.TreeViewColumn(str(n+1), gtk.CellRendererText(), text=(n*2+1), background=(n*2+2))
			self.all_view.append_column(column)

		team_list = []
		### For each team in the league...
		map(team_list.append, self.JTN_db.get_teams(season_id = season_id))
		team_list.sort()

		for (team_id, name, city, abbr) in team_list:
			team_row = [name]

			### Fetch the results for each game for the current team (sorted by date)
			for game in self.JTN_db.get_all_games(season_id = season_id, ordered = True, any_team = team_id, order_asc = True):
				if game[2] == team_id:
					other_team_id = game[5]
					other_goals = game[6]
					goals = game[3]
					prefix = ""
				else:
					other_team_id = game[2]
					other_goals = game[3]
					goals = game[6]
					prefix = "@"
		
				(other_team_id, other_team_name, other_team_city, other_team_abbr) = self.JTN_db.get_team(team_id = other_team_id)
				text = prefix
				if other_team_abbr != None:
					text += other_team_abbr
				text += "\n"


				if game[10] == "TRUE":
					text += str(game[3])
				else:
					text += " "
				text += "-"
				if game[10] == "TRUE":
					text += str(game[6])
				else:
					text += " "
				team_row.append(text)

				if game[10] == "FALSE":
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
