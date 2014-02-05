
import sqlite3

class JTN_db:
	def __init__(self):
		self.db = None
		self.cur = None

	def upgrade_db_to_v2(self):
		print "Got a version 1 DB, upgrading to version 2"
		self.cur.execute("ALTER TABLE teams ADD COLUMN abbr STRING")
		self.cur.execute("DELETE FROM version")
		self.cur.execute("INSERT INTO version (number) VALUES('2')")
		self.commit()

	def upgrade_db_to_v3(self):
		print "Got a version 2 DB, upgrading to version 3"
		self.cur.execute("CREATE TABLE IF NOT EXISTS season_confs (" +
				"season_id INTEGER, " +
				"conf_id INTEGER)")
		self.cur.execute("CREATE TABLE IF NOT EXISTS confs (" +
				"conf_id INTEGER PRIMARY KEY ASC, " +
				"conf_name STRING)")
		self.cur.execute("DELETE FROM version")
		self.cur.execute("INSERT INTO version (number) VALUES('3')")
		self.commit()

	def upgrade_db_to_v4(self):
		print "Got a version 3 DB, upgrading to version 4"
		self.cur.execute("ALTER TABLE team_season ADD COLUMN conf_id INTEGER")
		self.cur.execute("DELETE FROM version")
		self.cur.execute("INSERT INTO version (number) VALUES('4')")
		self.commit()

	def upgrade_db_to_v5(self):
		print "Got a version 4 DB, upgrading to version 5"
		self.cur.execute("ALTER TABLE games ADD COLUMN attendance INTEGER")
		self.cur.execute("DELETE FROM version")
		self.cur.execute("INSERT INTO version (number) VALUES('5')")
		self.commit()

	def upgrade_db_to_v6(self):
		print "Got a version 5 DB, upgrading to version 6"
		self.cur.execute("CREATE TABLE IF NOT EXISTS players (" +
				"id INTEGER PRIMARY KEY ASC, " +
				"first_name STRING, " +
				"last_name STRING, " +
				"nation STRING, " +
				"home STRING)")
		self.cur.execute("CREATE TABLE IF NOT EXISTS player_team (" +
				"player_id INTEGER, " +
				"team_id INTEGER, " +
				"start DATE, " +
				"end DATE, " +
				"loan BOOL, " +
				"number INTEGER)")
		self.cur.execute("DELETE FROM version")
		self.cur.execute("INSERT INTO version (number) VALUES('6')")
		self.commit()
	
	def open(self, dbname = None):
		if dbname == None:
			dbname = "test.sqlite"

		print "Opening database",dbname
		self.db = sqlite3.connect(dbname, check_same_thread = False)
		self.cur = self.db.cursor()
		self.cur.execute("CREATE TABLE IF NOT EXISTS leagues (" +
                	    "league_name STRING UNIQUE, " +
	                    "id INTEGER PRIMARY KEY ASC, " + 
        	            "country STRING, " + 
                	    "confederation STRING, " + 
	                    "level INTEGER)")
		self.cur.execute("CREATE TABLE IF NOT EXISTS seasons (" + 
                	    "start DATE, " + 
	                    "end DATE, " + 
        	            "id INTEGER PRIMARY KEY ASC, " + 
                	    "league INTEGER)")
		self.cur.execute("CREATE TABLE IF NOT EXISTS teams (" +
        	            "id INTEGER PRIMARY KEY ASC, " +
                	    "team_name STRING UNIQUE, " +
	                    "city STRING)")
		self.cur.execute("CREATE TABLE IF NOT EXISTS team_season (" +
                	    "team_id INTEGER, " +
	                    "season_id INTEGER)")
		self.cur.execute("CREATE TABLE IF NOT EXISTS games (" +
			    "season_id INTEGER, " +
			    "date DATE, " +
			    "home_id INTEGER, " +
			    "home_goals INTEGER, " +
			    "home_pks INTEGER, " +
			    "away_id INTEGER, " +
			    "away_goals INTEGER, " +
			    "away_pks INTEGER, " +
			    "aet BOOL, " +
			    "pks BOOL, " +
			    "played BOOL, " +
			    "game_style INTEGER, " +
			    "id INTEGER PRIMARY KEY ASC)")
		self.cur.execute("CREATE TABLE IF NOT EXISTS version (" +
			    "number INTEGER)")

		self.cur.execute("SELECT number FROM version")
		row = self.cur.fetchone()
		if(row == None):
			print "Adding version number to table"
			self.cur.execute("INSERT INTO version (number) VALUES('1')")
			self.commit()
		self.cur.execute("SELECT number FROM version")
		row = self.cur.fetchone()
		while (row != None):
			if(row[0] == 1):
				self.upgrade_db_to_v2()
			elif(row[0] == 2):
				self.upgrade_db_to_v3()
			elif(row[0] == 3):
				self.upgrade_db_to_v4()
			elif(row[0] == 4):
				self.upgrade_db_to_v5()
			elif(row[0] == 5):
				self.upgrade_db_to_v6()
			elif(row[0] == 6):
				print "Got a version 6 DB"
				break
			else:
				print "Error, got an unsupported DB version"
				return
			self.cur.execute("SELECT number FROM version")
			row = self.cur.fetchone()

		self.cur.execute("SELECT * FROM leagues")
		print "Found",len(self.cur.fetchall()),"leagues."

		self.cur.execute("SELECT * FROM seasons")
		print "Found",len(self.cur.fetchall()),"seasons."

		self.cur.execute("SELECT * FROM teams")
		print "Found",len(self.cur.fetchall()),"teams."

		self.cur.execute("SELECT * FROM games")
		print "Found",len(self.cur.fetchall()),"games."

		return (self.db, self.cur)

	def commit(self):
		self.db.commit()

	def add_league(self):
		text = ""
		self.cur.execute("INSERT INTO leagues (league_name)VALUES ('" + text + "')")
		self.commit()

	def get_league(self, league_name):
		self.cur.execute("SELECT * FROM leagues WHERE league_name = '" + league_name + "'")
		return self.cur.fetchone()

	def get_league_id(self, league_name):
		row = self.get_league(league_name)
		if row != None:
			return row[1]
		return None
		
	def get_leagues(self):
		self.cur.execute("SELECT * FROM leagues")
		return self.cur

	def set_league(self, id, name, country, confed, level):
		self.cur.execute("UPDATE leagues " + 
                                 "SET country = '" + country + "', " + 
                                     "league_name = '" + name + "', " + 
                                     "confederation = '" + confed + "', " + 
                                     "level = '" + level + "' " + 
                                 "WHERE id = '" + str(id) + "'")
		self.commit()

	def add_season(self, league_id):
		self.cur.execute("INSERT INTO seasons (league) VALUES ('" + str(league_id) + "')")
		self.commit()

	def get_season(self, league_id = None, start_year = None, end_year = None, season_id = None):
		if(end_year == None):
			end_year = start_year

		### Query the database to get the ID
		if(season_id != None):
			self.cur.execute("SELECT * FROM seasons " + 
                                         "WHERE id = '" + str(season_id) + "'")
		elif(start_year != None) and (league_id != None):
			self.cur.execute("SELECT * FROM seasons " + 
                                         "WHERE STRFTIME('%Y',end) = '" + end_year + "' " + 
                                             "AND STRFTIME('%Y',start) = '" + start_year + "' " + 
                                             "AND league = '" + str(league_id) + "'")
		else:
			self.cur.execute("SELECT * FROM seasons WHERE end IS NULL AND start IS NULL")
		
		row = self.cur.fetchone()
		return row

	def get_seasons(self, league_id):
		self.cur.execute("SELECT * FROM seasons " + 
                                 "WHERE league = '" + str(league_id) + "' " + 
                                     "ORDER BY end DESC")
		rows = self.cur.fetchall()
		return rows
		
	def set_season(self, season_id, start_date, end_date):
		self.cur.execute("UPDATE seasons SET " +
					"start = DATE('" + start_date + "'), " +
					"end   = DATE('" + end_date   + "')  " +
					"WHERE id = '" + str(season_id) + "'")
		self.commit()

	def get_confs_by_season(self, season_id):
		if season_id != None:
			self.cur.execute("SELECT * FROM season_confs WHERE season_id = '" + str(season_id) + "'")

		return self.cur.fetchall()

	def get_conf(self, conf_id = None, conf_name = None):
		if conf_id != None:
			self.cur.execute("SELECT * FROM confs WHERE conf_id = '" + str(conf_id) + "'")
			return self.cur.fetchone()

		if conf_name != None:
			self.cur.execute("SELECT * FROM confs WHERE conf_name = '" + conf_name + "'")
			return self.cur.fetchone()

		return None

	def get_confs(self):
		self.cur.execute("SELECT * FROM confs")
		return self.cur.fetchall()

	def add_conf(self, season_id, conf_id):
		self.cur.execute("INSERT INTO season_confs (conf_id, season_id) VALUES ('" + str(conf_id) + "', '" + str(season_id) + "')")
		self.commit()

	def remove_conf(self, season_id, conf_id):
		self.cur.execute("DELETE FROM season_confs WHERE (conf_id = '" + str(conf_id) + "' AND season_id = '" + str(season_id) + "')")
		self.commit()

	def delete_conf(self, conf_id):
		self.cur.execute("UPDATE team_season SET conf_id = NULL WHERE conf_id = '" + str(conf_id) + "'")
		self.cur.execute("DELETE FROM season_confs WHERE (conf_id = '" + str(conf_id) + "')")
		self.cur.execute("DELETE FROM confs WHERE (conf_id = '" + str(conf_id) + "')")
		self.commit()

	def set_conf(self, old_name, new_name):
		self.cur.execute("UPDATE confs " +
				"SET conf_name = '" + new_name + "'" +
				"WHERE conf_name = '" + old_name + "'")
		self.commit()

	def create_conf(self, name):
		self.cur.execute("INSERT INTO confs (conf_name) " +
				"VALUES ('" + name + "')")
		self.commit()

	# id, name, city, abbr
	def get_team(self, team_id = None, name = None, abbr = None, season_id = None):
		if team_id != None:
			self.cur.execute("SELECT * FROM teams WHERE (id='" + str(team_id) + "')")
		elif name != None:
			self.cur.execute("SELECT * FROM teams WHERE (team_name='" + name + "')")
		elif ((abbr != None) and (season_id != None)):
			self.cur.execute("SELECT * FROM teams WHERE (abbr='" + abbr + "' AND id IN (" + 
						"SELECT team_id FROM team_season WHERE (season_id = '" + str(season_id) + "')" +
						"))")
		elif (abbr != None):
			self.cur.execute("SELECT * FROM teams WHERE (abbr='" + abbr + "')")
		return self.cur.fetchone()

	# id, name, city, abbr
	def get_teams(self, season_id = None, conf_id = None):
		if season_id != None:
			conf_id_text = ""
			if conf_id != None:
				conf_id_text = " AND conf_id = '" + str(conf_id) + "'"
			self.cur.execute("SELECT * FROM teams WHERE (id IN (" + 
						"SELECT team_id FROM team_season WHERE (season_id = '" + str(season_id) + "'" +
							conf_id_text + ")" +
						"))")
		else:
			self.cur.execute("SELECT * FROM teams")
		return self.cur.fetchall()

	# team, season, conf
	def get_teams_by_season(self, season_id):
		self.cur.execute("SELECT * FROM team_season WHERE (season_id='" + str(season_id) + "')")
		return self.cur.fetchall()

	def add_team(self, season_id, team_id):
		self.cur.execute("INSERT INTO team_season (team_id, season_id) VALUES ('" + str(team_id) + "', '" + str(season_id) + "')")
		self.commit()

	def remove_team(self, season_id, team_id):
		self.cur.execute("DELETE FROM team_season WHERE (team_id = '" + str(team_id) + "' AND season_id = '" + str(season_id) + "')")
		self.commit()

	def delete_games(self, game_id = None, team_id = None):
		if game_id != None:
			self.cur.execute("DELETE FROM games WHERE (id = '" + str(game_id) + "')")
		elif team_id != None:
			self.cur.execute("DELETE FROM games WHERE (home_id='" + str(team_id) + "' OR away_id='" + str(team_id) + "')")
		self.commit()

	def delete_team(self, team_id):
		self.delete_games(team_id = team_id)
		self.cur.execute("DELETE FROM team_season WHERE (team_id = '" + str(team_id) + "')")
		self.cur.execute("DELETE FROM teams WHERE (id = '" + str(team_id) + "')")
		self.commit()

	def get_team_conf(self, team_id, season_id):
		self.cur.execute("SELECT conf_id FROM team_season WHERE (team_id = '" + str(team_id) + "' AND season_id = '" + str(season_id) + "')")
		return self.cur.fetchone()
		
	def set_team_conf(self, team_id, season_id, conf_id):
		conf_text = None
		if conf_id == None:
			conf_text = "conf_id = NULL"
		else:
			conf_text = "conf_id = " + str(conf_id)
		self.cur.execute("UPDATE team_season SET " + conf_text + 
				" WHERE (team_id = '" + str(team_id) + "' " +
					"AND season_id = '" + str(season_id) + "')")
		self.commit()

	def edit_team(self, old_name, new_name, city, abbr):
		self.cur.execute("UPDATE teams " + 
	                           "SET team_name = '" + new_name + "', " + 
	                              "city = '" + city + "', " + 
	                              "abbr = '" + abbr + "' " + 
	                           "WHERE team_name = '" + old_name + "'")
		self.commit()

	def create_team(self, name, city, abbr):
		self.cur.execute("INSERT INTO teams (team_name, city, abbr) " + 
	                           "VALUES ('" + name + "', '" +
	                              city + "', '" + 
				      abbr + "')")
		self.commit()

	# 0:season_id, 1:date, 2:home_id, 3:home_goals, 4:home_pks, 5:away_id, 6:away_goals, 7:away_pks, 8:aet, 9:pks, 10:played, 11:game_style, 12:game_id, 13:attendance
	def get_all_games(self, season_id = None, ordered = False, played = None, start_date = None, end_date = None, date = None, home_team = None, away_team = None, any_team = None, home_win = None, away_win = None, game_tied = None):
		order_text = ""
		where_parts = []
		if ordered == True:
			order_text = " ORDER BY date DESC"

		if season_id != None:
			where_parts.append("season_id='" + str(season_id) + "'")
		if played != None:
			where_parts.append("played='" + str(played) + "'")
		if start_date != None:
			where_parts.append("date>='" + start_date + "'")
		if end_date != None:
			where_parts.append("date<='" + end_date + "'")
		if date != None:
			where_parts.append("date='" + date + "'")
		if home_team != None:
			where_parts.append("home_id='" + str(home_team) + "'")
		if away_team != None:
			where_parts.append("away_id='" + str(away_team) + "'")
		if any_team != None:
			where_parts.append("(home_id='" + str(any_team) + "' OR away_id='" + str(any_team) + "')")
		if home_win != None:
			where_parts.append("home_goals > away_goals")
		if away_win != None:
			where_parts.append("away_goals > home_goals")
		if game_tied != None:
			where_parts.append("home_goals = away_goals")

		where_text = ""
		if len(where_parts):
			where_text = "WHERE (" + " AND ".join(where_parts) + ") "
		
		self.cur.execute("SELECT * FROM games " + where_text + order_text)
		return self.cur.fetchall()

	# 0:season_id, 1:date, 2:home_id, 3:home_goals, 4:home_pks, 5:away_id, 6:away_goals, 7:away_pks, 8:aet, 9:pks, 10:played, 11:game_style, 12:game_id, 13:attendance
	def get_game(self, season_id = None, home_id = None, away_id = None, date = None):
		parts_arr = []

		if season_id != None:
			parts_arr.append("season_id = '" + str(season_id) + "'")
		if home_id != None:
			parts_arr.append("home_id = '" + str(home_id) + "'")
		if away_id != None:
			parts_arr.append("away_id = '" + str(away_id) + "'")
		if date != None:
			parts_arr.append("date = '" + date + "'")

		where_clause = " AND ".join(parts_arr)
		if len(where_clause):
			self.cur.execute("SELECT * FROM games WHERE (" + where_clause + ")")
			return self.cur.fetchone()
		return None

	def update_game(self, game_id, season_id = None, date = None, home_id = None, home_goals = None, home_pks = None, away_id = None, away_goals = None, away_pks = None, aet = None, pks = None, game_style = None, played = None, attendance = None):
		set_arr = []
		if season_id != None:
			set_arr.append("season_id = '" + str(season_id) + "'")
		if date != None:
			set_arr.append("date = '" + str(date) + "'")
		if home_id != None:
			set_arr.append("home_id = '" + str(home_id) + "'")
		if home_goals != None:
			set_arr.append("home_goals = '" + str(home_goals) + "'")
		if home_pks != None:
			set_arr.append("home_pks = '" + str(home_pks) + "'")
		if away_id != None:
			set_arr.append("away_id = '" + str(away_id) + "'")
		if away_goals != None:
			set_arr.append("away_goals = '" + str(away_goals) + "'")
		if away_pks != None:
			set_arr.append("away_pks = '" + str(away_pks) + "'")
		if aet != None:
			set_arr.append("aet = '" + str(aet) + "'")
		if pks != None:
			set_arr.append("pks = '" + str(pks) + "'")
		if game_style != None:
			set_arr.append("game_style = '" + str(game_style) + "'")
		if played != None:
			set_arr.append("played = '" + str(played) + "'")
		if attendance != None:
			set_arr.append("attendance = '" + str(attendance) + "'")

		set_clause = ", ".join(set_arr)
		if len(set_clause):
			self.cur.execute("UPDATE games SET " + set_clause +
						"WHERE (id = '" + str(game_id) + "')")
			self.commit()

	def create_game(self, season_id = None, date = None, home_id = None, home_goals = None, home_pks = None, away_id = None, away_goals = None, away_pks = None, aet = None, pks = None, game_style = None, played = None, attendance = None):
		set_arr = []
		val_arr = []
		if season_id != None:
			set_arr.append("season_id")
			val_arr.append("'" + str(season_id) + "'")
		if date != None:
			set_arr.append("date")
			val_arr.append("'" + str(date) + "'")
		if home_id != None:
			set_arr.append("home_id")
			val_arr.append("'" + str(home_id) + "'")
		if home_goals != None:
			set_arr.append("home_goals")
			val_arr.append("'" + str(home_goals) + "'")
		if home_pks != None:
			set_arr.append("home_pks")
			val_arr.append("'" + str(home_pks) + "'")
		if away_id != None:
			set_arr.append("away_id")
			val_arr.append("'" + str(away_id) + "'")
		if away_goals != None:
			set_arr.append("away_goals")
			val_arr.append("'" + str(away_goals) + "'")
		if away_pks != None:
			set_arr.append("away_pks")
			val_arr.append("'" + str(away_pks) + "'")
		if aet != None:
			set_arr.append("aet")
			val_arr.append("'" + str(aet) + "'")
		if pks != None:
			set_arr.append("pks")
			val_arr.append("'" + str(pks) + "'")
		if game_style != None:
			set_arr.append("game_style")
			val_arr.append("'" + str(game_style) + "'")
		if played != None:
			set_arr.append("played")
			val_arr.append("'" + str(played) + "'")
		if attendance != None:
			set_arr.append("attendance")
			val_arr.append("'" + str(attendance) + "'")

		set_clause = ", ".join(set_arr)
		val_clause = ", ".join(val_arr)
		if len(set_clause):
			self.cur.execute("INSERT INTO games (" + set_clause + ") " +
					"VALUES (" + val_clause + ")")
			self.commit()

