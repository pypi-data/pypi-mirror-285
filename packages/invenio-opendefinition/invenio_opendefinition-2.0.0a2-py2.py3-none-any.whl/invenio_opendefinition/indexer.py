# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Record modification prior to indexing."""

from __future__ import absolute_import, print_function


def indexer_receiver(sender, json=None, record=None, index=None, **dummy_kwargs):
    """Connect to before_record_index signal to transform record for ES."""
    if index.startswith("licenses-"):
        json["suggest"] = {"input": [json["id"], json["title"]]}
