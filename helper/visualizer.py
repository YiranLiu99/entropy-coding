import igraph
import plotly.graph_objects as go


def visualize_tree(G_networkx):
    def make_annotations(pos, labels, font_size=10, font_color='rgb(250,250,250)'):
        L = len(pos)
        if len(labels) != L:
            raise ValueError('The lists pos and text must have the same len')
        annotations = []
        for k in range(L):
            annotations.append(
                dict(
                    text=labels[k],
                    x=pos[k][0], y=2 * M - pos[k][1],
                    xref='x1', yref='y1',
                    font=dict(color=font_color, size=font_size),
                    showarrow=False)
            )
        return annotations

    # Function to convert NetworkX graph to igraph graph
    def nx_to_igraph(networkx_graph):
        edges = [edge for edge in networkx_graph.edges()]
        return igraph.Graph.TupleList(edges)

    # Convert NetworkX graph to igraph graph
    G_igraph = nx_to_igraph(G_networkx)

    lay = G_igraph.layout('rt')
    nr_vertices = len(G_networkx.nodes)
    position = {k: lay[k] for k in range(nr_vertices)}
    Y = [lay[k][1] for k in range(nr_vertices)]
    M = max(Y)

    es = G_igraph.es()  # sequence of edges
    E = [e.tuple for e in es]  # list of edges

    L = len(position)
    Xn = [position[k][0] for k in range(L)]
    Yn = [2 * M - position[k][1] for k in range(L)]
    Xe = []
    Ye = []
    for edge in E:
        Xe += [position[edge[0]][0], position[edge[1]][0], None]
        Ye += [2 * M - position[edge[0]][1], 2 * M - position[edge[1]][1], None]

    labels = [G_networkx.nodes[node]['label'] for node in G_networkx.nodes]  # Extract labels from NetworkX nodes

    fig = go.Figure()
    # add a scatter trace with the edges
    fig.add_trace(go.Scatter(x=Xe,
                             y=Ye,
                             mode='lines',
                             line=dict(color='rgb(210,210,210)', width=1),
                             hoverinfo='none'
                             ))
    # add a scatter trace with the nodes
    fig.add_trace(go.Scatter(x=Xn,
                             y=Yn,
                             mode='markers',
                             name='node',
                             marker=dict(symbol='circle-dot',
                                         size=18,
                                         color='#6175c1',  # '#DB4551',
                                         line=dict(color='rgb(50,50,50)', width=1)
                                         ),
                             text=labels,
                             hoverinfo='text',
                             opacity=0.8
                             ))

    axis = dict(showline=False,
                zeroline=False,
                showgrid=False,
                showticklabels=False,
                )

    fig.update_layout(title='Tree with Reingold-Tilford Layout',
                      annotations=make_annotations(position, labels),
                      font_size=12,
                      showlegend=False,
                      xaxis=axis,
                      yaxis=axis,
                      margin=dict(l=40, r=40, b=85, t=100),
                      hovermode='closest',
                      plot_bgcolor='rgb(248,248,248)'
                      )
    # fig.show()
    return fig