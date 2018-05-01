import pandas as pd
from IPython.core.display import display, HTML
from recordsearch_tools.client import RSSeriesClient
import plotly.offline as py
import plotly.graph_objs as go
py.init_notebook_mode()

def make_summary(series, df):
    # We're going to assemble some summary data about the series in a 'summary' dictionary
    # Let's create the dictionary 
    summary = {}
    s = RSSeriesClient()
    series_data = s.get_summary(series)
    summary['title'] = series_data['title']
    summary['total_items'] = df.shape[0]
    # Get the frequency of the different access status categories
    summary['access_counts'] = df['access_status'].value_counts().to_dict()
    # Get the number of files that have been digitised
    summary['digitised_files'] = len(df.loc[df['digitised_status'] == True])
    # Get the number of individual pages that have been digitised
    summary['digitised_pages'] = df['digitised_pages'].sum()
    # Get the earliest start date
    summary['date_from'] = df['start_date'].min().year
    # Get the latest end date
    summary['date_to'] = df['end_date'].max().year
    return summary

def display_summary(series, df):
    summary = make_summary(series, df)
    display(HTML('<h1>NAA Series {}</h1>'.format(series)))
    display(HTML('<h2>{}</h2>'.format(summary['title'])))
    table = '<table class="table" style="text-align: left">'
    table += '<tr><th style="text-align: left">Total items</th><td style="text-align: left">{:,}</td></tr>'.format(summary['total_items'])
    table += '<tr><th style="text-align: left">Access status</th><td></td></tr>'
    for status, number in summary['access_counts'].items():
        table += '<tr><td style="text-align: left">{}</td><td style="text-align: left">{:,} ({:.2%})</td></tr>'.format(status, number, number/summary['total_items'])
    table += '<tr><th style="text-align: left">Number of items digitised</th><td style="text-align: left">{:,} ({:.2%})</td></tr>'.format(summary['digitised_files'], summary['digitised_files']/summary['total_items'])
    table += '<tr><th style="text-align: left">Number of pages digitised</th><td style="text-align: left">{:,}</td></tr>'.format(summary['digitised_pages'])
    table += '<tr><th style="text-align: left">Date of earliest content</th><td style="text-align: left">{}</td></tr>'.format(summary['date_from'])
    table += '<tr><th style="text-align: left">Date of latest content</th><td style="text-align: left">{}</td></tr>'.format(summary['date_to'])
    table += '</table>'
    
    display(HTML(table))
    
def plot_dates(series, df):
    # This is a bit tricky.
    # For each item we want to find the years that it has content from -- ie start_year <= year <= end_year.
    # Then we want to put all the years from all the items together and look at their frequency
    # At the moment I'm checking the start of the year -- so I think an item that has a start date after 1 Jan
    # won't register as having content from that year. Needs some adjustment...
    df['end_date'] = df[['end_date']].apply(lambda x: x.fillna(value=df['start_date']))
    years = pd.concat([pd.date_range(
        start=row.start_date, 
        end=row.end_date, 
        freq='AS').year.to_series() for row in df.itertuples(index=False)]).value_counts()
    # Put the resulting series in a dataframe so it looks pretty.
    year_totals = pd.DataFrame(years)
    # Sort results by year
    year_totals.sort_index(inplace=True)
    # Let's graph the frequency of content years
    plotly_data = [go.Bar(
            x=year_totals.index.values, # The years are the index
            y=year_totals[0]
    )]

    # Add some labels
    layout = go.Layout(
        title='Content dates',
        xaxis=dict(
            title='Year'
        ),
        yaxis=dict(
            title='Number of items'
        )
    )

    # Create a chart 
    fig = go.Figure(data=plotly_data, layout=layout)
    py.iplot(fig, filename='series-dates-bar')