"""WorkItems module to get the work items from Robocorp WorkItems library or from local file."""
try:
    from RPA.Robocorp.WorkItems import WorkItems

    work_items = WorkItems()
    work_items.get_input_work_item()
    work_item = work_items.get_work_item_variables()

    METADATA = work_item.get("metadata", dict())
    VARIABLES = work_item.get("variables", dict())
except (ImportError, KeyError):
    VARIABLES = {}
    METADATA = {}
