"""
@Author = 'Mike Stanley'

============ Change Log ============
2018-May-09 = Created.

============ License ============
The MIT License (MIT)

Copyright (c) 2018 Michael Stanley

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import networkx as nx
from wmul_file_manager.utilities import graph


def test_generate_equivalency_graph_two_items():
    edges = [".wav", ".mp3"]
    result = graph.generate_equivalency_graph(edges)
    assert result.has_edge(".wav", ".mp3")
    assert result.number_of_nodes() == 2
    assert result.number_of_edges() == 1


def test_generate_equivalency_graph_four_items():
    edges = [".wav", ".mp3", ".wav", ".ogg"]
    result = graph.generate_equivalency_graph(edges)

    assert result.has_edge(".wav", ".mp3")
    assert result.has_edge(".wav", ".mp3")

    mp3_connected_components = nx.node_connected_component(result, ".mp3")
    assert ".wav" in mp3_connected_components
    assert ".ogg" in mp3_connected_components

    ogg_connected_components = nx.node_connected_component(result, ".ogg")

    assert ".wav" in ogg_connected_components
    assert ".mp3" in ogg_connected_components

    assert result.number_of_nodes() == 3
    assert result.number_of_edges() == 2


def test_generate_equivalency_graph_five_items():
    edges = [".wav", ".mp3", ".wav", ".ogg", ".wma"]
    result = graph.generate_equivalency_graph(edges)

    assert result.has_edge(".wav", ".mp3")
    assert result.has_edge(".wav", ".mp3")
    assert not result.has_node(".wma")


def test_generate_equivalency_graph_zero_items():
    edges = []
    result = graph.generate_equivalency_graph(edges)
    assert result.number_of_nodes() == 0
    assert result.number_of_edges() == 0


def test_generate_equivalency_graph_one_item():
    edges = [".wav"]
    result = graph.generate_equivalency_graph(edges)
    assert result.number_of_nodes() == 0
    assert result.number_of_edges() == 0

def test_generate_equivalency_graph_none_item():
    edges = None
    result = graph.generate_equivalency_graph(edges)
    assert result.number_of_nodes() == 0
    assert result.number_of_edges() == 0
