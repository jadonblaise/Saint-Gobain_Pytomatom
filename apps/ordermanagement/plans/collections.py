def extract_key(plan: list[dict], key: str, stringify: bool = False) -> dict:
    """
    Build "level-two" collection sorted by given `column` value
    'restructuring the plan-dict'

    - broken entries (not compatible with schema) will be lost (removed)

    - this method does not touch given `plan` objects

    plan:
        whole plan in one collection
    key:
        fetch values in dicts to define new collection keys in second level
    stringify:
        keys to select collections as string

    ```
    input_plan = [  # level one
        {"key": "A", "bar": "b", "baz": "c"},
        {"foo": "a", "key": "B", "fizz": "e"},
    ]

    expected = {  # level two
        "A": [
            {"key": "A", "bar": "b", "baz": "c"},
        ],
        "B": [
            {"foo": "a", "key": "B", "fizz": "e"},
        ],
    }
    ```
    """
    out: dict = {}
    for entry in plan:
        if entry.get(key, None) is not None:
            formated_key = str(entry[key]) if stringify else entry[key]
            # out[formated_key] = out.get(formated_key, []).append(entry)
            if formated_key in out.keys():
                out[formated_key].append(entry)
            else:
                out[formated_key] = [entry]
        # TODO: else - logging of useless entries (or throw error)
    return out


def sort_flat(
    collection: list,
    key: str,
    descending: bool = False,
) -> list:
    """
    Sort collections in 'second level' by given key.

    plan: 'second level' collection
    key: sort collections by this key
    descending: True to reverse sorting
    """
    # TBD: row = copy(row)
    collection.sort(
        # hint: cast value to string to avoid error (sorting with different types not possible)
        # TBD: order of sort - key type transformation is wrong
        # BUG: this let to errors pass silently before, we never want that, usage with letter "■" was a bug
        # key=lambda row: row.get(key, float("inf")),
        # cast value to string to avoid error
        # (sorting with different types not possible)
        key=lambda row: str(row.get(key, "")),
        reverse=descending,
    )
    # TODO: build underlying test to guarantee right behavior
    return collection


def sort_by(
    plan: dict[str, list],
    key: str,
    exclude: list[str] | None = None,
    descending: bool = False,
) -> dict[str, list[dict]]:
    """
    Sort collections in 'second level' by given key.

    plan:
        'second level' collection
    key:
        sort collections in 'second level' by this key
    exclude:
        exclude collection from sorting
    descending:
        True for reversed sorting
    """
    exclude = exclude if exclude is not None else []
    for collection_key, value in plan.items():
        if collection_key not in exclude:
            value.sort(
                # hint: cast value to string to avoid error (sorting with different types not possible)
                key=lambda row: str(row.get(key, float("inf"))),
                reverse=descending,
            )
            # TODO: build underlying test to guarantee right behavior
    return plan


def deep_extract(
    plan: dict[str, list[dict]],
    key: str,
    stringify: bool = True,
) -> dict[str, dict[str, list[dict]]]:
    """
    Build a more complex collection with higher abstaction level.

    plan:
        plan as 'second level' collection
    key:
        fetch values in dicts of 'second level' to define new collection keys in 'third level'
    stringify:
        keys to select collections as string (default is True)

    ```
    plan_input_level_two = {
        "A": [
            {"bar": "b", "baz": "c", "key": "E"},
            {"foo": "a", "fizz": "e", "key": "F"},
        ],
        "B": [
            {"bar": "b", "baz": "c", "key": "E"},
            {"foo": "a", "fizz": "e", "key": "F"},
        ],
    }

    expected = {
        "A" : {
            "E": [
                {"bar": "b", "baz": "c", "key": "E"},
            ],
            "F": [
                {"foo": "a", "fizz": "e", "key": "F"},
            ]
        },
        "B" : {
            "E": [
                {"bar": "b", "baz": "c", "key": "E"},
            ],
            "F": [
                {"foo": "a", "fizz": "e", "key": "F"},
            ]
        }
    }
    ```
    """
    new_plan = dict()
    for new_key, collection_of_plan in plan.items():
        new_key = str(new_key) if stringify else new_key
        new_plan[new_key] = extract_key(
            plan=collection_of_plan,
            key=key,
            stringify=stringify,
        )
    return new_plan


def sort_by_deep(
    plan: dict[str, dict[str, list]],
    key: str,
    exclude: list | None = None,
    descending: bool = False,
) -> dict[str, dict[str, list]]:
    """
    Sort collections in 'third level' by given key.

    plan:
        'third level' collection
    key:
        sort collections in 'third level' by this key
    exclude:
        exclude collection from sorting
    descending:
        True for reversed sorting
    """
    for second_level_entry in plan.values():
        second_level_entry = sort_by(
            plan=second_level_entry,
            key=key,
            exclude=exclude,
            descending=descending,
        )
    return plan
