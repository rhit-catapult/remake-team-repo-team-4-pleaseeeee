import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("upgrade_module", ROOT / "upgrade_module.py")
upgrade_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(upgrade_module)


def test_manager_supports_multiple_upgrades():
    manager = upgrade_module.UpgradeManager()
    manager.add_upgrade(upgrade_module.Upgrade("Click Power", 10, "Adds 1 point per click", effect=1))
    manager.add_upgrade(upgrade_module.Upgrade("Auto Clicker", 50, "Adds 1 point per second", effect=1))
    manager.add_upgrade(upgrade_module.Upgrade("Lucky Charm", 80, "Adds 2 points per click", effect=2))

    assert len(manager.get_all_status()) == 3
    assert manager.get_status("Lucky Charm")["level"] == 0
    assert manager.get_total_effect("Lucky Charm") == 0


def test_upgrades_split_into_pages():
    upgrades = [
        upgrade_module.Upgrade("A", 10, "First", effect=1),
        upgrade_module.Upgrade("B", 20, "Second", effect=1),
        upgrade_module.Upgrade("C", 30, "Third", effect=1),
        upgrade_module.Upgrade("D", 40, "Fourth", effect=1),
        upgrade_module.Upgrade("E", 50, "Fifth", effect=1),
    ]

    pages = upgrade_module.split_upgrades_into_pages(upgrades, page_size=4)

    assert len(pages) == 2
    assert [upgrade.name for upgrade in pages[0]] == ["A", "B", "C", "D"]
    assert [upgrade.name for upgrade in pages[1]] == ["E"]
