import sqlite3
from prettytable import PrettyTable

class CricketStatsQueries:
    def __init__(self, db_name='odi_cricket.db'):
        self.db_name = db_name

    def _run_query(self, query, headers):
        """Helper method to run a query and display results in a formatted table."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute(query)
        results = cursor.fetchall()

        table = PrettyTable()
        table.field_names = headers

        for row in results:
            table.add_row(row)

        print(table)
        conn.close()

    def team_win_statistics(self):
        """Runs a query to get team win statistics by gender and season."""
        query = """
        SELECT 
            team,
            gender,
            season,
            COUNT(*) AS total_matches,
            SUM(CASE WHEN winner = team THEN 1 ELSE 0 END) AS total_wins,
            ROUND(100.0 * SUM(CASE WHEN winner = team THEN 1 ELSE 0 END) / COUNT(*), 2) AS win_percentage
        FROM (
            SELECT team1 AS team, gender, season, winner FROM matches
            UNION ALL
            SELECT team2 AS team, gender, season, winner FROM matches
        )
        WHERE winner IS NOT NULL
        GROUP BY team, gender, season;
        """
        headers = ["Team", "Gender", "Season", "Total Matches", "Total Wins", "Win Percentage"]
        self._run_query(query, headers)

    def highest_win_percentage(self):
        """Runs a query to find the team with the highest win percentage by gender."""
        query = """
        WITH ranked_teams AS (
            SELECT 
                team,
                gender,
                ROUND(100.0 * SUM(CASE WHEN winner = team THEN 1 ELSE 0 END) / COUNT(*), 2) AS win_percentage,
                DENSE_RANK() OVER (PARTITION BY gender ORDER BY ROUND(100.0 * SUM(CASE WHEN winner = team THEN 1 ELSE 0 END) / COUNT(*), 2) DESC) AS rank
            FROM (
                SELECT team1 AS team, gender, winner FROM matches
                UNION ALL
                SELECT team2 AS team, gender, winner FROM matches
            ) AS combined_matches
            WHERE winner IS NOT NULL
            GROUP BY team, gender
        )
        SELECT team, gender, win_percentage
        FROM ranked_teams
        WHERE rank = 1;
        """
        headers = ["Team", "Gender", "Win Percentage"]
        self._run_query(query, headers)

    def highest_strike_rate(self):
        """Runs a query to find the player with the highest strike rate."""
        query = """
        SELECT 
            batter,
            SUM(runs_batter) AS total_runs,
            COUNT(*) AS total_balls,
            ROUND(SUM(runs_batter) * 100.0 / COUNT(*), 2) AS strike_rate
        FROM innings
        JOIN matches ON innings.match_id = matches.match_id
        GROUP BY batter
        ORDER BY strike_rate DESC
        LIMIT 4;
        """
        headers = ["Batter", "Total Runs", "Total Balls", "Strike Rate"]
        self._run_query(query, headers)

if __name__ == "__main__":
    import argparse

    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Run cricket statistics queries.")
    parser.add_argument("query", choices=["team_win_statistics", "highest_win_percentage", "highest_strike_rate"],
                        help="Specify the query to run: team_win_statistics, highest_win_percentage, or highest_strike_rate.")

    args = parser.parse_args()

    cricket_stats = CricketStatsQueries()

    # Call the appropriate method based on the command-line argument
    if args.query == "team_win_statistics":
        cricket_stats.team_win_statistics()
    elif args.query == "highest_win_percentage":
        cricket_stats.highest_win_percentage()
    elif args.query == "highest_strike_rate":
        cricket_stats.highest_strike_rate()
