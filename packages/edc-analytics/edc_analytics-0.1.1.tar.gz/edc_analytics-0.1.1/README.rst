|pypi| |downloads|


edc-analytics
-------------

Build analytic tables from EDC data


Read your data into a dataframe, for example an EDC screening table:

.. code-block:: python

    qs_screening = SubjectScreening.objects.all()
    df = read_frame(qs_screening)


Convert all numerics to ``pandas`` numerics:

.. code-block:: python

    cols = [
        "age_in_years",
        "dia_blood_pressure_avg",
        "fbg_value",
        "hba1c_value",
        "ogtt_value",
        "sys_blood_pressure_avg",
    ]
    df[cols] = df[cols].apply(pd.to_numeric)


Pass the dataframe to each ``Table`` class

.. code-block:: python

    gender_tbl = GenderTable(main_df=df)
    age_tbl = AgeTable(main_df=df)
    bp_table = BpTable(main_df=df)


In the ``Table`` instance,

* ``data_df`` is the supporting dataframe
* ``table_df`` is the dataframe to display. The ``table_df`` displays formatted data in the first 5 columns ("Characteristic", "Statistic", "F", "M", "All"). The ``table_df`` has additional columns that contain the statistics used for the statistics displayed in columns ["F", "M", "All"].

From above, ``gender_tbl.table_df`` is just a dataframe and can be combined with other ``table_df`` dataframes using ``pd.concat()`` to make a single ``table_df``.

.. code-block:: python

    table_df = pd.concat(
        [gender_tbl.table_df, age_tbl.table_df, bp_table.table_df]
     )

Show just the first 5 columns:

.. code-block:: python

    table_df.iloc[:, :5]


Like any dataframe, you can export to csv:

.. code-block:: python

    path = "my/path/to/csv/folder/table_df.csv"
    table_df.to_csv(path_or_buf=path, encoding="utf-8", index=0, sep="|")



.. |pypi| image:: https://img.shields.io/pypi/v/edc-analytics.svg
   :target: https://pypi.python.org/pypi/edc-analytics

.. |downloads| image:: https://pepy.tech/badge/edc-analytics
   :target: https://pepy.tech/project/edc-analytics
