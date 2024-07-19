"""Altissimo Tools moduule."""


def chunks(items, n):
    """Yield successive chunks of size n from list items."""
    for i in range(0, len(items), n):
        yield items[i:i + n]


def list_to_dict(items, key="id"):
    """Convert a list of dicts to a dict of dicts by key."""
    results = {}
    for item in items:
        k = item.get(key)
        if k is None:
            continue  # Skip items with null key
        if k in results:
            continue  # Skip items with duplicate key
        results[k] = item
    return results
