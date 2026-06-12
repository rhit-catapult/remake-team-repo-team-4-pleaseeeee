class Upgrade:
    """Represents one upgrade in a clicker game.

    Each upgrade has:
    - a name
    - a base cost
    - a description
    - a multiplier that makes later levels more expensive
    - an effect value that can be used by your game logic
    """

    def __init__(self, name, base_cost, description="", multiplier=1.15, effect=1):
        self.name = name
        self.base_cost = base_cost
        self.description = description
        self.multiplier = multiplier
        self.effect = effect

    def get_cost(self, level):
        """Return the cost for a given upgrade level."""
        return int(self.base_cost * (self.multiplier ** level))


class UpgradeManager:
    """Keeps track of all upgrades and their current levels."""

    def __init__(self):
        self.upgrades = {}
        self.levels = {}

    def add_upgrade(self, upgrade):
        """Register an upgrade so it can be bought later."""
        self.upgrades[upgrade.name] = upgrade
        self.levels[upgrade.name] = 0

    def buy(self, name, currency):
        """Try to buy an upgrade if the player has enough currency."""
        if name not in self.upgrades:
            raise KeyError(f"Unknown upgrade: {name}")

        upgrade = self.upgrades[name]
        level = self.levels[name]
        cost = upgrade.get_cost(level)

        if currency < cost:
            return False, cost, level, self.get_status(name)

        self.levels[name] = level + 1
        return True, cost, self.levels[name], self.get_status(name)

    def get_status(self, name):
        """Return the current status of one upgrade."""
        upgrade = self.upgrades[name]
        level = self.levels[name]
        return {
            "name": upgrade.name,
            "level": level,
            "cost": upgrade.get_cost(level),
            "description": upgrade.description,
            "effect": upgrade.effect,
        }

    def get_all_status(self):
        """Return the status of every upgrade."""
        return [self.get_status(name) for name in self.upgrades]

    def get_total_effect(self, name):
        """Return the current total effect of one upgrade type."""
        upgrade = self.upgrades[name]
        return self.levels[name] * upgrade.effect


def demo():
    """Show a tiny example of how the upgrade system could be used."""
    manager = UpgradeManager()
    manager.add_upgrade(Upgrade("Click Power", 10, "Adds 1 point per click", effect=1))
    manager.add_upgrade(Upgrade("Auto Clicker", 50, "Adds 1 point per second", effect=1))

    currency = 60
    print("Starting currency:", currency)

    bought, cost, level, status = manager.buy("Click Power", currency)
    if bought:
        currency -= cost
        print(f"Bought {status['name']} for {cost} points.")

    bought, cost, level, status = manager.buy("Auto Clicker", currency)
    if bought:
        currency -= cost
        print(f"Bought {status['name']} for {cost} points.")

    print("Remaining currency:", currency)
    print("Upgrade summary:", manager.get_all_status())


if __name__ == "__main__":
    demo()