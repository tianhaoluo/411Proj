import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output,dash_table  # pip install dash (version 2.0.0 or higher)
import dash
import mysql.connector as connection
import dash_bootstrap_components as dbc
import collections
from wordcloud import WordCloud          # pip install wordcloud
from dash_extensions import Lottie       # pip install dash-extensions
import credentials
from neo4jconn import Neo4jConnection
from pymongo import MongoClient
import pickle

#some lottie icons
url_coonections = "https://assets9.lottiefiles.com/private_files/lf30_5ttqPi.json"
url_companies = "https://assets9.lottiefiles.com/packages/lf20_EzPrWM.json"
url_msg_in = "https://assets9.lottiefiles.com/packages/lf20_8wREpI.json"
url_msg_out = "https://assets2.lottiefiles.com/packages/lf20_Cc8Bpg.json"
url_reactions = "https://assets2.lottiefiles.com/packages/lf20_nKwET0.json"
url_publications = "https://assets8.lottiefiles.com/packages/lf20_1Zt5Qk.json"
url_teamwork = "https://assets3.lottiefiles.com/packages/lf20_9s8fgged.json"
url_h = "https://assets6.lottiefiles.com/packages/lf20_ctx5upb6.json"
url_lightbulb = "https://assets3.lottiefiles.com/packages/lf20_Ugigaz.json"
options = dict(loop=True, autoplay=True, rendererSettings=dict(preserveAspectRatio='xMidYMid slice'))





app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )

#connect to sql
try:
    mydb = connection.connect(host="localhost", database = 'academicworld',user="root", passwd=credentials.mysql_pw,use_pure=True)
except Exception as e:
    mydb.close()
    print(str(e))

try:
    with open('keywords_df.pickle', 'rb') as handle:
        grouped_keywords = pickle.load(handle)
except:
    client = MongoClient('mongodb://localhost:27017/db')
    db_mongo = client['academicworld']
    df_mongo = pd.DataFrame(db_mongo['publications'].find())
    hm = {'keyword':[],'year':[],'citations':[]}
    for kws,yr,cite in zip(df_mongo['keywords'],df_mongo['year'],df_mongo['numCitations']):
        for kw in kws:
            hm['keyword'].append(kw['name'])
            hm['year'].append(yr)
            hm['citations'].append(cite)
    keywords_df = pd.DataFrame(hm)
    grouped_keywords = keywords_df.groupby(['keyword','year']).agg(['sum','count']).rename(columns={'sum':'#citations','count':'#publications'})
    with open('keywords_df.pickle', 'wb') as handle:
        pickle.dump(grouped_keywords, handle)




conn = Neo4jConnection(uri="bolt://localhost:7687", 
                       user="neo4j",              
                       pwd=credentials.neo4j_pw)


faculties_df = pd.read_sql("SELECT f.name,u.name AS university_name FROM faculty AS f JOIN university AS u ON u.id = f.university_id",mydb)
print(faculties_df.head())

faculties_dict = collections.defaultdict(list)
for f,u in zip(faculties_df['name'],faculties_df['university_name']):
    faculties_dict[u].append(f)

print(pd.read_sql("SHOW Tables;",mydb))
print(pd.read_sql("SELECT * FROM publication_keyword LIMIT 10;",mydb))
print(pd.read_sql("SELECT * FROM publication LIMIT 10;",mydb))

def h_index(citations_list):
    n = len(citations_list)
    cnt = [0]*(n+1)
    for c in citations_list:
        cnt[min(c,n)] += 1
    ans = 0
    for i in reversed(range(n+1)):
        ans += cnt[i]
        if ans >= i:
            return i




