"""
Demo tools — mock NBA data for environments without nba-stats-mcp or Ollama.

These return realistic hardcoded data so workshop scripts run identically
in demo mode. Students never see these — they exist for CI/testing only.
"""

from __future__ import annotations

from strands import tool


@tool
def get_scoreboard(date: str = "") -> str:
    """Get today's NBA scoreboard with live scores and game status.

    Args:
        date: Date in YYYYMMDD format. Defaults to today.

    Returns:
        Formatted string with game scores and status.
    """
    return """NBA Scoreboard — May 5, 2026

🏀 Golden State Warriors 108 - Los Angeles Lakers 102 (Final)
   Top performers: S. Curry 32 PTS, 8 AST | L. James 28 PTS, 10 REB

🏀 Denver Nuggets 95 - Minnesota Timberwolves 88 (Q3 8:42)
   Top performers: N. Jokic 22 PTS, 11 REB | A. Edwards 20 PTS

🏀 Boston Celtics 78 - New York Knicks 72 (Q2 3:15)
   Top performers: J. Tatum 18 PTS | J. Brunson 16 PTS

🏀 Oklahoma City Thunder vs Dallas Mavericks (8:30 PM ET)
🏀 Phoenix Suns vs Sacramento Kings (10:00 PM ET)
🏀 LA Clippers vs Portland Trail Blazers (10:30 PM ET)"""


@tool
def get_box_score(game_id: str) -> str:
    """Get detailed box score for a specific game.

    Args:
        game_id: The NBA game ID.

    Returns:
        Formatted box score with player stats.
    """
    return """Box Score: Warriors 108 - Lakers 102 (Final)

GOLDEN STATE WARRIORS
Player           MIN  PTS  REB  AST  STL  BLK
S. Curry          38   32    5    8    2    0
A. Wiggins        36   22    6    3    1    1
D. Green          34    8   10    7    2    1
K. Looney         28    6   12    2    0    3
B. Podziemski     32   14    4    5    1    0

LOS ANGELES LAKERS
Player           MIN  PTS  REB  AST  STL  BLK
L. James          40   28   10    6    1    2
A. Davis          38   24   13    3    1    3
A. Reaves         36   18    4    8    2    0
D. Russell        30   16    3    7    1    0
R. Hachimura      26   10    5    1    0    1"""


@tool
def get_standings(conference: str = "") -> str:
    """Get current NBA standings.

    Args:
        conference: 'east', 'west', or empty for both.

    Returns:
        Formatted standings table.
    """
    west = """Western Conference
#   Team                    W    L    PCT    GB
1   Oklahoma City Thunder   58   24   .707   -
2   Denver Nuggets          54   28   .659   4.0
3   Minnesota Timberwolves  52   30   .634   6.0
4   Dallas Mavericks        50   32   .610   8.0
5   Phoenix Suns            49   33   .598   9.0
6   Golden State Warriors   46   36   .561   12.0
7   Los Angeles Lakers      44   38   .537   14.0
8   Sacramento Kings        42   40   .512   16.0"""

    east = """Eastern Conference
#   Team                    W    L    PCT    GB
1   Boston Celtics          62   20   .756   -
2   New York Knicks         54   28   .659   8.0
3   Milwaukee Bucks         52   30   .634   10.0
4   Cleveland Cavaliers     50   32   .610   12.0
5   Philadelphia 76ers      47   35   .573   15.0
6   Indiana Pacers          46   36   .561   16.0
7   Miami Heat              44   38   .537   18.0
8   Orlando Magic           42   40   .512   20.0"""

    if conference.lower() == "west":
        return west
    elif conference.lower() == "east":
        return east
    return f"{west}\n\n{east}"
