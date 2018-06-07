import os
import pandas as pd
from IPython.core.display import display, HTML
from recordsearch_tools.client import RSSeriesClient
import plotly.offline as py
import plotly.graph_objs as go
from textblob import TextBlob
import nltk
stopwords = nltk.corpus.stopwords.words('english')
py.init_notebook_mode()

def make_summary(series, df, include_titles=True):
    # We're going to assemble some summary data about the series in a 'summary' dictionary
    # Let's create the dictionary 
    summary = {'series': series}
    if include_titles:
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
    start = df['start_date'].min()
    try:
        summary['date_from'] = start.year
    except AttributeError:
        summary['date_from'] = None
    # Get the latest end date
    end = df['end_date'].max()
    try:
        summary['date_to'] = end.year
    except AttributeError:
        summary['date_to'] = None
    return summary

def display_summary(series, df):
    summary = make_summary(series, df)
    display(HTML('<h1>National Archives of Australia: Series {}</h1>'.format(series)))
    display(HTML('<h3>{}</h3>'.format(summary['title'])))
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
    table += '<ul><li><b><a href="https://github.com/wragge/ozglam-workbench/blob/master/data/RecordSearch/{}.csv">Download item data (CSV format)</a></b></li>'.format(series.replace('/', '-'))
    table += '<li><b><a href="http://www.naa.gov.au/cgi-bin/Search?O=S&Number={}">View details on RecordSearch</a></b></li></ul>'.format(series)
    
    display(HTML(table))
    

def make_df_all(series_list):
    # Create a list to store the summaries
    summaries = []

    # Loop through the list of series in this repo
    for series in series_list:
        # Open the CSV of each series harvest as a data frame
        df = pd.read_csv('../data/RecordSearch/{}.csv'.format(series.replace('/', '-')), parse_dates=['start_date', 'end_date'])
        # Extract a summary of each series and add it to the list of summaries
        summaries.append(make_summary(series, df, include_titles=False))

    # Convert the list of summaries into a DataFrame for easy manipulation
    df = pd.DataFrame(summaries)

    # Flatten the access count dictionaries and fill blanks with zero
    df = pd.concat([df, pd.DataFrame((d for idx, d in df['access_counts'].iteritems()))], axis=1).fillna(0)

    # Change access counts from floats to integers
    df[['Closed', 'Not yet examined', 'Open with exception', 'Open']] = df[['Closed', 'Not yet examined', 'Open with exception', 'Open']].astype(int)

    # Delete the old 'access_counts' column
    del df['access_counts']

    # For convenience acronymise 'Not yet examined' and 'Open with exception'
    df.rename({'Not yet examined': 'NYE', 'Open with exception': 'OWE'}, axis=1, inplace=True)
    return df


def make_summary_all(df):
    summary = {}
    summary['total_items'] = df['total_items'].sum()
    summary['date_from'] = int(df['date_from'].min())
    summary['date_to'] = int(df['date_to'].max())
    access_status = {}
    for status in ['Open', 'OWE', 'NYE', 'Closed']:
        status_total = df[status].sum()
        access_status[status] = status_total
    summary['access_counts'] = access_status
    summary['digitised_files'] = df['digitised_files'].sum()
    summary['digitised_pages'] = df['digitised_pages'].sum()
    return summary

    
def display_summary_all(df):
    summary = make_summary_all(df)
    display(HTML('<h2>Aggregated totals</h2>'))
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
    
    
def display_series_all(df):
    # Get the columns into the order we want
    df = df[['series', 'total_items', 'date_from', 'date_to', 'Open', 'OWE', 'NYE', 'Closed', 'digitised_files', 'digitised_pages']].copy()

    # Calculate and add a percentage open column
    df['% open'] = df['Open'] / df['total_items']

    # Calculate and add a percentage digitised column
    df['% digitised'] = df['digitised_files'] / df['total_items']

    # Add a link to the series name
    df['series'] = df['series'].apply(lambda x: '<a href="{}-summary.ipynb">{}</a>'.format(x.replace('/', '-'), x))

    # Style the output
    table = (df.style
         .set_properties(**{'font-size': '120%'})
         .set_properties(subset=['series'], **{'text-align': 'left', 'font-weight': 'bold'})
         .format('{:,}', ['total_items', 'Open', 'OWE', 'NYE', 'Closed', 'digitised_files', 'digitised_pages'])
         .format('{:.2%}', ['% open', '% digitised'])
         # Hide the index
         .set_table_styles([dict(selector="th", props=[("font-size", "120%"), ("text-align", "center")]),
                           dict(selector='.row_heading, .blank', props=[('display', 'none')])])
         .background_gradient(cmap='Greens', subset=['% open', '% digitised'], high=0.5)
    )
    return table
    

