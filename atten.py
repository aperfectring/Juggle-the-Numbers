#!/usr/bin/python

import sys
import gtk

### Import local modules
import JTN_db
import League_Combo
import Season_Combo
import Date_Calendar
import Floating_Window_Notebook
import Game_Rating_Notebook

class Base:
	def __init__(self, dbname = None):
		gtk.gdk.threads_init()

		self.JTN_db = JTN_db.JTN_db()
		(self.db, self.cur) = self.JTN_db.open(dbname)

		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect('destroy', lambda w: gtk.main_quit())

		self.window_vbox = gtk.VBox(spacing=10)
		self.window_vbox.set_border_width(5)
		self.window.add(self.window_vbox)

		self.combo_hbox = gtk.HBox(spacing=10)
		self.window_vbox.pack_start(self.combo_hbox, expand = False)
		self.combo_vbox = gtk.VBox(spacing=5)
		self.combo_hbox.pack_start(self.combo_vbox, expand = False)

		self.league_vbox = gtk.VBox(spacing=5)
		self.combo_vbox.add(self.league_vbox)

		self.league_combo = League_Combo.League_Combo(self.league_vbox, self.JTN_db)
		
		self.season_vbox = gtk.VBox(spacing=5)
		self.combo_vbox.add(self.season_vbox)

		self.season_combo = Season_Combo.Season_Combo(self.season_vbox, self.JTN_db, self.league_combo.get_id)

		# When the League Combo selection changes,
		# the Season Combo needs to be repopulated
		self.league_combo.register(self.season_combo.repop)

		self.start_date_vbox = gtk.VBox(spacing=5)
		self.combo_hbox.pack_start(self.start_date_vbox, expand=False)
		self.start_date_cal = Date_Calendar.Date_Calendar(self.start_date_vbox, label_txt = "Start Date:")

		self.end_date_vbox = gtk.VBox(spacing=5)
		self.combo_hbox.pack_start(self.end_date_vbox, expand=False)
		self.end_date_cal = Date_Calendar.Date_Calendar(self.end_date_vbox, label_txt = "End Date:")

		self.notebook = gtk.Notebook()
		self.window_vbox.add(self.notebook)

		self.float_note_vbox = gtk.VBox(spacing=10)
		self.float_note_vbox.set_border_width(5)
		self.notebook.append_page(self.float_note_vbox, gtk.Label("Floating"))

		self.float_note = Floating_Window_Notebook.Floating_Window_Notebook(self.float_note_vbox, self.season_combo.get_id, self.start_date_cal.get_date, self.end_date_cal.get_date, self.JTN_db)

		# When the season combo updates,
		# the floating window needs to be repopulated.
		self.season_combo.register(self.float_note.repop)

		# When the start date calendar updates,
		# the floating window needs to be repopulated.
		self.start_date_cal.register(self.float_note.repop)

		# When the end date calendar updates,
		# the floating window needs to be repopulated.
		self.end_date_cal.register(self.float_note.repop)

		self.score_note_vbox = gtk.VBox(spacing=10)
		self.score_note_vbox.set_border_width(5)
		self.notebook.append_page(self.score_note_vbox, gtk.Label("Game Score"))

		self.score_note = Game_Rating_Notebook.Game_Rating_Notebook(self.score_note_vbox, self.season_combo.get_id, self.start_date_cal.get_date, self.end_date_cal.get_date, self.JTN_db)

		# When the season combo updates,
		# the score window needs to be repopulated.
		self.season_combo.register(self.score_note.repop)
		
		# When the start date calendar updates,
		# the score window needs to be repopulated.
		self.start_date_cal.register(self.score_note.repop)

		# When the end date calendar updates,
		# the score window needs to be repopulated.
		self.end_date_cal.register(self.score_note.repop)


		self.league_combo.repop()
		self.window.show_all()

	def main(self):
		gtk.gdk.threads_enter()
		gtk.main()

if __name__ == "__main__":
	if len(sys.argv) > 1:
		base = Base(sys.argv[1])
	else:
		base = Base()
	base.main()
