
import gtk
import gobject
import datetime
import math

class Game_Rating_Notebook:
	def __init__(self, parent_box, get_season_id, get_start_date, get_end_date, JTN_db):
		self.parent_box = parent_box
		self.get_season_id = get_season_id
		self.get_start_date = get_start_date
		self.get_end_date = get_end_date
		self.JTN_db = JTN_db

		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.parent_box.pack_start(scrolled_window)

		list_store = gtk.ListStore(gobject.TYPE_STRING, # Date
					   gobject.TYPE_STRING,	# Home Team
					   gobject.TYPE_INT,    # Attendance
					   gobject.TYPE_INT,    # League Score
					   gobject.TYPE_INT)    # Team Score

		self.all_view = gtk.TreeView()
		scrolled_window.add(self.all_view)
		self.all_view.set_model(list_store)

		column = gtk.TreeViewColumn("Game", gtk.CellRendererText(), text=0)
		column.set_sort_column_id(0)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Home", gtk.CellRendererText(), text=1)
		column.set_sort_column_id(1)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Attendance", gtk.CellRendererText(), text=2)
		column.set_sort_column_id(2)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("League Score", gtk.CellRendererText(), text=3)
		column.set_sort_column_id(3)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Team Score", gtk.CellRendererText(), text=4)
		column.set_sort_column_id(4)
		self.all_view.append_column(column)

		self.export_button = gtk.Button("Export")
		self.parent_box.pack_start(self.export_button, expand = False)
		self.export_button.connect('clicked', self.export_text)

	### Export the table+models in the format expected by the JuggleTheNumbers website
	def export_text(self, button):
		print "Game Ratings"
		print ""
		print "These numbers are an attempt to assign a rating of how well an individual game's attendance matches up with performance of the league as a whole, and the individual team.  The reference data is the previous year's average and standard deviation, for both the league, and the individual team.  The numbers are the normal distribution's CDF multiplied by 100, and rounded to the nearest whole number.  This means the valid range is from 0 to 100."
		print ""
		print ""
		print "[table]Date|Team|Attendance|League Score|Team Score"
		all_list = self.all_view.get_model()
		for game in all_list:
			print "\\",game[0],"|",game[1],"|",game[2],"|",game[3],"|",game[4]
		print "[/table]"

	### Recalculate the models for all teams
	def repop(self, cal = None):
		season_id = self.get_season_id()
		all_list = self.all_view.get_model()
		all_list.clear()

		start_date = self.get_start_date()
		end_date = self.get_end_date()

		game_list = self.JTN_db.get_all_games(played = "TRUE", start_date = start_date, end_date = end_date)
		this_season = self.JTN_db.get_season(season_id = season_id)
		valid_seasons = map(lambda x: x[2], self.JTN_db.get_seasons(league_id = this_season[3]))

		league_games = self.JTN_db.get_all_games(season_id = season_id)
		league_games_trim = filter(lambda x: False if x[13] == u'' else True, league_games)
		league_att = sum(map(lambda x: x[13], league_games_trim))
		league_avg = float(league_att) / float(len(league_games_trim))
		league_dev = pow(sum(map(lambda x: pow(float(x[13]) - league_avg, 2), league_games_trim))/float(len(league_games_trim)), 0.5)
				
		for game in game_list:
			if game[0] in valid_seasons:
				team = self.JTN_db.get_team(team_id = game[2])
				team_games = self.JTN_db.get_all_games(season_id = season_id, home_team = game[2])
				team_games_trim = filter(lambda x: False if x[13] == u'' else True, team_games)
				team_att = sum(map(lambda x: x[13], team_games_trim))
				team_avg = float(team_att) / float(len(team_games_trim))
				team_dev = pow(sum(map(lambda x: pow(float(x[13]) - team_avg, 2), team_games_trim))/float(len(team_games_trim)), 0.5)

				league_rating = self.calc_rating(game[13], league_avg, league_dev)
				team_rating = self.calc_rating(game[13], team_avg, team_dev)

				team = self.JTN_db.get_team(team_id = game[2])
				all_list.append((game[1], team[1], game[13], league_rating, team_rating))

	def calc_rating(self, att, avg, dev):
		if dev != 0:
			rating = int(round(0.5 * (1.0 + math.erf((att - avg) / pow(2.0 * pow(dev, 2.0), 0.5)))*100, 0))
		else:
			rating = 50
		return rating
