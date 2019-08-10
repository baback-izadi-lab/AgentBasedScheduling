import plotly.figure_factory as ff

df = [dict(Task="Processor-1", Start='2016-01-01 08:00:00', Finish='2016-01-01 08:00:01', Resource='TaskAgent0'),
dict(Task="Processor-1", Start='2016-01-01 08:00:01', Finish='2016-01-01 08:00:04', Resource='TaskAgent1'),
dict(Task="Processor-2", Start='2016-01-01 08:00:01', Finish='2016-01-01 08:00:02', Resource='TaskAgent2'),
dict(Task="Processor-2", Start='2016-01-01 08:00:02', Finish='2016-01-01 08:00:05', Resource='TaskAgent3')
      ]

colors = {'Not Started': 'rgb(220, 0, 0)',
          'Incomplete': (1, 0.9, 0.16),
          'Complete': 'rgb(0, 255, 100)'}

fig = ff.create_gantt(df, show_colorbar=True, index_col='Resource',
                      group_tasks=True)
fig.show()