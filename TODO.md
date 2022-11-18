# TODOs
- Add tests!
- Add examples + documentation.
- Add auth.
- Add support for table header offsets + sheet select, especially for xlsx
  spreadsheet input data files.
  Use frictionless functionality for this e.g. like

      resource = frictionless.describe("rki-covid-fallzahlen.xlsx",
      dialect=ExcelDialect(sheet="LK_7-Tage-Inzidenz-aktualisiert"),
      layout=frictionless.Layout(header_rows=[3], skip_fields=[64]))

- Use PATCH instead of PUT for update endpoints.
- Return 201 Created status instead of 200 for succesful POST.
- Add custom numeric handling i.e. use decimal instead of float, store exact
  values in the database instead of floats, ...
- Fix examples for number values (should be numbers, not strings) - apply
  frictionless cast functionality for this?
- Maybe restructure commands (e.g. init, load, run) so that the resulting
  app.yaml and <table>.yaml can be modified *before* adding primary key column
  and loading the database?
