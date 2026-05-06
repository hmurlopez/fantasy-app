"""
FBRef Data Scraper
==================
Fetches player stats from FBRef using the `soccerdata` library (which handles
rate-limiting and HTML parsing) with a raw requests fallback.

FBRef's robots.txt asks for a 3-second delay between requests — soccerdata
handles this automatically. Be a good citizen; don't hammer the server.

Usage:
    scraper = FBRefScraper()
    players = scraper.fetch_squad_stats(league="ENG-Premier League", season="2024-25")
    gw_stats = scraper.fetch_match_stats(match_id="...")
"""

import time
import logging
from typing import Optional
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Supported league keys (FBRef / soccerdata notation)
SUPPORTED_LEAGUES = {
    "premier_league": "ENG-Premier League",
    "la_liga": "ESP-La Liga",
    "bundesliga": "GER-Bundesliga",
    "serie_a": "ITA-Serie A",
    "ligue_1": "FRA-Ligue 1",
    "champions_league": "UEFA-Champions League",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; FantasySoccerBot/1.0; "
        "educational project — respects robots.txt)"
    )
}
RATE_LIMIT_SECONDS = 3  # FBRef asks for at least 3s between requests


class FBRefScraper:
    def __init__(self, use_soccerdata: bool = True):
        self._soccerdata_available = False
        if use_soccerdata:
            try:
                import soccerdata as sd  # noqa: F401
                self._soccerdata_available = True
                logger.info("soccerdata library available — using it for FBRef access")
            except ImportError:
                logger.warning(
                    "soccerdata not installed; falling back to raw requests. "
                    "Install with: pip install soccerdata"
                )

    # ------------------------------------------------------------------
    # High-level methods used by update scripts
    # ------------------------------------------------------------------

    def fetch_squad_stats(self, league: str = "ENG-Premier League", season: str = "2024-25") -> list[dict]:
        """
        Return a list of player dicts with season-level stats.
        Each dict has keys: name, position, club, nationality, goals,
        assists, minutes, etc.
        """
        if self._soccerdata_available:
            return self._fetch_via_soccerdata(league, season)
        return self._fetch_via_requests(league, season)

    def fetch_match_stats(self, match_id: str) -> list[dict]:
        """
        Return per-player stats for a specific FBRef match ID.
        Used by the gameweek update script.
        """
        url = f"https://fbref.com/en/matches/{match_id}"
        return self._scrape_match_page(url)

    # ------------------------------------------------------------------
    # soccerdata path
    # ------------------------------------------------------------------

    def _fetch_via_soccerdata(self, league: str, season: str) -> list[dict]:
        import soccerdata as sd

        fbref = sd.FBref(leagues=league, seasons=season)
        try:
            df = fbref.read_player_season_stats(stat_type="standard")
            players = []
            for _, row in df.iterrows():
                players.append({
                    "fbref_id": row.get("player_id", ""),
                    "name": row.get("player", "Unknown"),
                    "position": self._normalise_position(str(row.get("position", "MID"))),
                    "club": str(row.get("team", "")),
                    "nationality": str(row.get("nationality", "")),
                    "goals": int(row.get("goals", 0) or 0),
                    "assists": int(row.get("assists", 0) or 0),
                    "minutes": int(row.get("minutes_90s", 0) * 90 or 0),
                })
            return players
        except Exception as exc:
            logger.error("soccerdata fetch failed: %s", exc)
            return []

    # ------------------------------------------------------------------
    # Raw requests / BeautifulSoup path
    # ------------------------------------------------------------------

    def _fetch_via_requests(self, league: str, season: str) -> list[dict]:
        """Scrape FBRef season stats table directly."""
        season_slug = season.replace("-", "-20")  # "2024-25" → "2024-2025"
        league_slug = league.replace(" ", "-").replace("ENG-", "")
        url = (
            f"https://fbref.com/en/comps/9/{season_slug}/stats/"
            f"{season_slug}-{league_slug}-Stats"
        )
        logger.info("Fetching %s", url)
        time.sleep(RATE_LIMIT_SECONDS)
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Request failed: %s", exc)
            return []

        return self._parse_stats_table(resp.text)

    def _parse_stats_table(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", {"id": "stats_standard"})
        if not table:
            logger.warning("Could not find stats table — FBRef HTML may have changed")
            return []

        players = []
        for row in table.select("tbody tr:not(.thead)"):
            cols = row.find_all(["td", "th"])
            if len(cols) < 10:
                continue
            name_tag = row.find("td", {"data-stat": "player"})
            if not name_tag or not name_tag.text.strip():
                continue
            a_tag = name_tag.find("a")
            fbref_id = ""
            if a_tag and a_tag.get("href"):
                # href like /en/players/abc123/Player-Name
                parts = a_tag["href"].split("/")
                fbref_id = parts[3] if len(parts) > 3 else ""

            def _int(stat: str) -> int:
                tag = row.find("td", {"data-stat": stat})
                try:
                    return int(tag.text.strip()) if tag and tag.text.strip() else 0
                except ValueError:
                    return 0

            def _str(stat: str) -> str:
                tag = row.find("td", {"data-stat": stat})
                return tag.text.strip() if tag else ""

            players.append({
                "fbref_id": fbref_id,
                "name": name_tag.text.strip(),
                "position": self._normalise_position(_str("position")),
                "club": _str("squad"),
                "nationality": _str("nationality"),
                "goals": _int("goals"),
                "assists": _int("assists"),
                "minutes": _int("minutes"),
            })
        return players

    def _scrape_match_page(self, url: str) -> list[dict]:
        """Parse a FBRef match report for per-player stats."""
        time.sleep(RATE_LIMIT_SECONDS)
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Match fetch failed: %s", exc)
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        results = []

        # FBRef match pages have multiple player-stats tables
        for table in soup.select("table[id^='stats_']"):
            for row in table.select("tbody tr:not(.thead)"):
                name_tag = row.find("th", {"data-stat": "player"})
                if not name_tag or not name_tag.text.strip():
                    continue

                def _int(stat: str) -> int:
                    tag = row.find("td", {"data-stat": stat})
                    try:
                        return int(tag.text.strip()) if tag and tag.text.strip() else 0
                    except ValueError:
                        return 0

                results.append({
                    "name": name_tag.text.strip(),
                    "minutes": _int("minutes"),
                    "goals": _int("goals"),
                    "assists": _int("assists"),
                    "shots_on_target": _int("shots_on_target"),
                    "yellow_cards": _int("cards_yellow"),
                    "red_cards": _int("cards_red"),
                })
        return results

    @staticmethod
    def _normalise_position(raw: str) -> str:
        """Map FBRef position strings to GK/DEF/MID/FWD."""
        raw = raw.upper().split(",")[0].strip()
        mapping = {
            "GK": "GK",
            "CB": "DEF", "LB": "DEF", "RB": "DEF", "WB": "DEF",
            "DF": "DEF",
            "DM": "MID", "CM": "MID", "AM": "MID", "LM": "MID", "RM": "MID",
            "MF": "MID",
            "LW": "FWD", "RW": "FWD", "CF": "FWD", "ST": "FWD",
            "FW": "FWD",
        }
        return mapping.get(raw, "MID")
