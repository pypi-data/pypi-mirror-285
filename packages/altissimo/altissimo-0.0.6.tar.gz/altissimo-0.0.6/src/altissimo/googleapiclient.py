# -*- coding: utf-8 -*-
"""GoogleAPIClient class file."""


class GoogleAPIClient:
    """GoogleAPIClient service class."""

    def get_list_items(self, method, request, name):
        """Return a list of items from a GoogleAPIClient list/list_next cycle."""
        items = []
        while request is not None:
            response = request.execute()
            items += response.get(name, [])
            request = method.list_next(request, response)
        return items

    def get_list_items_iterator(self, method, request, name):
        """Yeild items from a GoogleAPIClient list/list_next cycle."""
        while request is not None:
            response = request.execute()
            items = response.get(name, [])
            for item in items:
                yield item
            request = method.list_next(request, response)
