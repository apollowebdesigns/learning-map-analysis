from bs4 import BeautifulSoup

html_content = """
<tbody><tr>
<td><table style="background:#76b3df; color: black; text-align:left; border:1px solid darkgrey; width: 130px;"><tbody><tr><td style="background:gray; height: 3px;"></td></tr><tr><td style="height: 30px; text-align: right; vertical-align: top;"><small><a class="mw-selflink selflink">Perfect Graphs</a><br /><i></i></small></td></tr><tr><td style="background:gray;"></td></tr><tr><td colspan="5" style="height: 135px; text-align: center; vertical-align: middle;"><span typeof="mw:File"><a href="/wiki/File:Turan_13-4.svg" class="mw-file-description"><img src="//upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Turan_13-4.svg/125px-Turan_13-4.svg.png" decoding="async" width="125" height="125" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Turan_13-4.svg/188px-Turan_13-4.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Turan_13-4.svg/250px-Turan_13-4.svg.png 2x" data-file-width="470" data-file-height="470" /></a></span></td></tr></tbody></table>
</td></tr></tbody></table>
<div class="mw-heading mw-heading2"><h2 id="Perfect_Graphs">Perfect Graphs</h2><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=User:David_Eppstein/Perfect_Graphs&amp;action=edit&amp;section=1" title="Edit section: Perfect Graphs"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span></div>
<dl><dt>Background and definitions</dt>
<dd><a href="/wiki/Graph_theory" title="Graph theory">Graph theory</a></dd>
<dd><a href="/wiki/Graph_(discrete_mathematics)" title="Graph (discrete mathematics)">Undirected graphs</a></dd>
<dd><a href="/wiki/Clique_(graph_theory)" title="Clique (graph theory)">Cliques</a></dd>
<dd><a href="/wiki/Independent_set_(graph_theory)" title="Independent set (graph theory)">Independent sets</a></dd>
<dd><a href="/wiki/Graph_coloring" title="Graph coloring">Graph coloring</a></dd>
<dd><a href="/wiki/Clique_cover" title="Clique cover">Clique cover</a></dd>
<dd><a href="/wiki/Induced_path" title="Induced path">Induced cycle</a></dd>
<dd><a href="/wiki/Perfect_graph" title="Perfect graph">Perfect graph</a></dd></dl>
<dl><dt>Structure theorems and perfection-preserving graph operations</dt>
<dd><a href="/wiki/Complement_graph" title="Complement graph">Complement graph</a></dd>
<dd><a href="/wiki/Induced_subgraph" title="Induced subgraph">Induced subgraph</a></dd>
<dd><a href="/wiki/Skew_partition" title="Skew partition">Skew partition</a></dd>
<dd><a href="/wiki/Lexicographic_product_of_graphs" title="Lexicographic product of graphs">Lexicographic product of graphs</a></dd>
<dd><a href="/wiki/Perfect_graph_theorem" title="Perfect graph theorem">Perfect graph theorem</a></dd>
<dd><a href="/wiki/Strong_perfect_graph_theorem" title="Strong perfect graph theorem">Strong perfect graph theorem</a></dd></dl>
<dl><dt>Bipartite graphs, their line graphs, and their matchings</dt>
<dd><a href="/wiki/Bipartite_graph" title="Bipartite graph">Bipartite graph</a></dd>
<dd><a href="/wiki/Line_graph" title="Line graph">Line graph</a></dd>
<dd><a href="/wiki/Matching_(graph_theory)" title="Matching (graph theory)">Matching (graph theory)</a></dd>
<dd><a href="/wiki/Hall%27s_marriage_theorem" title="Hall&#39;s marriage theorem">Hall's marriage theorem</a></dd>
<dd><a href="/wiki/K%C5%91nig%27s_theorem_(graph_theory)" title="Kőnig&#39;s theorem (graph theory)">Kőnig's theorem (graph theory)</a></dd>
<dd><a href="/wiki/Dulmage%E2%80%93Mendelsohn_decomposition" title="Dulmage–Mendelsohn decomposition">Dulmage–Mendelsohn decomposition</a></dd>
<dd><a href="/wiki/Rook%27s_graph" title="Rook&#39;s graph">Rook's graph</a></dd></dl>
<dl><dt>Chains and antichains in partial orders</dt>
<dd><a href="/wiki/Partially_ordered_set" title="Partially ordered set">Partially ordered set</a></dd>
<dd><a href="/wiki/Comparability_graph" title="Comparability graph">Comparability graph</a></dd>
<dd><a href="/wiki/Dilworth%27s_theorem" title="Dilworth&#39;s theorem">Dilworth's theorem</a></dd>
<dd><a href="/wiki/Mirsky%27s_theorem" title="Mirsky&#39;s theorem">Mirsky's theorem</a></dd>
<dd><a href="/wiki/Cograph" title="Cograph">Cograph</a></dd>
<dd><a href="/wiki/Threshold_graph" title="Threshold graph">Threshold graph</a></dd>
<dd><a href="/wiki/Trivially_perfect_graph" title="Trivially perfect graph">Trivially perfect graph</a></dd>
<dd><a href="/wiki/Permutation_graph" title="Permutation graph">Permutation graph</a></dd></dl>
<dl><dt>Chordal and interval graphs</dt>
<dd><a href="/wiki/Chordal_graph" title="Chordal graph">Chordal graph</a></dd>
<dd><a href="/wiki/Interval_graph" title="Interval graph">Interval graph</a></dd>
<dd><a href="/wiki/Apollonian_network" title="Apollonian network">Apollonian network</a></dd>
<dd><a href="/wiki/Block_graph" title="Block graph">Block graph</a></dd>
<dd><a href="/wiki/Indifference_graph" title="Indifference graph">Indifference graph</a></dd>
<dd><a href="/wiki/K-tree" title="K-tree">K-tree</a></dd>
<dd><a href="/wiki/Leaf_power" title="Leaf power">Leaf power</a></dd>
<dd><a href="/wiki/Outerplanar_graph" title="Outerplanar graph">Maximal outerplanar graph</a></dd>
<dd><a href="/wiki/Ptolemaic_graph" title="Ptolemaic graph">Ptolemaic graph</a></dd>
<dd><a href="/wiki/Split_graph" title="Split graph">Split graph</a></dd>
<dd><a href="/wiki/Strongly_chordal_graph" title="Strongly chordal graph">Strongly chordal graph</a></dd>
<dd><a href="/wiki/Windmill_graph" title="Windmill graph">Windmill graph</a></dd></dl>
<dl><dt>Other classes of perfect graphs</dt>
<dd><a href="/wiki/Distance-hereditary_graph" title="Distance-hereditary graph">Distance-hereditary graph</a></dd>
<dd><a href="/wiki/Line_perfect_graph" title="Line perfect graph">Line perfect graph</a></dd>
<dd><a href="/wiki/Meyniel_graph" title="Meyniel graph">Meyniel graph</a></dd>
<dd><a href="/wiki/Parity_graph" title="Parity graph">Parity graph</a></dd>
<dd><a href="/wiki/Perfectly_orderable_graph" title="Perfectly orderable graph">Perfectly orderable graph</a></dd>
<dd><a href="/wiki/Tolerance_graph" title="Tolerance graph">Tolerance graph</a></dd>
<dd><a href="/wiki/Trapezoid_graph" title="Trapezoid graph">Trapezoid graph</a></dd></dl>
"""

def extract_chapters(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    chapters = {}
    
    for dl in soup.find_all("dl"):
        # Get the chapter name from <dt>
        chapter_name = dl.find("dt").text.strip() if dl.find("dt") else "Unknown Chapter"
        chapters[chapter_name] = {}
        
        for dd in dl.find_all("dd"):
            link = dd.find("a")
            if link:
                topic_name = link.text.strip()
                href = link.get("href")
                if href and not href.startswith("http"):
                    href = "https://en.wikipedia.org" + href  # Construct full URL if relative
                chapters[chapter_name][topic_name] = {
                    "href": href,
                    "book": "Perfect Graphs"
                }
    return chapters

chapters_dict = extract_chapters(html_content)

import json
with open("Perfect_Graphs.json", "w") as f:
    json.dump(chapters_dict, f)
