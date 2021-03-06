
import gtk
import gobject
import datetime

### The standard array of different types of game format.
style_text_array = [
		"Standard format",
		"AET and PKs format",
		"Golden goal AET format",
		"Home+Away Game 1 format",
		"Home+Away Game 2 format"
		]

class Games_Notebook:
	def __init__(self, parent_box, JTN_db, get_season_id):
		self.parent_box = parent_box
		self.JTN_db = JTN_db
		self.get_season_id = get_season_id
		self.callback_list = []

		self.list_hbox = gtk.HBox(spacing=10)
		self.list_hbox.set_border_width(5)
		self.parent_box.pack_start(self.list_hbox)

		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.list_hbox.pack_start(scrolled_window)

		list_store = gtk.ListStore(gobject.TYPE_STRING,		# Date
						gobject.TYPE_STRING,	# Home
						gobject.TYPE_STRING,	# Home goals
						gobject.TYPE_STRING,	# Home PKs
						gobject.TYPE_STRING,	# Away
						gobject.TYPE_STRING,	# Away goals
						gobject.TYPE_STRING,	# Away PKs
						gobject.TYPE_STRING,	# AET
						gobject.TYPE_STRING,	# PKs
						gobject.TYPE_STRING,	# Style
						gobject.TYPE_STRING,	# Played
						gobject.TYPE_STRING)    # Attendance

		self.all_view = gtk.TreeView()
		scrolled_window.add(self.all_view)
		self.all_view.set_model(list_store)

		column = gtk.TreeViewColumn("Date", gtk.CellRendererText(), text=0)
		column.set_sort_column_id(0)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Home", gtk.CellRendererText(), text=1)
		column.set_sort_column_id(1)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Home\nGoals", gtk.CellRendererText(), text=2)
		column.set_sort_column_id(2)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Home PK\nGoals", gtk.CellRendererText(), text=3)
		column.set_sort_column_id(3)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Away", gtk.CellRendererText(), text=4)
		column.set_sort_column_id(4)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Away\nGoals", gtk.CellRendererText(), text=5)
		column.set_sort_column_id(5)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Away PK\nGoals", gtk.CellRendererText(), text=6)
		column.set_sort_column_id(6)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("AET", gtk.CellRendererText(), text=7)
		column.set_sort_column_id(7)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("PKs", gtk.CellRendererText(), text=8)
		column.set_sort_column_id(8)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Style", gtk.CellRendererText(), text=9)
		column.set_sort_column_id(9)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Played", gtk.CellRendererText(), text=10)
		column.set_sort_column_id(10)
		self.all_view.append_column(column)

		column = gtk.TreeViewColumn("Attendance", gtk.CellRendererText(), text=11)
		column.set_sort_column_id(11)
		self.all_view.append_column(column)

		self.gameops_hbox = gtk.HBox(spacing=10)
		self.gameops_hbox.set_border_width(5)
		self.parent_box.pack_end(self.gameops_hbox, expand=False)
		
		self.game_add_button = gtk.Button("Add game")
		self.gameops_hbox.add(self.game_add_button)
		self.game_add_button.connect('clicked', self.edit_game)

		self.game_edit_button = gtk.Button("Edit game")
		self.gameops_hbox.add(self.game_edit_button)
		self.game_edit_button.connect('clicked', self.edit_game)

		self.game_delete_button = gtk.Button("Delete game")
		self.gameops_hbox.add(self.game_delete_button)
		self.game_delete_button.connect('clicked', self.delete_game)

	### Register with the class for callbacks on updates
	def register(self, callback):
		self.callback_list.append(callback)


	### Update the treeview with all games pertaining to the specified league/season
	def repop(self):
		sid = self.get_season_id()
		all_list = self.all_view.get_model()

		all_list.clear()
		all_games = self.JTN_db.get_all_games(sid)
		for game in all_games:
			home_text = self.JTN_db.get_team(team_id = game[2])[3] # 3rd item is abbr

			away_text = self.JTN_db.get_team(team_id = game[5])[3] # 3rd item is abbr

			all_list.append( (game[1], home_text, game[3], game[4], away_text, game[6], game[7], game[8], game[9], style_text_array[game[11]], game[10], game[13]) )
			
		map(lambda x: x(), self.callback_list)

	### Get the game information tuple from the treeview
	def get_game(self, view):
		all_list = view.get_model()
		if view.get_cursor()[0]:
			itera = all_list.iter_nth_child(None, view.get_cursor()[0][0])
			date = all_list.get_value(itera, 0)
			home = all_list.get_value(itera, 1)
			home_goals = all_list.get_value(itera, 2)
			home_pks = all_list.get_value(itera, 3)
			away = all_list.get_value(itera, 4)
			away_goals = all_list.get_value(itera, 5)
			away_pks = all_list.get_value(itera, 6)
			aet = all_list.get_value(itera, 7)
			pks = all_list.get_value(itera, 8)
			style = all_list.get_value(itera, 9)
			played = all_list.get_value(itera, 10)
			attendance = all_list.get_value(itera, 11)
		else:
			date = None
			home = None
			home_goals = None
			home_pks = None
			away = None
			away_goals = None
			away_pks = None
			aet = None
			pks = None
			style = None
			played = None
			attendance = None
		return (date,	home, home_goals, home_pks,
				away, away_goals, away_pks,
				aet, pks, style, played,
				attendance)

	### Add the appropriate teams (from the team_season table) to the specified combo box.
	def pop_team_combo(self, combo):
		row = None
		team_list = []
		map(lambda x: team_list.append(x[3]),
		    self.JTN_db.get_teams(season_id = self.get_season_id()))
		team_list.sort()
		map(combo.append_text, team_list)



	### Delete the game selected in the treeview
	def delete_game(self, button):
		all_list = self.all_view.get_model()
		(date,
			home, home_goals, home_pks,
			away, away_goals, away_pks,
			aet, pks, style, played, attendance) = self.get_game(self.all_view)
		if date == None:
			return
		(home_id, home_text, home_city_text, home_abbr_text) = self.JTN_db.get_team(abbr = home, season_id = self.get_season_id())
		(away_id, away_text, away_city_text, away_abbr_text) = self.JTN_db.get_team(abbr = away, season_id = self.get_season_id())

		row = self.JTN_db.get_game(season_id = self.get_season_id(), home_id = home_id, away_id = away_id, date = date)
		if row != None:
			self.JTN_db.delete_games(game_id = row[12])

		self.repop()


	### Add a new game, or edit an already existing game
	def edit_game(self, button):
		# Determine if we are editing, or adding, a game
		edit = True if button.get_label() == "Edit game" else False

		all_list = self.all_view.get_model()
		# If editing, try to fetch the appropriate game information
		if edit == True:
			(date,
				home_abbr, home_goals, home_pks,
				away_abbr, away_goals, away_pks,
				aet, pks, style, played, attendance) = self.get_game(self.all_view)
			if date == None:
				edit = False


		# Create a dialog window to query the user for the game information
		dialog = gtk.Dialog("Edit Game",
				    None,
				    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
				    (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
				     gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

		dialog.set_default_response(gtk.RESPONSE_ACCEPT)

		########## DATE ###########
		date_vbox = gtk.VBox(spacing=10)
		date_vbox.set_border_width(5)
		date_vbox.show()
		dialog.vbox.pack_start(date_vbox)
		date_label = gtk.Label("Date:")
		date_label.show()
		date_vbox.pack_start(date_label)
		date_cal = gtk.Calendar()
		date_cal.show()
		date_vbox.add(date_cal)


		######### HOME TEAM STUFF #############
		home_hbox = gtk.HBox(spacing=10)
		home_hbox.set_border_width(5)
		home_hbox.show()
		dialog.vbox.pack_start(home_hbox)

		home_label = gtk.Label("Home team:")
		home_label.show()
		home_hbox.pack_start(home_label)
		home_combo = gtk.combo_box_new_text()
		home_combo.show()
		self.pop_team_combo(home_combo)
		home_hbox.add(home_combo)

		homegoals_label = gtk.Label("Home goals:")
		homegoals_label.show()
		home_hbox.pack_start(homegoals_label)
		homegoals_spin = gtk.SpinButton()
		homegoals_spin.set_range(0,100)
		homegoals_spin.set_increments(1,1)
		homegoals_spin.set_activates_default(True)
		homegoals_spin.show()
		home_hbox.pack_start(homegoals_spin)
		
		homepks_label = gtk.Label("Home PK goals:")
		homepks_label.show()
		home_hbox.pack_start(homepks_label)
		homepks_spin = gtk.SpinButton()
		homepks_spin.set_range(0,100)
		homepks_spin.set_increments(1,1)
		homepks_spin.set_activates_default(True)
		homepks_spin.show()
		home_hbox.pack_start(homepks_spin)


		######### AWAY TEAM STUFF #############
		away_hbox = gtk.HBox(spacing=10)
		away_hbox.set_border_width(5)
		away_hbox.show()
		dialog.vbox.pack_start(away_hbox)

		away_label = gtk.Label("Away team:")
		away_label.show()
		away_hbox.pack_start(away_label)
		away_combo = gtk.combo_box_new_text()
		away_combo.show()
		self.pop_team_combo(away_combo)
		away_hbox.add(away_combo)

		awaygoals_label = gtk.Label("Away goals:")
		awaygoals_label.show()
		away_hbox.pack_start(awaygoals_label)
		awaygoals_spin = gtk.SpinButton()
		awaygoals_spin.set_range(0,100)
		awaygoals_spin.set_increments(1,1)
		awaygoals_spin.set_activates_default(True)
		awaygoals_spin.show()
		away_hbox.pack_start(awaygoals_spin)
		
		awaypks_label = gtk.Label("Away PK goals:")
		awaypks_label.show()
		away_hbox.pack_start(awaypks_label)
		awaypks_spin = gtk.SpinButton()
		awaypks_spin.set_range(0,100)
		awaypks_spin.set_increments(1,1)
		awaypks_spin.set_activates_default(True)
		awaypks_spin.show()
		away_hbox.pack_start(awaypks_spin)


		############# Extra Time Stuff ###############
		et_hbox = gtk.HBox(spacing=10)
		et_hbox.set_border_width(5)
		et_hbox.show()
		dialog.vbox.pack_start(et_hbox)

		played_check = gtk.CheckButton("Game has been played")
		played_check.show()
		et_hbox.pack_start(played_check)

		aet_check = gtk.CheckButton("Went to AET")
		aet_check.show()
		et_hbox.pack_start(aet_check)

		pk_check = gtk.CheckButton("Went to PKs")
		pk_check.show()
		et_hbox.pack_start(pk_check)

		style_combo = gtk.combo_box_new_text()
		map(style_combo.append_text, style_text_array)
		style_combo.set_active(0)
		style_combo.show()
		et_hbox.pack_start(style_combo)

		############# Attendance Stuff ################
		atten_hbox = gtk.HBox(spacing=10)
		atten_hbox.set_border_width(5)
		atten_hbox.show()
		dialog.vbox.pack_start(atten_hbox)

		atten_label = gtk.Label("Attendance:")
		atten_label.show()
		atten_hbox.pack_start(atten_label)
		atten_spin = gtk.SpinButton()
		atten_spin.set_range(-1,1000000)
		atten_spin.set_increments(100,1000)
		atten_spin.set_activates_default(True)
		atten_spin.set_value(-1)
		atten_spin.show()
		atten_hbox.pack_start(atten_spin)

		season_id_text = str(self.get_season_id())

		###### Populate the widgets with the retrieved data
		if edit == True:
			# If editing, populate with the original data
			datetime_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
			date_cal.select_month(datetime_obj.month - 1, datetime_obj.year)
			date_cal.select_day(datetime_obj.day)
			model = home_combo.get_model()
			map(home_combo.set_active, filter(lambda x: model[x][0] == home_abbr, range(0,len(model))))
			homegoals_spin.set_value(int(home_goals))
			homepks_spin.set_value(int(home_pks))

			model = away_combo.get_model()
			map(away_combo.set_active, filter(lambda x: model[x][0] == away_abbr, range(0,len(model))))
			awaygoals_spin.set_value(int(away_goals))
			awaypks_spin.set_value(int(away_pks))

			aet_check.set_active(True if (aet == "TRUE") else False)
			pk_check.set_active(True if (pks == "TRUE") else False)
			played_check.set_active(True if (played == "TRUE") else False)
			model = style_combo.get_model()
			map(style_combo.set_active, filter(lambda x: model[x][0] == style, range(0,len(model))))

			map(lambda x: atten_spin.set_value(x),
				[int(attendance)] if (attendance and attendance != "NULL") else [-1])

		else:
			## If we are adding a game, get the latest date of a game in the list to
			##   provide a relavent starting date.  If no games exist, use the start
			##   date of the season.
			this_val = self.JTN_db.get_all_games(season_id = self.get_season_id(), ordered = True)
			start_date = this_val[0][1] if len(this_val) > 0 \
				else self.JTN_db.get_season(season_id = self.get_season_id())[0]
			datetime_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
			date_cal.select_month(datetime_obj.month - 1, datetime_obj.year)
			date_cal.select_day(datetime_obj.day)
			map(lambda x: played_check.set_active(x),
				[True] if datetime_obj < datetime.datetime.today() else [False])
				

		response = dialog.run()
		if response == gtk.RESPONSE_ACCEPT:
			### Get all of the updated game info from the many widgets
			newdate = date_cal.get_date()
			date_text = str(newdate[0]) + "-" + str(newdate[1]+1).zfill(2) + "-" + str(newdate[2]).zfill(2)
			model = home_combo.get_model()
			index = home_combo.get_active()
			home_abbr_text = model[index][0]
			home_goals_text = str(homegoals_spin.get_value_as_int())
			home_pks_text = str(homepks_spin.get_value_as_int())
			model = away_combo.get_model()
			index = away_combo.get_active()
			away_abbr_text = model[index][0]
			away_goals_text = str(awaygoals_spin.get_value_as_int())
			away_pks_text = str(awaypks_spin.get_value_as_int())
			aet_text = "TRUE" if (aet_check.get_active() == True) else "FALSE"
			pks_text = "TRUE" if (pk_check.get_active() == True) else "FALSE"
			played_text = "TRUE" if (played_check.get_active() == True) else "FALSE"
			model = style_combo.get_model()
			index = style_combo.get_active()
			style_text = model[index][0]
			style_num_text = str(index)
			atten_text = str(atten_spin.get_value_as_int())
			if atten_spin.get_value_as_int() == -1:
				atten_text = ""

			(home_id, home_text, home_city_text, home_abbr_text) = self.JTN_db.get_team(abbr = home_abbr_text, season_id = self.get_season_id())
			(away_id, away_text, away_city_text, away_abbr_text) = self.JTN_db.get_team(abbr = away_abbr_text, season_id = self.get_season_id())
			home_id_text = str(home_id)
			away_id_text = str(away_id)


			### Only allow data modification if the home and away teams differ.
			### Update if we are editing, otherwise create a new game
			if home_text != away_text:
				if edit == True:
					(orig_home_id, home, orig_home_city_text, orig_home_abbr_text) = self.JTN_db.get_team(abbr = home_abbr, season_id = self.get_season_id())
					(orig_away_id, away, orig_away_city_text, orig_away_abbr_text) = self.JTN_db.get_team(abbr = away_abbr, season_id = self.get_season_id())
					orig_home_id_text = str(orig_home_id)
					orig_away_id_text = str(orig_away_id)
					game_id = self.JTN_db.get_game(season_id = self.get_season_id(), home_id = orig_home_id_text, away_id = orig_away_id_text, date = date)[12]
					self.JTN_db.update_game(game_id = game_id,
								date = date_text,
								home_id = home_id_text,
								home_goals = home_goals_text,
								home_pks = home_pks_text,
								away_id = away_id_text,
								away_goals = away_goals_text,
								away_pks = away_pks_text,
								aet = aet_text,
								pks = pks_text,
								game_style = style_num_text,
								played = played_text,
								attendance = atten_text)
				else:
					self.JTN_db.create_game(season_id = self.get_season_id(),
								date = date_text,
								home_id = home_id_text,
								home_goals = home_goals_text,
								home_pks = home_pks_text,
								away_id = away_id_text,
								away_goals = away_goals_text,
								away_pks = away_pks_text,
								aet = aet_text,
								pks = pks_text,
								game_style = style_num_text,
								played = played_text,
								attendance = atten_text)

				self.repop()


		dialog.destroy()

