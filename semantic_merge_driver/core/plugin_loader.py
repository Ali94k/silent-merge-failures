import importlib
import inspect
import pkgutil
import os
from typing import List, Type
from core.interfaces import MergeStrategy
import strategies

class StrategyLoader:
    def __init__(self, config_enabled_list: List[str] = None):
        self.enabled_strategies = config_enabled_list

    def load_strategies(self) -> List[MergeStrategy]:
        """Dynamically discovers and initializes strategy classes."""
        found_strategies = []
        
        # Walk through the 'strategies' package
        package_path = os.path.dirname(strategies.__file__)
        
        for _, name, _ in pkgutil.walk_packages([package_path], strategies.__name__ + "."):
            try:
                module = importlib.import_module(name)
                # Inspect module for classes implementing MergeStrategy
                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)
                    
                    if (isinstance(attribute, type) and 
                        issubclass(attribute, MergeStrategy) and 
                        attribute is not MergeStrategy):
                        
                        # Instantiate the strategy
                        strategy_instance = attribute()
                        
                        # Filter based on config (if provided)
                        if self.enabled_strategies is None or strategy_instance.name in self.enabled_strategies:
                            found_strategies.append(strategy_instance)
                            
            except Exception as e:
                print(f"Warning: Failed to load module {name}: {e}")

        return found_strategies