# ------------------------------------------------------------------------------
# App layout
app.layout = dbc.Container([

    dbc.Row(
        dbc.Col(html.H1(id="title",children="Researcher personal dashboard",
                        className='text-center text-primary mb-4'),
                width=12)
    ),

    dbc.Row([

        dbc.Col([
            html.P("Select University:",
                   style={"textDecoration": "underline"}),
            dcc.Dropdown(id='university_list', multi=False, value='University of illinois at Urbana Champaign',
                         options=[
                         {"label":u,"value":u} for u in sorted(faculties_dict.keys())
                         ],
                         )
        ],# width={'size':5, 'offset':1, 'order':1},
           xs=12, sm=12, md=12, lg=5, xl=5
        ),

        dbc.Col([
            html.P("Select Researcher:",
                   style={"textDecoration": "underline"}),
            dcc.Dropdown(id='faculty_list', multi=False, value="Kevin Chenchuan Chang",
                         options=[],
                         )
        ], #width={'size':5, 'offset':0, 'order':2},
           xs=12, sm=12, md=12, lg=5, xl=5
        ),

    ], className="g-0", justify='start'),  # Horizontal:start,center,end,between,around

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(Lottie(options=options, width="25%", height="25%", url=url_publications)),
                dbc.CardBody([
                    html.H6('# Publications'),
                    html.H2(id='content_publications', children="000")
                ], style={'textAlign':'center'})
            ]),
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(Lottie(options=options, width="45%", height="45%", url=url_lightbulb)),
                dbc.CardBody([
                    html.H6('# Citations'),
                    html.H2(id='content_citations', children="000")
                ], style={'textAlign':'center'})
            ]),
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(Lottie(options=options, width="25%", height="25%", url=url_h)),
                dbc.CardBody([
                    html.H6('h-index'),
                    html.H2(id='content_hindex', children="000")
                ], style={'textAlign':'center'})
            ]),
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(Lottie(options=options, width="25%", height="25%", url=url_teamwork)),
                dbc.CardBody([
                    html.H6('Collaborators'),
                    html.H2(id='content_collaborators', children="000")
                ], style={'textAlign': 'center'})
            ]),
        ], width=3),
    ],className='mb-2'),

    dbc.Row([
        dbc.Col([
            # dbc.Card([
            #     dbc.CardHeader(Lottie(options=options, width="53%", height="53%", url=url_msg_out)),
            #     dbc.CardBody([
            #         html.H6('Invites sent'),
            #         html.H2(id='content-msg-out', children="000")
            #     ], style={'textAlign': 'center'})
            # ]),
            dbc.Card(
                [
                    
                    dbc.CardImg(
                        id = "main_faculty",
                        src={},
                        bottom=True),
                ],
                style={"width": "24rem"},
            )
        ], xs=12, sm=12, md=12, lg=3, xl=3),
         dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='wordcloud', figure={}, config={'displayModeBar': False}),
                ])
            ]),
        ],  #width={'size':5, 'offset':1},
           #xs=8, sm=8, md=8, lg=5, xl=5
           xs=12, sm=12, md=12, lg=5, xl=5
        ),
         dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2('Top collaborators',style={'text-align':'center'}),
                    dash_table.DataTable(id='colab_table')
                ])
            ]),
        ],  #width={'size':5, 'offset':1},
           #xs=8, sm=8, md=8, lg=5, xl=5
           xs=12, sm=12, md=12, lg=4, xl=4
        )
    ], align="center"),  # Vertical: start, center, end

    dbc.Row(
        dbc.Col(html.H1(id="title2",children="Exploring research trend",
                        className='text-center text-primary mb-4'),
                width=12)
    ),

    dbc.Row([

        dbc.Col([
            html.P("Select keyword:",
                   style={"textDecoration": "underline"}),
            dcc.Dropdown(id='kw', multi=False, value='deep learning',
                         options=[
                         {"label":u,"value":u} for u in list(grouped_keywords.index.get_level_values(0).unique())
                         ],
                         )
        ],# width={'size':5, 'offset':1, 'order':1},
           xs=12, sm=12, md=12, lg=5, xl=5
        ),

        dbc.Col([
            html.P("Select metric type:",
                   style={"textDecoration": "underline"}),
            dcc.RadioItems(id='radio',options=['#publications','#citations'], value='#publications')
        ], #width={'size':5, 'offset':0, 'order':2},
           xs=12, sm=12, md=12, lg=5, xl=5
        ),

    ], className="g-0", justify='start'),

    dbc.Row([

        dbc.Col([
            dcc.Graph(id='linechart', figure={})
        ],# width={'size':5, 'offset':1, 'order':1},
           xs=12, sm=12, md=12, lg=12, xl=12
        )

    ], className="g-0", justify='start')

    

], fluid=True)



# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    Output('faculty_list', 'options'),
    Output('faculty_list', 'value'),
    Input('university_list', 'value'))
def set_faculty_options(selected_university):
    return [{'label': i, 'value': i} for i in sorted(faculties_dict[selected_university])],sorted(faculties_dict[selected_university])[0]


@app.callback(
    [
    Output('title','children'),
    Output('main_faculty','src'),
    Output(component_id="content_publications",component_property='children'),
    Output(component_id="content_citations",component_property='children'),
    Output(component_id="content_hindex",component_property='children'),
    Output(component_id="content_collaborators",component_property='children'),
    Output(component_id="wordcloud",component_property='figure'),
    Output(component_id="colab_table",component_property='data'),
    Output(component_id="colab_table",component_property='columns')
    ],
    [Input(component_id="university_list",component_property='value'),
    Input(component_id='faculty_list',component_property='value')
    ]
    )
