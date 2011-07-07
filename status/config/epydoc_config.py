[epydoc]

name: TorStatus

output: html
target: api/
introspect: no
private: no
exclude: django, manage, settings, tests,
sourcecode: no
# The verbosity should be set at -2 upon release, as this gets rid of
# error messages of the flavor:
# Warning: No information available for status.statusapp.models.Vote's
# base django.db.models.Model
verbosity: -2
