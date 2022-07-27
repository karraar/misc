#!/usr/bin/env python3

# https://graphviz.org/doc/info/attrs.html
from sys import argv
from graphviz import Digraph
import json

SYSTEM_SHAPES = {'s3': {'shape': 'folder', 'color': 'orange'},
                 'fivetran': {'shape': 'tripleoctagon', 'color': 'lime'},
                 'redshift': {'shape': 'cylinder', 'color': 'thistle'},
                 'redshift-external': {'shape': 'invhouse', 'color': 'yellow'},
                 'default': {'shape': 'oval', 'color': 'turquoise'}
                 }


def html_bold(s):
    return '<b>{0}</b>'.format(s)


def html_underline(s):
    return '<u>{0}</u>'.format(s)


def html_newline():
    return '<br></br>'


def format_label(s):
    parts = s.split('|')
    if len(parts) >= 3:
        return '<{0}{1}{2}{3}{4}>'.format(html_underline(html_bold(parts[0].capitlaize())),
                                          html_newline(),
                                          html_bold(parts[1]),
                                          html_newline(),
                                          '|'.join(parts[2:]))
    elif len(parts) == 2:
        return '<{0}{1}{2}>'.format(html_underline(html_bold(parts[0].capitalize())),
                                    html_newline(),
                                    '|'.join(parts[1:]))
    else:
        return s


class DigraphNode(object):
    def __init__(self, system, label):
        self.system = system
        self.label = label
        self.name = '{0}.{1}'.format(system, label)
        self.formatted_label = format_label(self.name)


class DigraphLineage(object):
    def __init__(self, graph_name):
        self.graph_name = graph_name
        self.digraph = Digraph(name=self.graph_name, comment=self.graph_name)
        self.nodes = []

    def add_node(self, system, label):
        node = DigraphNode(system, label)
        if node.name not in self.nodes:
            self.nodes.append(node.name)
            self.digraph.node(name=node.name,
                              label=node.formatted_label,
                              style='filled',
                              shape=SYSTEM_SHAPES[system]['shape'],
                              color=SYSTEM_SHAPES[system]['color'],
                              fontsize='12.0')
        return node

    def add_edge(self, node_source, node_dest, edge_label):
        self.digraph.edge(tail_name=node_source.name,
                          head_name=node_dest.name,
                          label=edge_label,
                          fontsize='10.0')

    def generate(self):
        self.digraph.view(filename=self.graph_name,
                          cleanup=True,
                          quiet=True,
                          quiet_view=True)


if __name__ == "__main__":
    dep_file = argv[1]
    digraph = DigraphLineage(graph_name=dep_file.split('.')[0])
    with open(dep_file) as f:
        config = json.load(f)
        digraph.digraph.attr(label=config["label"], fontsize='20')
        for config_mapping in config["mappings"]:
            source_node = digraph.add_node(config_mapping['source']['system'],
                                           config_mapping['source']['label'])
            dest_node = digraph.add_node(config_mapping['dest']['system'],
                                         config_mapping['dest']['label'])
            digraph.add_edge(source_node,
                             dest_node,
                             format_label(config_mapping['edge']['label']))

    digraph.generate()
