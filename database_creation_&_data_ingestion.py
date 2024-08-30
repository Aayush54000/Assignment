import sqlite3
import json
import os
from glob import glob

class CricketDataIngestion:
    def __init__(self, db_name='odi_cricket.db', base_dir='./data'):
        self.db_name = db_name
        self.base_dir = base_dir
        self.create_db()
 
    def create_db(self):
        """Creates the SQLite database and tables only if the database doesn't exist."""
        if not os.path.exists(self.db_name):
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                match_id TEXT PRIMARY KEY,
                date TEXT,
                city TEXT,
                venue TEXT,
                gender TEXT,
                match_type TEXT,
                season TEXT,
                team1 TEXT,
                team2 TEXT,
                toss_winner TEXT,
                toss_decision TEXT,
                winner TEXT,
                win_type TEXT,
                win_margin INTEGER
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS innings (
                inning_id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT,
                team TEXT,
                over INTEGER,
                ball INTEGER,
                batter TEXT,
                bowler TEXT,
                runs_batter INTEGER,
                runs_extras INTEGER,
                runs_total INTEGER,
                wicket TEXT,
                FOREIGN KEY(match_id) REFERENCES matches(match_id)
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                player_id TEXT PRIMARY KEY,
                name TEXT
            )
            ''')

            conn.commit()
            conn.close()
            print(f"Database '{self.db_name}' created successfully!")
        else:
            print(f"Database '{self.db_name}' already exists. Skipping creation.")

    def populate_db(self, json_file):
        """Populates the database with data from the JSON file without skipping files due to missing keys."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        with open(json_file) as f:
            data = json.load(f)

        match_info = data.get('info', {})
        match_id = f"{match_info.get('dates', [''])[0]}_{match_info.get('teams', [''])[0]}_vs_{match_info.get('teams', [''])[1]}_{match_info.get('venue', '')}"

        cursor.execute('SELECT 1 FROM matches WHERE match_id = ?', (match_id,))
        match_exists = cursor.fetchone()

        if not match_exists:
            try:
                match_row = (
                    match_id,
                    match_info.get('dates', [None])[0],
                    match_info.get('city', None),
                    match_info.get('venue', None),
                    match_info.get('gender', None),
                    match_info.get('match_type', None),
                    match_info.get('season', None),
                    match_info.get('teams', [None, None])[0],
                    match_info.get('teams', [None, None])[1],
                    match_info.get('toss', {}).get('winner', None),
                    match_info.get('toss', {}).get('decision', None),
                    match_info.get('outcome', {}).get('winner', None),
                    list(match_info.get('outcome', {}).get('by', {}).keys())[0] if match_info.get('outcome', {}).get('by') else None,
                    list(match_info.get('outcome', {}).get('by', {}).values())[0] if match_info.get('outcome', {}).get('by') else None
                )
                cursor.execute('INSERT INTO matches VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', match_row)
                print(f"Inserted match {match_id} into matches table.")
            except sqlite3.IntegrityError as e:
                print(f"Failed to insert match {match_id}: {e}")
        else:
            print(f"Match {match_id} already exists in the database. Skipping match insertion.")

        for team, players in match_info.get('players', {}).items():
            for player in players:
                player_id = match_info.get('registry', {}).get('people', {}).get(player, None)
                if player_id:
                    cursor.execute('INSERT OR IGNORE INTO players (player_id, name) VALUES (?, ?)', (player_id, player))

        for inning in data.get('innings', []):
            team = inning.get('team', None)
            for over_data in inning.get('overs', []):
                over_number = over_data.get('over', None)
                for ball_number, delivery in enumerate(over_data.get('deliveries', []), start=1):
                    batter = delivery.get('batter', None)
                    bowler = delivery.get('bowler', None)
                    runs_batter = delivery.get('runs', {}).get('batter', None)
                    runs_extras = delivery.get('runs', {}).get('extras', None)
                    runs_total = delivery.get('runs', {}).get('total', None)
                    wicket = delivery.get('wickets', None)

                    cursor.execute('''
                    INSERT INTO innings (match_id, team, over, ball, batter, bowler, runs_batter, runs_extras, runs_total, wicket) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (match_id, team, over_number, ball_number, batter, bowler, runs_batter, runs_extras, runs_total, json.dumps(wicket)))

        conn.commit()
        conn.close()
        print(f"Data from '{json_file}' inserted into database '{self.db_name}' successfully!")

    def ingest_data(self):
        """Ingests data from all JSON files in the latest directory."""
        latest_dir = max([os.path.join(self.base_dir, d) for d in os.listdir(self.base_dir)], key=os.path.getmtime)
        json_files = glob(os.path.join(latest_dir, '*.json'))

        for json_file_path in json_files:
            self.populate_db(json_file_path)

if __name__ == "__main__":
    ingestion = CricketDataIngestion()
    ingestion.ingest_data()
    print("Database ingestion completed successfully!")