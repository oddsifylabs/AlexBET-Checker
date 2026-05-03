"""Bet evaluation logic: moneyline, spread, totals, and CLV."""

from dataclasses import dataclass
from typing import Literal, Optional

from espn_client import GameResult
from odds_client import ClosingLine
from parsers import BetRequest


@dataclass(frozen=True)
class BetResult:
    """Evaluated bet result."""

    bet_request: BetRequest
    game_result: GameResult
    outcome: Literal["win", "loss", "push", "pending"]
    bet_type_display: str
    user_line_display: str
    result_detail: str
    closing_line: Optional[ClosingLine] = None
    clv_display: Optional[str] = None
    clv_value: Optional[float] = None


def _get_opponent_line(
    closing_line: ClosingLine, team: str, opponent: str
) -> Optional[float]:
    """Get the spread line for the specified team from closing line data."""
    team_lower = team.lower()
    home_lower = closing_line.home_team.lower()
    away_lower = closing_line.away_team.lower()

    if team_lower in home_lower:
        return closing_line.spread_home
    elif team_lower in away_lower:
        return closing_line.spread_away
    # Fallback: try opponent matching
    if opponent.lower() in home_lower:
        # Team is away
        return closing_line.spread_away
    elif opponent.lower() in away_lower:
        # Team is home
        return closing_line.spread_home
    return None


def _get_team_moneyline(
    closing_line: ClosingLine, team: str, opponent: str
) -> Optional[int]:
    """Get the moneyline for the specified team from closing line data."""
    team_lower = team.lower()
    home_lower = closing_line.home_team.lower()
    away_lower = closing_line.away_team.lower()

    if team_lower in home_lower:
        return closing_line.home_moneyline
    elif team_lower in away_lower:
        return closing_line.away_moneyline
    if opponent.lower() in home_lower:
        return closing_line.away_moneyline
    elif opponent.lower() in away_lower:
        return closing_line.home_moneyline
    return None


def _calculate_clv_spread(
    user_line: float, closing_line: Optional[float]
) -> tuple[Optional[float], Optional[str]]:
    """Calculate CLV for a spread bet.

    Positive CLV = you got a better line than the market close.
    """
    if closing_line is None:
        return None, None

    # CLV = closing_line - user_line
    # Example: user took -5.5, closed -7.  CLV = -7 - (-5.5) = -1.5 (bad)
    # Example: user took +3, closed +1.5.  CLV = 1.5 - 3 = -1.5 (bad)
    # Example: user took +3, closed +4.5.  CLV = 4.5 - 3 = +1.5 (good)
    value = round(closing_line - user_line, 2)
    if value > 0:
        display = f"+{value} ✓ (beat the close)"
    elif value < 0:
        display = f"{value} ✗ (worse than close)"
    else:
        display = "0.0 (pinned the close)"
    return value, display


def _calculate_clv_total(
    user_line: float, closing_line: Optional[float], side: str
) -> tuple[Optional[float], Optional[str]]:
    """Calculate CLV for a total bet."""
    if closing_line is None:
        return None, None

    # For overs: lower closing total = better for user
    # For unders: higher closing total = better for user
    if side == "over":
        value = round(closing_line - user_line, 2)
    else:
        value = round(user_line - closing_line, 2)

    if value > 0:
        display = f"+{value} ✓ (beat the close)"
    elif value < 0:
        display = f"{value} ✗ (worse than close)"
    else:
        display = "0.0 (pinned the close)"
    return value, display


def evaluate_bet(
    bet: BetRequest,
    game: GameResult,
    closing_line: Optional[ClosingLine] = None,
) -> BetResult:
    """Evaluate a bet against a game result and optional closing line."""

    if not game.completed:
        return BetResult(
            bet_request=bet,
            game_result=game,
            outcome="pending",
            bet_type_display=bet.bet_type.upper(),
            user_line_display=_format_user_line(bet),
            result_detail="Game is still in progress",
            closing_line=closing_line,
        )

    if bet.bet_type == "moneyline":
        outcome = "win" if game.winner else "loss"
        detail = f"{'Won' if game.winner else 'Lost'} outright"
        clv_val, clv_disp = None, None
        if closing_line:
            clv_val, clv_disp = _calculate_clv_spread(
                0.0 if game.winner else 1.0,  # placeholder — moneyline CLV needs implied prob
                None,
            )
            # Moneyline CLV is complex (requires implied probability conversion).
            # For now we skip detailed ML CLV and note it if spread CLV exists.
            clv_val, clv_disp = None, None

    elif bet.bet_type == "spread":
        if bet.line is None:
            outcome = "pending"
            detail = "Spread line missing"
        else:
            margin = game.team_score - game.opponent_score
            result_with_line = margin + bet.line
            if result_with_line > 0:
                outcome = "win"
                detail = f"Covered by {abs(result_with_line):.1f}"
            elif result_with_line < 0:
                outcome = "loss"
                detail = f"Missed by {abs(result_with_line):.1f}"
            else:
                outcome = "push"
                detail = "Pushed (landed exactly on the number)"

        clv_val, clv_disp = None, None
        if closing_line and bet.line is not None:
            cl = _get_opponent_line(closing_line, bet.team, game.opponent)
            clv_val, clv_disp = _calculate_clv_spread(bet.line, cl)

    elif bet.bet_type == "total":
        if bet.line is None or bet.total_side is None:
            outcome = "pending"
            detail = "Total line or side missing"
        else:
            total = game.total
            if total > bet.line:
                outcome = "win" if bet.total_side == "over" else "loss"
                detail = f"Total went OVER {bet.line} ({total})"
            elif total < bet.line:
                outcome = "win" if bet.total_side == "under" else "loss"
                detail = f"Total went UNDER {bet.line} ({total})"
            else:
                outcome = "push"
                detail = f"Pushed exactly on {bet.line} ({total})"

        clv_val, clv_disp = None, None
        if closing_line and bet.line is not None and bet.total_side is not None:
            # Use over total as the reference line
            cl = closing_line.total_over or closing_line.total_under
            clv_val, clv_disp = _calculate_clv_total(bet.line, cl, bet.total_side)

    else:
        outcome = "pending"
        detail = "Unknown bet type"
        clv_val, clv_disp = None, None

    return BetResult(
        bet_request=bet,
        game_result=game,
        outcome=outcome,
        bet_type_display=bet.bet_type.upper(),
        user_line_display=_format_user_line(bet),
        result_detail=detail,
        closing_line=closing_line,
        clv_display=clv_disp,
        clv_value=clv_val,
    )


def _format_user_line(bet: BetRequest) -> str:
    """Format the user's bet line for display."""
    if bet.bet_type == "moneyline":
        return "ML"
    if bet.bet_type == "spread" and bet.line is not None:
        sign = "" if bet.line < 0 else "+"
        return f"{sign}{bet.line}"
    if bet.bet_type == "total" and bet.line is not None and bet.total_side:
        return f"{bet.total_side.upper()} {bet.line}"
    return "?"
