
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
