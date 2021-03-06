"""
Author: Alex Cannan
Date Created: 4/22/20
Purpose: This module will be the main script to call when searching for article
sources. Right now the url is hardcoded, but this can be replaced by argparse.
"""

from pprint import pprint
from urllib.parse import urlparse, urlunparse

import networkx as nx
from newspaper import Article

from source_node import SourceNode
from visualize import draw_source_tree_matplotlib

url = 'https://www.thegatewaypundit.com/2019/11/revealed-adam-schiff-connected-to-both-companies-named-in-7-4-billion-burisma-us-ukraine-corruption-case/'
# url = "https://www.cnn.com/2020/08/22/politics/donald-trump-popular-vote-analysis/index.html"


def clean_url(url):
    return urlunparse(urlparse(url))


def get_domain(url):
    """ Returns domain of url """
    return urlparse(url).netloc


def count_articles_at_depth(G, d):
    """ Counts number of articles at a certain depth """
    return len([x for x in G.nodes if G.nodes[x]["scan_depth"] == d])


def get_leaf_depths(G):
    leaves = [G.nodes[x]["scan_depth"] for x in G.nodes()
              if G.nodes[x]["parsed"] == False]
    return leaves


def get_sources(G, node_url):
    new_depth = G.nodes[node_url]["scan_depth"] + 1
    node = SourceNode(node_url)
    node.get_links()
    node.filter_links(check_blacklist=False, ignore_local=False)
    for i, link in enumerate(node.links):
        if clean_url(link) not in G:
            G.add_node(clean_url(link),
                       scan_depth=new_depth,
                       parsed=False,
                       pos=[new_depth,
                            count_articles_at_depth(G, new_depth)],
                       domain=get_domain(link)+"\n")
        G.add_edge(node_url, clean_url(link))
    G.nodes[node_url]["parsed"] = True
    return G


def recursive_source_check(url, max_level=3):
    G = nx.DiGraph()
    G.add_node(clean_url(url), scan_depth=0, parsed=True,
               pos=[0, 0], domain=get_domain(url))
    G = get_sources(G, clean_url(url))
    while any(x < max_level for x in get_leaf_depths(G)):
        urls = [x for x in G.nodes() if G.nodes[x]["parsed"] == False]
        G = get_sources(G, clean_url(urls[0]))
    return G


def save_source_tree(G):
    nx.write_gpickle(G, "source_tree.pickle")


if __name__ == '__main__':
    G = recursive_source_check(url, max_level=3)
    save_source_tree(G)
    draw_source_tree_matplotlib(G)