def make_year_trace(df, digitised=True):
    all_years = []
    for row in df.loc[df['digitised_status'] == digitised].itertuples(index=False):
        try:
            years = pd.date_range(start=row.start_date, end=row.end_date, freq='AS').year.to_series()
        except ValueError:
            # No start date
            pass
        else:
            all_years.append(years)
    year_counts = pd.concat(all_years).value_counts()
    # Put the resulting series in a dataframe so it looks pretty.
    year_totals = pd.DataFrame(year_counts)
    # Sort results by year
    year_totals.sort_index(inplace=True)
    return year_totals
    
    
def plot_dates(df):
    # This is a bit tricky.
    # For each item we want to find the years that it has content from -- ie start_year <= year <= end_year.
    # Then we want to put all the years from all the items together and look at their frequency
    # At the moment I'm checking the start of the year -- so I think an item that has a start date after 1 Jan
    # won't register as having content from that year. Needs some adjustment...
    df['end_date'] = df[['end_date']].apply(lambda x: x.fillna(value=df['start_date']))
    plotly_data = []
    if len(df.loc[df['digitised_status'] == True]) > 0:
        years_dg = make_year_trace(df, digitised=True)
        plotly_data.append(
            go.Bar(
                x=years_dg.index.values, # The years are the index
                y=years_dg[0],
                name='Digitised'
            )   
        )
    if len(df.loc[df['digitised_status'] == False]) > 0:
        years_nd = make_year_trace(df, digitised=False)
        # Let's graph the frequency of content years
        plotly_data.append(
            go.Bar(
                x=years_nd.index.values, # The years are the index
                y=years_nd[0],
                name='Not digitised'
            )
        )

    # Add some labels
    layout = go.Layout(
        title='Content dates',
        xaxis=dict(
            title='Year'
        ),
        yaxis=dict(
            title='Number of items'
        ),
        barmode='stack'
    )

    # Create a chart 
    fig = go.Figure(data=plotly_data, layout=layout)
    return fig

def plot_all_dates(series_list):
    sdfs = []
    for series in series_list:
        sdf = pd.read_csv('../data/RecordSearch/{}.csv'.format(series.replace('/', '-')), parse_dates=['start_date', 'end_date'])
        sdfs.append(sdf)
    combined_df = pd.concat(sdfs)
    fig = plot_dates(combined_df)
    return fig


def plot_all_access_statuses(df):
    statuses = ['Open', 'OWE', 'NYE', 'Closed', 'Withheld pending agency advice']
    totals = []
    for status in statuses:
        totals.append(df[status].sum())
    # Create a pie chart
    plot_data = [go.Pie(
                labels=statuses,
                values=totals
        )]
    return plot_data


def get_word_counts(text):
    blob = TextBlob(text)
    words = [[word, count] for word, count in blob.lower().word_counts.items() if word not in stopwords]
    word_counts = pd.DataFrame(words).rename({0: 'word', 1: 'count'}, axis=1).sort_values(by='count', ascending=False)
    return word_counts


def display_word_counts(text):
    word_counts = get_word_counts(text)
    return word_counts[:25].style.format({'count': '{:,}'}).bar(subset=['count'], color='#d65f5f').set_properties(subset=['count'], **{'width': '300px'})

    
def get_ngram_counts(text, size):
    blob = TextBlob(text)
    # Extract n-grams as WordLists, then convert to a list of strings
    ngrams = [' '.join(ngram).lower() for ngram in blob.lower().ngrams(size)]
    # Convert to dataframe then count values and rename columns
    ngram_counts = pd.DataFrame(ngrams)[0].value_counts().rename_axis('ngram').reset_index(name='count')
    return ngram_counts
    

def display_top_ngrams(text, size):
    ngram_counts = get_ngram_counts(text, 2)
    # Display top 25 results as a bar chart
    return display(ngram_counts[:25].style.format({'count': '{:,}'}).bar(subset=['count'], color='#d65f5f').set_properties(subset=['count'], **{'width': '300px'}))