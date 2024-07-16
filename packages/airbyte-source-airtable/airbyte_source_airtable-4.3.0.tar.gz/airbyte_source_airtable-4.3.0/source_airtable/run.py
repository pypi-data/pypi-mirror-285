#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_airtable import SourceAirtable


def run():
    source = SourceAirtable()
    launch(source, sys.argv[1:])
