import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
# app = Dash(assets_folder='./assets')
df = pd.read_csv('./top_250.csv')

## Get decade of release from each movie and create a new column in the dataframe
decades = []
df['year'] = df['year'].astype(int)
for x in df['year']:
    c = x / 100
    y = x - (int(c) * 100)
    d = int(y) / 10
    decades.append(str(x)[:2] + str(int(d)) + '0')
df['decade'] = decades

## Get how many times each decade appear and then order the values
d = df['decade'].value_counts().to_frame().reset_index()
d.rename(columns={'index':'Decade','decade':'Count'},inplace = True)
d.sort_values(by = 'Decade',inplace=True)

## Get how many times each genre appears on the top 250 movies
df['genres'] = df['genres'].str.replace(', ',',')
genres = df['genres'].str.split(',',expand = True).stack().value_counts()
avgs = []
## Get average rating for each genre
for x in genres.index:
    n = df.loc[df['genres'].str.contains(x)]['rating'].mean()
    avgs.append(n)

## Convert rating to float
df['rating'] = pd.to_numeric(df['rating'], downcast="float")

## Convert votes to number, by replacing the letter (K or M), for the appropiate value
df['votes'] = df["votes"].replace({"K":"*1e3", "M":"*1e6"}, regex=True).map(pd.eval).astype(int)

## Split casts by commas and count how many times each members appears
df['crew'] = df['crew'].str.replace(', ',',')
tc = df['crew'].str.split(',',expand = True).stack().value_counts()
actors = tc.to_frame().reset_index()
actors.rename(columns = {'index':'name',0:'count'},inplace = True)
l = []

## Get average rating for each actor
for x in actors['name']:
    m = df.loc[df['crew'].str.contains(x)]['rating'].mean()
    l.append(m)
actors['avg'] = l

directors = df['director'].value_counts().to_frame().reset_index()
directors.rename(columns = {'index':'name','director':'count'},inplace = True)
u = []

## Get average rating for each director
for x in directors['name']:
    m = df.loc[df['director'] == x]['rating'].mean()
    u.append(m)
directors['avg'] = u

## Movies from each decade graph
fig = go.Figure(
    data = [
        go.Bar(name = 'Count', x = list(d['Decade']), y = list(d['Count']))
    ],
    layout={
        'yaxis': {'title': 'Count'},
        'xaxis': {'title': 'Decades'}
    }
)
fig.update_layout(
    barmode='group',
    autosize = True,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=5, r=0, t=25, b=0)
)

## Genres count and average rating graph
fig2 = go.Figure(
    data = [
        go.Bar(name = 'Count', x = list(genres.index), y = list(genres.values), yaxis='y', offsetgroup=1),
        go.Bar(name = 'Average rating', x = list(genres.index), y = avgs, yaxis='y2', offsetgroup=2),
    ],
    layout={
        'yaxis': {'title': 'Count'},
        'yaxis2': {'title': 'Average Rating', 'overlaying': 'y', 'side': 'right'},
        'xaxis': {'title': 'Genres'}
    }
)
fig2.update_layout(
    barmode='group',
    autosize = True,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=5, r=0, t=25, b=0)
)

## Genre popularity per decade graph 

fig3 = go.Figure()

for x in genres.index:
    c = df.loc[df['genres'].str.contains(x)]['decade'].value_counts().sort_index(axis=0)
    axis = c.to_frame().reset_index()
    axis.rename(columns={'decade':'count','index':'decade'},inplace=True)
    fig3.add_trace(go.Scatter(x = list(axis['decade']), y = list(axis['count']), name = str(x), mode='lines'))

fig3.update_layout(
    barmode='group',
    autosize = True,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=5, r=0, t=25, b=0)
)

## Scatter plot with release year, vote count and average rating

fig4 = px.scatter(df,x = 'year',y = 'votes',color='rating',hover_data=['title'])
fig4.update_traces(marker_size=10)
fig4.update_layout(
    barmode='group',
    autosize = True,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=5, r=0, t=25, b=0)
)

