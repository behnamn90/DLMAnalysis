XY_SCALE = 10

# used for drawing
default_colours = ["#4D5656", "#229954", "#21618C", "#9C640C"]
default_colour_names = [
    "Scaffold",
    "One-domain staple",
    "Two-domain staple",
    "Three-domain staple",
]

""" 
Order parameters in the domain-level model and their code values:
BP: Base Pair, DOM: Domain, CR: Crossover, ST: Staple, HLX: Helix,
LH: Left-Helix, RH: Right-Helix, CRPair: Crossover Pair 
"""
op_dict = {
    "BP": "0",
    "DOM": "1",
    "CR": "2",
    "ST": "3",
    "HLX": "4",
    "LH": "5",
    "RH": "6",
    "CRPair": "7",
}


import matplotlib


def draw(G, ax, pos):
    """
    Draw a graph using matplotlib.

    Parameters:
    - G: NetworkX graph object
    - ax: Matplotlib Axes object to draw the graph on
    - pos: Dictionary of node positions

    Returns:
    - e: Matplotlib FancyArrowPatch object representing the drawn graph
    """
    colors = [G[u][v]["color"] for u, v in G.edges()]
    widths = [G[u][v]["width"] for u, v in G.edges()]
    for n in G:
        c = matplotlib.patches.Circle(pos[n], radius=0.001, alpha=1.0, color="black")
        ax.add_patch(c)
        G.node[n]["patch"] = c
        x, y = pos[n]
    seen = {}
    for u, v, d in G.edges(data=True):
        if d["show"]:
            alpha = 1
            n1 = G.node[u]["patch"]
            n2 = G.node[v]["patch"]
            rad = G[u][v]["arc"]
            if (u, v) in seen:
                rad = seen.get((u, v))
            color = G[u][v]["color"]
            e = matplotlib.patches.FancyArrowPatch(
                n1.center,
                n2.center,
                patchA=n1,
                patchB=n2,
                arrowstyle="-",
                connectionstyle="arc3,rad=%s" % rad,
                mutation_scale=10.0,
                lw=2,
                alpha=alpha,
                color=color,
            )
            seen[(u, v)] = rad
            ax.add_patch(e)
    return e
