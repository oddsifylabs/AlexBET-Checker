"""Bet evaluation logic: moneyline, spread, totals, and CLV across books."""

from dataclasses import dataclass
from typing import Literal, Optional

from espn_client import GameResult
from models import MultiBookLines
from parsers import BetRequest


@dataclass(frozen=True)
class BookCLV:
    """CLV result for a single bookmaker."""

    book_key: str
    book_name: str
    closing_line: Optional[float]
    closing_line_display: Optional[str]
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


def _american_to_implied(odds: int) -> float:
    """Convert American odds to implied probability (0.0 – 1.0)."""
    if odds > 0:
        return 100 / (odds + 100)
    return abs(odds) / (abs(odds) + 100)


def _format_american(odds: int) -> str:
    """Format American odds with + sign for positive."""
    return f"+{odds}" if odds > 0 else str(odds)


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


def _get_team_moneyline(
    multi_book: MultiBookLines, book_key: str, team: str, opponent: str
) -> Optional[int]:
    """Get the moneyline for the specified team from a specific book."""
    book = multi_book.books.get(book_key)
    if not book:
        return None

    team_lower = team.lower()
    home_lower = multi_book.home_team.lower()
    away_lower = multi_book.away_team.lower()

    if team_lower in home_lower:
        return book.home_moneyline
    elif team_lower in away_lower:
        return book.away_moneyline
    if opponent.lower() in home_lower:
        return book.away_moneyline
    elif opponent.lower() in away_lower:
        return book.home_moneyline
    return None


def _clv_display(value: Optional[float], suffix: str = "") -> Optional[str]:
    """Format a CLV value with emoji."""
    if value is None:
        return None
    if value > 0:
        return f"+{value}{suffix} ✓"
    elif value < 0:
        return f"{value}{suffix} ✗"
    return f"0.0{suffix} →"


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
            closing_disp = None

            if bet.bet_type == "spread" and bet.line is not None:
                closing = _get_team_spread(
                    multi_book_lines, book_key, bet.team, game.opponent
                )
                if closing is not None:
                    # CLV = user_line - closing_line
                    clv_val = round(bet.line - closing, 2)
                    closing_disp = f"{closing:+.1f}"

            elif bet.bet_type == "total" and bet.line is not None and bet.total_side:
                closing = _get_team_total(multi_book_lines, book_key)
                if closing is not None:
                    if bet.total_side == "over":
                        clv_val = round(closing - bet.line, 2)
                    else:
                        clv_val = round(bet.line - closing, 2)
                    closing_disp = f"O/U {closing}"

            elif bet.bet_type == "moneyline" and bet.ml_odds is not None:
                closing = _get_team_moneyline(
                    multi_book_lines, book_key, bet.team, game.opponent
                )
                if closing is not None:
                    user_impl = _american_to_implied(bet.ml_odds)
                    close_impl = _american_to_implied(closing)
                    # CLV = closing_implied - user_implied (in percentage points)
                    clv_val = round((close_impl - user_impl) * 100, 2)
                    closing_disp = _format_american(closing)

            if clv_val is not None:
                clv_values.append(clv_val)
                clv_disp = _clv_display(
                    clv_val, suffix="%" if bet.bet_type == "moneyline" else ""
                )

            book_clvs.append(
                BookCLV(
                    book_key=book_key,
                    book_name=book_line.bookmaker_name,
                    closing_line=closing,
                    closing_line_display=closing_disp,
                    clv_value=clv_val,
                    clv_display=clv_disp,
                )
            )

    avg_clv = None
    avg_disp = None
    if clv_values:
        avg_clv = round(sum(clv_values) / len(clv_values), 2)
        suffix = "%" if bet.bet_type == "moneyline" else ""
        if avg_clv > 0:
            avg_disp = f"+{avg_clv}{suffix} ✓ (beat the close)"
        elif avg_clv < 0:
            avg_disp = f"{avg_clv}{suffix} ✗ (worse than close)"
        else:
            avg_disp = f"0.0{suffix} → (pinned the close)"

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
        if bet.ml_odds is not None:
            return _format_american(bet.ml_odds)
        return "ML"
    if bet.bet_type == "spread" and bet.line is not None:
        return f"{bet.line:+.1f}".replace(".0", "")
    if bet.bet_type == "total" and bet.line is not None and bet.total_side:
        return f"{bet.total_side.upper()} {bet.line}"
    return "?"
