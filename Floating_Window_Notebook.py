
import gtk
import gobject
import datetime

class Floating_Window_Notebook:
	def __init__(self, parent_box, get_season_id, get_start_date, get_end_date, JTN_db):
		self.parent_box = parent_box
		self.get_season_id = get_season_id
		self.get_start_date = get_start_date
		self.get_end_date = get_end_date
		self.JTN_db = JTN_db

		self.list_hbox = gtk.HBox(spacing=10)
		self.list_hbox.set_border_width(5)
		self.parent_box.pack_start(self.list_hbox)

		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
		self.list_hbox.pack_start(scrolled_window)

		list_store = gtk.ListStore(gobject.TYPE_STRING, #Team
					   gobject.TYPE_INT,  #Start Last 1
					   gobject.TYPE_INT,  #End Last 1
					   gobject.TYPE_INT,  #Diff Last 1
					   gobject.TYPE_INT,  #Start Last 5
					   gobject.TYPE_INT,  #End Last 5
					   gobject.TYPE_INT,  #Diff Last 5
					   gobject.TYPE_INT,  #Start Last 17
					   gobject.TYPE_INT,  #End Last 17
					   gobject.TYPE_INT,  #Diff Last 17
					   gobject.TYPE_INT,  #Start Last Year
					   gobject.TYPE_INT,  #End Last Year
					   gobject.TYPE_INT,  #Diff Last Year
					   gobject.TYPE_INT,  #Start Last 5 Year
					   gobject.TYPE_INT,  #End Last 5 Year
					   gobject.TYPE_INT)  #Diff Last 5 Year

		self.all_view = gtk.TreeView()
		scrolled_window.add(self.all_view)
		self.all_view.set_model(list_store)

		column = gtk.TreeViewColumn("Team", gtk.CellRendererText(), text=0)
		column.set_sort_column_id(0)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Before\nLast 1\nGm", gtk.CellRendererText(), text=1)
		column.set_sort_column_id(1)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("After\nLast 1\nGm", gtk.CellRendererText(), text=2)
		column.set_sort_column_id(2)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Diff\nLast 1\nGm", gtk.CellRendererText(), text=3)
		column.set_sort_column_id(3)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Before\nLast 5\nGm", gtk.CellRendererText(), text=4)
		column.set_sort_column_id(4)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("After\nLast 5\nGm", gtk.CellRendererText(), text=5)
		column.set_sort_column_id(5)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Diff\nLast 5\nGm", gtk.CellRendererText(), text=6)
		column.set_sort_column_id(6)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Before\nLast 17\nGm", gtk.CellRendererText(), text=7)
		column.set_sort_column_id(7)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("After\nLast 17\nGm", gtk.CellRendererText(), text=8)
		column.set_sort_column_id(8)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Diff\nLast 17\nGm", gtk.CellRendererText(), text=9)
		column.set_sort_column_id(9)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Before\nLast 1\nYr", gtk.CellRendererText(), text=10)
		column.set_sort_column_id(10)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("After\nLast 1\nYr", gtk.CellRendererText(), text=11)
		column.set_sort_column_id(11)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Diff\nLast 1\nYr", gtk.CellRendererText(), text=12)
		column.set_sort_column_id(12)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Before\nLast 5\nYr", gtk.CellRendererText(), text=13)
		column.set_sort_column_id(13)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("After\nLast 5\nYr", gtk.CellRendererText(), text=14)
		column.set_sort_column_id(14)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Diff\nLast 5\nYr", gtk.CellRendererText(), text=15)
		column.set_sort_column_id(15)
		self.all_view.append_column(column)

		self.export_button = gtk.Button("Export")
		self.parent_box.pack_start(self.export_button, expand = False)
		self.export_button.connect('clicked', self.export_text)

	### Export the table+models in the format expected by the JuggleTheNumbers website
	def export_text(self, button):
		print "Floating Window"
		print ""
		print "A floating window number is the average attendance for that team over the last X number of games, or X calendar years.  So, for 17 games, it is the average of the last 17-n games from the previous season and the n games from the current season.  For 1 year, it is the average from one year prior to the noted date through the noted date, inclusive.  e.g. for 2014-03-10 it would be from 2013-03-10 through 2014-03-10 inclusive.  For each floating window size, a prior and a current value are provided, as well as the difference between them.  The dates for prior and current are specified below, and the values there are inclusive of games played on that date."
		print ""
		print ""
		print "Floating window for X number of games"
		print ""
		print "Prior date:",self.get_start_date()
		print "Current date:", self.get_end_date()
		print ""
		print "[table]Team|Prior 1|Current 1|Diff 1|Prior 5|Current 5|Diff 5|Prior 17|Current 17|Diff 17"
		all_list = self.all_view.get_model()
		for game in all_list:
			print "\\",game[0],"|",game[1],"|",game[2],"|",game[3],"|",game[4],"|",game[5],"|",game[6],"|",game[7],"|",game[8],"|",game[9]
		print "[/table]"
		print ""
		print ""
		print "Floating window for X number of years"
		print ""
		print "Prior date:",self.get_start_date()
		print "Current date:", self.get_end_date()
		print ""
		print "[table]Team|Prior 1|Current 1|Diff 1|Prior 5|Current 5|Diff 5"
		all_list = self.all_view.get_model()
		for game in all_list:
			print "\\",game[0],"|",game[10],"|",game[11],"|",game[12],"|",game[13],"|",game[14],"|",game[15]
		print "[/table]"

	### Clear the model table.
	def clear(self):
		self.all_view.get_model().clear()
		self.calc_progress.set_visible(False)

	### Recalculate the models for all teams
	def repop(self):
		season_id = self.get_season_id()
		all_list = self.all_view.get_model()
		all_list.clear()
		start_date = self.get_start_date()
		end_date = self.get_end_date()

		if season_id:
			team_list = []
			map(team_list.append, self.JTN_db.get_teams(season_id = season_id))
			team_list.sort()

			for team in team_list:
				gms1_start = self.calc_window(team, games = 1, end_date_txt = start_date)
				gms5_start = self.calc_window(team, games = 5, end_date_txt = start_date)
				gms17_start = self.calc_window(team, games = 17, end_date_txt = start_date)
				yrs1_start = self.calc_window(team, years = 1, end_date_txt = start_date)
				yrs5_start = self.calc_window(team, years = 5, end_date_txt = start_date)

				gms1_end = self.calc_window(team, games = 1, end_date_txt = end_date)
				gms5_end = self.calc_window(team, games = 5, end_date_txt = end_date)
				gms17_end = self.calc_window(team, games = 17, end_date_txt = end_date)
				yrs1_end = self.calc_window(team, years = 1, end_date_txt = end_date)
				yrs5_end = self.calc_window(team, years = 5, end_date_txt = end_date)

				gms1_diff = gms1_end - gms1_start
				gms5_diff = gms5_end - gms5_start
				gms17_diff = gms17_end - gms17_start
				yrs1_diff = yrs1_end - yrs1_start
				yrs5_diff = yrs5_end - yrs5_start
				
				all_list.append((team[1], gms1_start, gms1_end, gms1_diff, gms5_start, gms5_end, gms5_diff, gms17_start, gms17_end, gms17_diff, yrs1_start, yrs1_end, yrs1_diff, yrs5_start, yrs5_end, yrs5_diff))

	def calc_window(self, team, games = None, years = None, end_date_txt = None):
		if end_date_txt == None:
			return 0
		end_date = datetime.datetime.strptime(end_date_txt, "%Y-%m-%d")
		if years:
			start_date = datetime.date(end_date.year - years, end_date.month, end_date.day)
			start_date_txt = start_date.isoformat()
		else:
			start_date = None
			start_date_txt = None
		games_played = self.JTN_db.get_all_games(home_team = team[0], played = "TRUE", start_date = start_date_txt, end_date = end_date.isoformat(), ordered = True)
		if games:
			games_trimmed = games_played[:games]
		else:
			games_trimmed = games_played

		result = 0.0
		result += sum(map(lambda x: x[13], games_trimmed))
		average = int(round(result / len(games_trimmed)))
		return average
