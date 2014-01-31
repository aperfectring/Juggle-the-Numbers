
import sqlite3

def init(dbname = None):

	if dbname == None:
		dbname = "test.sqlite"
	print "Opening database",dbname
	db = sqlite3.connect(dbname, check_same_thread = False)
	cur = db.cursor()
	cur.execute("CREATE TABLE IF NOT EXISTS leagues (" +
                    "league_name STRING UNIQUE, " +
                    "id INTEGER PRIMARY KEY ASC, " + 
                    "country STRING, " + 
                    "confederation STRING, " + 
                    "level INTEGER)")
	cur.execute("CREATE TABLE IF NOT EXISTS seasons (" + 
                    "start DATE, " + 
                    "end DATE, " + 
                    "id INTEGER PRIMARY KEY ASC, " + 
                    "league INTEGER)")
	cur.execute("CREATE TABLE IF NOT EXISTS teams (" +
                    "id INTEGER PRIMARY KEY ASC, " +
                    "team_name STRING UNIQUE, " +
                    "city STRING)")
	cur.execute("CREATE TABLE IF NOT EXISTS team_season (" +
                    "team_id INTEGER, " +
                    "season_id INTEGER)")
	cur.execute("CREATE TABLE IF NOT EXISTS games (" +
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
	cur.execute("CREATE TABLE IF NOT EXISTS version (" +
		    "number INTEGER)")

	cur.execute("SELECT number FROM version")
	row = cur.fetchone()
	if(row == None):
		print "Adding version number to table"
		cur.execute("INSERT INTO version (number) VALUES('1')")
		db.commit()
	cur.execute("SELECT number FROM version")
	row = cur.fetchone()
	while (row != None):
		if(row[0] == 1):
			print "Got a version 1 DB, upgrading to version 2"
			cur.execute("ALTER TABLE teams ADD COLUMN abbr STRING")
			cur.execute("DELETE FROM version")
			cur.execute("INSERT INTO version (number) VALUES('2')")
			db.commit()
		elif(row[0] == 2):
			print "Got a version 2 DB, upgrading to version 3"
			cur.execute("CREATE TABLE IF NOT EXISTS season_confs (" +
					"season_id INTEGER, " +
					"conf_id INTEGER)")
			cur.execute("CREATE TABLE IF NOT EXISTS confs (" +
					"conf_id INTEGER PRIMARY KEY ASC, " +
					"conf_name STRING)")
			cur.execute("DELETE FROM version")
			cur.execute("INSERT INTO version (number) VALUES('3')")
			db.commit()
		elif(row[0] == 3):
			print "Got a version 3 DB, upgrading to version 4"
			cur.execute("ALTER TABLE team_season ADD COLUMN conf_id INTEGER")
			cur.execute("DELETE FROM version")
			cur.execute("INSERT INTO version (number) VALUES('4')")
			db.commit()
		elif(row[0] == 4):
			print "Got a version 4 DB, upgrading to version 5"
			cur.execute("ALTER TABLE games ADD COLUMN attendance INTEGER")
			cur.execute("DELETE FROM version")
			cur.execute("INSERT INTO version (number) VALUES('5')")
			db.commit()
		elif(row[0] == 5):
			print "Got a version 5 DB, upgrading to version 6"
			cur.execute("CREATE TABLE IF NOT EXISTS players (" +
					"id INTEGER PRIMARY KEY ASC, " +
					"first_name STRING, " +
					"last_name STRING, " +
					"nation STRING, " +
					"home STRING)")
			cur.execute("CREATE TABLE IF NOT EXISTS player_team (" +
					"player_id INTEGER, " +
					"team_id INTEGER, " +
					"start DATE, " +
					"end DATE, " +
					"loan BOOL, " +
					"number INTEGER)")
			cur.execute("DELETE FROM version")
			cur.execute("INSERT INTO version (number) VALUES('6')")
			db.commit()
		elif(row[0] == 6):
			print "Got a version 6 DB"
			break
		else:
			print "Error, got an unsupported DB version"
			return
		cur.execute("SELECT number FROM version")
		row = cur.fetchone()

	cur.execute("SELECT * FROM leagues")
	print "Found",len(cur.fetchall()),"leagues."

	cur.execute("SELECT * FROM seasons")
	print "Found",len(cur.fetchall()),"seasons."

	cur.execute("SELECT * FROM teams")
	print "Found",len(cur.fetchall()),"teams."

	cur.execute("SELECT * FROM games")
	print "Found",len(cur.fetchall()),"games."

	return (db, cur)

