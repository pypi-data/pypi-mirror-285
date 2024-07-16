"""
@Author = 'Mike Stanley'

Generates a networkx graph of equivalent suffixes based upon a list of suffixes.

E.G.
.wav .mp3 .wav .ogg .doc .docx

Generates a graph of
.wav .mp3
.wav .ogg
.doc .docx

============ Change Log ============
2018-May-14 = Added error handling if the equivalent_edges is not iterable.

2018-May-09 = Imported from Titanium_Monticello.Utilities

2017-Aug-10 = Add logging to generate_equivalency_graph

              Re-write generate_equivalency_graph to use the zip method to convert the list into pairs.
              https://stackoverflow.com/questions/4628290/pairs-from-single-list

============ License ============
The MIT License (MIT)

Copyright (c) 2017-2018, 2024 Michael Stanley

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
import wmul_logger


_logger = wmul_logger.get_logger()


def generate_equivalency_graph(equivalent_edges):
    _logger.debug(f"In generate_equivalency_graph with {equivalent_edges}")
    g = nx.Graph()
    try:
        pairs = zip(equivalent_edges[::2], equivalent_edges[1::2])
        g.add_edges_from(pairs)
    except TypeError as te:
        pass
    return g