def update_graph(university_name,faculty_name):
    print(university_name)
    print(faculty_name)

    basic_info_query = """
        SELECT f.*,u.name AS university_name
            FROM faculty AS f
            LEFT JOIN university AS u
            ON f.university_id = u.id
            WHERE f.name = "{}" AND u.name = "{}"
    """.format(faculty_name,university_name)

    df_basic_info = pd.read_sql(basic_info_query,mydb)
    query = """
        SELECT publications,num_citations
            FROM ResearcherFacts
            WHERE faculty_name = "{}" AND university_name = "{}"
    """.format(faculty_name,university_name)
    df = pd.read_sql(query,mydb)

    total_publications = sum(df['publications'])
    total_citations = sum(df['num_citations'])

    # df.sort_values("year",inplace=True)
    # fig1 = px.line(df,x="year",y='publications',title="publications by year")
    # fig2 = px.line(df,x="year",y='num_citations',title="citations by year")

    query_kw = """
        SELECT k.name AS kw,num_citations
            FROM faculty AS f
            LEFT JOIN faculty_publication AS fp
            ON f.id = fp.faculty_id
            JOIN publication AS p
            ON fp.publication_id = p.id
            JOIN university AS u
            ON f.university_id = u.id
            JOIN publication_keyword AS pk
            ON p.id = pk.publication_id
            JOIN keyword AS k
            ON pk.keyword_id = k.id
            WHERE f.name = "{}" AND u.name = "{}"
    """.format(faculty_name,university_name)

    query_citations = """
        SELECT num_citations
            FROM faculty AS f
            LEFT JOIN faculty_publication AS fp
            ON f.id = fp.faculty_id
            JOIN publication AS p
            ON fp.publication_id = p.id
            JOIN university AS u
            ON f.university_id = u.id
            WHERE f.name = "{}" AND u.name = "{}"
    """.format(faculty_name,university_name)

    df_cite = pd.read_sql(query_citations,mydb)
    print(df_cite)
    df = pd.read_sql(query,mydb)
    kw_df = pd.read_sql(query_kw,mydb)
    print(kw_df)
    citations_list = list(df_cite['num_citations'])
    print(citations_list)
    hind = h_index(citations_list)
    keywords = list(kw_df['kw'])
    my_wordcloud = WordCloud(
            background_color='white',
            height=275,width=400
        ).generate("Nothing to show")
    if len(keywords) > 0:
        my_wordcloud = WordCloud(
            background_color='white',
            height=275,width=400
        ).generate(' '.join(keywords))

    fig_wordcloud = px.imshow(my_wordcloud, template='ggplot2',
                              title="Research interests")
    fig_wordcloud['layout']['title']['font'] = dict(size=24)
    fig_wordcloud.update_layout(margin=dict(l=5, r=5, t=40, b=5))
    fig_wordcloud.update_xaxes(visible=False)
    fig_wordcloud.update_yaxes(visible=False)

    neo4j_query_string = """MATCH (u:INSTITUTE)<- [af:AFFILIATION_WITH]- (f:FACULTY) 
                        -[p:PUBLISH] -> (paper:PUBLICATION) <- [p2:PUBLISH] - (f1:FACULTY) WHERE f.name = "{}" AND u.name = "{}" AND f.name <> f1.name RETURN f1.name AS name, 
                        f1.photoUrl AS photoUrl,paper.title AS title""".format(faculty_name,university_name)
    print(neo4j_query_string)

    top_collaborators = pd.DataFrame([dict(_) for _ in conn.query(neo4j_query_string,db="academicworld")])
    print(top_collaborators)

    default_colab_frame = pd.DataFrame({"collaborator":["Nobody - be more collaborative!"]})
    data = default_colab_frame.to_dict(orient='records')
    columns = [{'name': col, 'id': col} for col in default_colab_frame]

    if top_collaborators.shape[0] > 0:
        tc_agg = top_collaborators.groupby(['name','photoUrl']).count().reset_index()
        print(tc_agg)

        tc_agg.columns = ['name','photoUrl','collaborations']
        tc_agg.drop(columns='photoUrl',inplace=True)

        tc_agg.sort_values('collaborations',inplace=True,ascending=False)
        columns = [{'name': col, 'id': col} for col in tc_agg]
        data = tc_agg.head(10).to_dict(orient='records')

    photo_url = list(df_basic_info['photo_url'])[0] if df_basic_info.shape[0] > 0 else None


    return faculty_name+"'s Research Dashboard",photo_url,total_publications,total_citations,hind,tc_agg.shape[0] if top_collaborators.shape[0] > 0 else 0,fig_wordcloud,data,columns

@app.callback(
    [
    Output(component_id='linechart',component_property='figure')
    ],
    [Input(component_id="kw",component_property='value'),
    Input(component_id='radio',component_property='value')
    ]
    )
def update_graph_kw(kw,metric):
    print(grouped_keywords.loc[kw]['citations'][metric])
    plot_df = grouped_keywords.loc[kw]['citations'][metric].reset_index().copy()

    fig_kw = px.line(plot_df,x='year',y=metric)
    return [go.Figure(data=fig_kw)]



# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)