app.layout = dbc.Container(children = [
    html.H1("Scraping and analysis of IMDb top 250", className= 'p-6 mt-2'),
    dbc.Row(align = 'center',children = [
        dbc.Tabs(id = 'tabs', active_tab = 'count_decades', children = [
                    dbc.Tab(label = 'Movie count per decade',tab_id = 'count_decades',children = [
                        html.Div([
                            html.H2("Decade distribution between top 250", className= 'p-3'),
                            html.Div(children = [
                                html.Div(className = 'static_graph', children = [
                                    dcc.Graph(figure=fig,config={'displayModeBar': False})
                                ]),
                            ]),
                        ])
                    ]),
                    dbc.Tab(label = 'Average rating per rating', children = [
                        html.Div([
                            html.H2("Count and average rating per genre", className= 'p-3'),
                            html.Div(children = [
                                html.Div(className = 'static_graph', children = [
                                    dcc.Graph(figure=fig2,config={'displayModeBar': False})
                                ]),
                            ]),
                        ])
                    ]),
                    dbc.Tab(label = 'Genre popularity by decade', children = [
                        html.Div([
                            html.H2("Genre popularity by decade", className= 'p-3'),
                            html.Div(children = [
                                html.Div(className = 'static_graph', children = [
                                    dcc.Graph(figure=fig3,config={'displayModeBar': False})
                                ]),
                            ]),
                        ])
                    ]),
                    dbc.Tab(label = 'Vote count and rating', children = [
                        html.Div([
                            html.H2("Vote count and rating around the years", className= 'p-3'),
                            html.Div(children = [
                                html.Div(className = 'static_graph', children = [
                                    dcc.Graph(figure=fig4,config={'displayModeBar': False})
                                ]),
                            ]),
                        ])
                    ]),
                    dbc.Tab(label = 'Cast count and rating', children = [
                        dbc.Row(children = [
                            html.H2("Cast with most appearances and highest average rating", className= 'p-3'),
                            dbc.Col(md = 3,children = [
                                html.Div([
                                    html.Div(children=[
                                        html.H4('Select number of appearances or rating', className= 'p-1'),
                                        dcc.Dropdown(id="s_slct",
                                                        options=[
                                                            {'label':'Appearances','value':'Count'},
                                                            {'label':'Average rating','value':'Rating'}
                                                        ],
                                                        multi=False,
                                                        value="Count",
                                                        className='dropdown'
                                        ),
                                        html.H4('Select crew member', className= 'p-1'),
                                        dcc.Dropdown(id="t_slct",
                                                        options=[
                                                            {'label':'Actors/Actresses','value':'Actors'},
                                                            {'label':'Directors','value':'Directors'}
                                                        ],
                                                        multi=False,
                                                        value="Actors",
                                                        className='dropdown'
                                        )
                                    ]),
                                ])
                            ]),
                            dbc.Col(md = 9, children = [
                                html.Div(children = [
                                    dcc.Graph(id='fig5', figure={},config={'displayModeBar': False})
                                ]),
                            ])
                        ])
                    ])
                ])
        ])
])

@app.callback(
    Output(component_id='fig5', component_property='figure'),
    [Input(component_id='s_slct', component_property='value'),
    Input(component_id='t_slct', component_property='value')]
)


def update_graph(s_slct,t_slct):
    
    a_count = actors.sort_values(by = 'count',ascending  = False).head(10)
    a_rating = actors.sort_values(by = 'avg',ascending  = False).head(10)
    d_count = directors.sort_values(by = 'count',ascending  = False).head(10)
    d_rating = directors.sort_values(by = 'avg',ascending  = False).head(10)

    fig5 = go.Figure()

    ## Conditional to plot graph depending on selected option
    if t_slct == 'Actors':
        if s_slct == 'Count':
            fig5 = go.Figure(
                data = [
                    go.Bar(name = 'Count',x = list(a_count['name']),y = list(a_count['count'])),
                    go.Bar(name = 'Average rating',x = list(a_count['name']),y = list(a_count['avg']))
                ]
            )
        elif s_slct == 'Rating':
            fig5 = go.Figure(
                data = [
                    go.Bar(name = 'Count',x = list(a_rating['name']),y = list(a_rating['count'])),
                    go.Bar(name = 'Average rating',x = list(a_rating['name']),y = list(a_rating['avg']))
                ]
            )
    if t_slct == 'Directors':
        if s_slct == 'Count':
            fig5 = go.Figure(
                data = [
                    go.Bar(name = 'Count',x = list(d_count['name']),y = list(d_count['count'])),
                    go.Bar(name = 'Average rating',x = list(d_count['name']),y = list(d_count['avg']))
                ]
            )
        elif s_slct == 'Rating':
            fig5 = go.Figure(
                data = [
                    go.Bar(name = 'Count',x = list(d_rating['name']),y = list(d_rating['count'])),
                    go.Bar(name = 'Average rating',x = list(d_rating['name']),y = list(d_rating['avg']))
                ]
            )
    
    fig5.update_layout(
        barmode='group',
        autosize = True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=5, r=0, t=25, b=0)
    )

    return fig5

if __name__ == '__main__':
    app.run_server(debug=True)