from typing import List, Callable, Coroutine, TYPE_CHECKING

if TYPE_CHECKING:
    from game import Game

# Command handler function signature
# We use 'Any' for Game to avoid circular imports at runtime if not careful, 
# but TYPE_CHECKING helps for static analysis.
CommandHandler = Callable[['Game', List[str]], Coroutine[None, None, str]]
