"""Bet evaluation logic: moneyline, spread, totals, and CLV across books."""

from dataclasses import dataclass
from typing import Literal, Optional

from espn_client import GameResult
from odds_client import MultiBookLines
from parsers import BetRequest


@dataclass(frozen=True)
class BookCLV:
    """CLV result for a single bookmaker."""

    book_key: str
    book_name: str
    closing_line: Optional[float]
    clv_value: Optional[float]
    clv_display: Optional[str]


@dataclass(frozen=True)
class BetResult:
    """Evaluated bet result."""

    bet_request: BetRequest
    game_result: GameResult
    outcome: Literal["win", "loss", "push", "pending"]
    bet_type_display: str
    user_line_display: str
    result_detail: str
    multi_book_lines: Optional[MultiBookLines] = None
    book_clvs: list[BookCLV] = None
    avg_clv_value: Optional[float] = None
    avg_clv_display: Optional[str] = None


def _get_team_spread(
    multi_book: MultiBookLines, book_key: str, team: str, opponent: str
) -> Optional[float]:
    """Get the spread line for the specified team from a specific book."""
    book = multi_book.books.get(book_key)
    if not book:
        return None

    team_lower = team.lower()
    home_lower = multi_book.home_team.lower()
    away_lower = multi_book.away_team.lower()

    if team_lower in home_lower:
        return book.spread_home
    elif team_lower in away_lower:
        return book.spread_away
    # Fallback via opponent
    if opponent.lower() in home_lower:
        return book.spread_away
    elif opponent.lower() in away_lower:
        return book.spread_home
    return None


def _get_team_total(
    multi_book: MultiBookLines, book_key: str
) -> Optional[float]:
    """Get the total over line from a specific book."""
    book = multi_book.books.get(book_key)
    if not book:
        return None
    return book.total_over


def _calculate_clv_spread(
    user_line: float, closing_line: Optional[float]
) -> tuple[Optional[float], Optional[str]]:
    """Calculate CLV for a spread bet.

    Positive CLV = you got a better line than the market close.
    """
    if closing_line is None:
        return None, None

    value = round(closing_line - user_line, 2)
    if value > 0:
        display = f"+{value} ✓"
    elif value < 0:
        display = f"{value} ✗"
    else:
        display = "0.0 →"
    return value, display


def _calculate_clv_total(
    user_line: float, closing_line: Optional[float], side: str
) -> tuple[Optional[float], Optional[str]]:
    """Calculate CLV for a total bet."""
    if closing_line is None:
        return None, None

    if side == "over":
        value = round(closing_line - user_line, 2)
    else:
        value = round(user_line - closing_line, 2)

    if value > 0:
        display = f"+{value} ✓"
    elif value < 0:
        display = f"{value} ✗"
    else:
        display = "0.0 →"
    return value, display


def evaluate_bet(
    bet: BetRequest,
    game: GameResult,
    multi_book_lines: Optional[MultiBookLines] = None,
) -> BetResult:
    """Evaluate a bet against a game result and optional multi-book lines."""

    if not game.completed:
        return BetResult(
            bet_request=bet,
            game_result=game,
            outcome="pending",
            bet_type_display=bet.bet_type.upper(),
            user_line_display=_format_user_line(bet),
            result_detail="Game is still in progress",
            multi_book_lines=multi_book_lines,
            book_clvs=[],
        )

    # Determine base outcome
    if bet.bet_type == "moneyline":
        outcome = "win" if game.winner else "loss"
        detail = f"{'Won' if game.winner else 'Lost'} outright"

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
    else:
        outcome = "pending"
        detail = "Unknown bet type"

    # Calculate CLV per bookmaker
    book_clvs: list[BookCLV] = []
    clv_values: list[float] = []

    if multi_book_lines:
        for book_key, book_line in multi_book_lines.books.items():
            clv_val = None
            clv_disp = None
            closing = None

            if bet.bet_type == "spread" and bet.line is not None:
                closing = _get_team_spread(
                    multi_book_lines, book_key, bet.team, game.opponent
                )
                clv_val, clv_disp = _calculate_clv_spread(bet.line, closing)

            elif bet.bet_type == "total" and bet.line is not None and bet.total_side:
                closing = _get_team_total(multi_book_lines, book_key)
                clv_val, clv_disp = _calculate_clv_total(
                    bet.line, closing, bet.total_side
                )

            elif bet.bet_type == "moneyline":
                # Moneyline CLV requires implied probability — skip for now
                closing = None
                clv_val = None
                clv_disp = None

            if clv_val is not None:
                clv_values.append(clv_val)

            book_clvs.append(
                BookCLV(
                    book_key=book_key,
                    book_name=book_line.bookmaker_name,
                    closing_line=closing,
                    clv_value=clv_val,
                    clv_display=clv_disp,
                )
            )

    avg_clv = None
    avg_disp = None
    if clv_values:
        avg_clv = round(sum(clv_values) / len(clv_values), 2)
        if avg_clv > 0:
            avg_disp = f"+{avg_clv} ✓ (beat the close)"
        elif avg_clv < 0:
            avg_disp = f"{avg_clv} ✗ (worse than close)"
        else:
            avg_disp = "0.0 → (pinned the close)"

    return BetResult(
        bet_request=bet,
        game_result=game,
        outcome=outcome,
        bet_type_display=bet.bet_type.upper(),
        user_line_display=_format_user_line(bet),
        result_detail=detail,
        multi_book_lines=multi_book_lines,
        book_clvs=book_clvs,
        avg_clv_value=avg_clv,
        avg_clv_display=avg_disp,
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
