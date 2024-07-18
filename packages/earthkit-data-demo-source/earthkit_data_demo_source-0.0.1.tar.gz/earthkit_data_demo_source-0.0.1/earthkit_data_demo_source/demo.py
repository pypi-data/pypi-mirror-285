# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import pandas as pd
from earthkit.data import Source
from sqlalchemy import create_engine


class DemoSource(Source):
    def __init__(self, database, query, **kwargs):
        self.database = database
        self.query = query
        self.kwargs = kwargs

    def to_pandas(self, **kwargs):
        engine = create_engine(self.database)

        options = {}
        options.update(self.kwargs)
        options.update(kwargs)

        with engine.connect() as connection:
            return pd.read_sql(self.query, connection, **options)


source = DemoSource
