"""Strategy corpus package. Module-level singleton for agent use.

    from gridiron.strategy import loader
    content = loader.load("03-waiver-strategy")
"""

from gridiron.strategy.loader import StrategyLoader

loader = StrategyLoader()

__all__ = ["loader", "StrategyLoader"]
