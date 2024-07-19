import json
from functools import reduce
from types import ModuleType
from typing import Any, Callable, Iterable, Optional, Tuple, Union
from uuid import UUID

from sqlalchemy import Table, func, union
from sqlalchemy.sql import select

from json_merge_tree.merged import merge

Ancestors = Iterable[Tuple[UUID, Optional[Callable]]]


def merge_tree(
        db: Any,
        table: Table,
        id: UUID,
        type: str,
        json_field: str,
        parents: ModuleType,
        slugs: Optional[Iterable[str]] = None,
        filters: Optional[tuple] = None,
        buff_query: Optional[Callable] = None,
        debug: Optional[str] = None
) -> dict:
    """Take a resource ID and return the merged json object for that page.

    The merged json object is any json saved for that resource, merged into any resources saved
    for its ancestor resources, all the way up the hierarchy.
    """
    # Get a generator that will yield the IDs of a resource's immediate ancestors
    parent_getter = getattr(parents, type, None)

    # Get a generator that will yield the json objects of all the requested resource's ancestors
    json_objects = get_json_objects(
        db, table, id, json_field, parent_getter, slugs, filters, buff_query, debug
    )

    # Merge those json objects and return the result
    return reduce(merge, json_objects, {})


def get_json_objects(
    db: Any,
    table: Table,
    resource_id: UUID,
    json_field: str,
    parent_getter: Optional[Callable[[UUID], Ancestors]],
    slugs: Optional[Iterable[str]] = None,
    filters: Optional[tuple] = None,
    buff_query: Optional[Callable] = None,
    debug: Optional[str] = None
) -> Iterable[dict]:
    """Take a resource ID and return all its ancestors' resources.

     Recurses up the hierarchy using "parent getters" to get the IDs of each resource's immediate
     ancestors, then on the way back down yields any resources defined for those resources, starting
     at the top.
    """
    c = table.columns
    query = select(table)
    # These filters will be used to get the resource record here, and also the slug records later
    query_filters: tuple = (c.resource_id == resource_id,)

    # Hook for altering query and query_filters before executing
    if callable(buff_query):
        query, query_filters = buff_query(c, query, query_filters)

    if filters is not None:
        query_filters = query_filters + filters
    query = query.where(*query_filters)
    record = get_resource_record(db, query.where(c.slug.is_(None)).order_by(c.created_at))

    if parent_getter is not None and getattr(record, 'inherits', True):
        # If this resource isn't the top of the hierarchy, recurse upwards...
        for parent_id, grandparent_getter in parent_getter(resource_id):
            # ...with the parent's ID and a generator of that resource's immediate ancestors
            yield from get_json_objects(db, table, parent_id, json_field, grandparent_getter, slugs,
                                        filters, buff_query, debug)

    # As the recursion unwinds, yield any json objects for each resource:
    # its own, and any slugs under it
    if record:
        yield record_json(record, json_field, debug)
    if slugs:
        for slug_record in get_slug_records(db, query, c, slugs, buff_query):
            yield record_json(slug_record, json_field, debug)


def get_resource_record(db, query):
    return db.execute(query).first()


def get_slug_records(db, query, c, slugs, buff_query):
    slug_query = None
    if callable(buff_query):
        queries = ()
        for slug in slugs:
            queries = queries + (query.filter(c.slug == slug).limit(1),)
        union_aliased = union(*queries).alias()
        order = func.array_position(slugs, union_aliased.c.slug)
        slug_query = select(union_aliased).order_by(order)
    else:
        order = func.array_position(slugs, c.slug)
        slug_query = query.where(c.slug.in_(slugs)).order_by(order)
    return db.execute(slug_query)


def record_json(
        record: Any,
        json_field: str,
        debug: Optional[str] = None
) -> dict:
    json_data = getattr(record, json_field)

    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    if debug is not None:
        add_debug_info(json_data, record, json_field, debug)

    return json_data


def add_debug_info(d, record, json_field, debug):
    new_items = []
    for k, v in d.items():
        if isinstance(v, dict):
            add_debug_info(v, record, json_field, debug)
        else:
            new_items.append(debug_info(k, v, record, json_field, debug))
    d.update(new_items)


def debug_info(
        k: str,
        v: Any,
        record: Any,
        json_field: str,
        debug: str,
) -> tuple[str, Union[dict, list]]:
    if debug == 'history':
        return k + '-history', [from_dict(record, json_field) | {'value': v}]
    if debug == 'annotate':
        return k + '-from', from_dict(record, json_field)
    return k, from_dict(record, json_field)


def from_dict(record: Any, json_field: str) -> dict:
    return dict(from_pairs(record, json_field))


def from_pairs(record: Any, json_field: str) -> Iterable[tuple[str, str]]:
    yield 'id', record.resource_id
    yield 'type', record.resource_type,
    yield json_field + '_id', record.id
    if record.slug:
        yield 'slug', record.slug
