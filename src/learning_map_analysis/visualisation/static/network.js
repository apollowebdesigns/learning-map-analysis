// Specify the size of the canvas
var width = 1000, height = 2000;

// Create a color scale
var color = d3.scaleOrdinal(d3.schemeCategory10);

// Create a force simulation
var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(d => d.id).distance(30))
    .force("charge", d3.forceManyBody().strength(-120))
    .force("center", d3.forceCenter(width / 2, height / 2));

// Create or select the SVG element
var svg = d3.select("#d3-example").select("svg");
if (svg.empty()) {
    svg = d3.select("#d3-example").append("svg")
        .attr("width", width)
        .attr("height", height);
}

// Load the JSON file
d3.json("/static/graph.json").then(function(graph) {
    // Create link elements
    var link = svg.selectAll(".link")
        .data(graph.links)
        .join("line")
        .attr("class", "link");

    // Create node elements
    var node = svg.selectAll(".node")
        .data(graph.nodes)
        .join("circle")
        .attr("class", "node")
        .attr("r", 5)
        .style("fill", d => color(d.club))
        .call(drag(simulation));

    // Add titles to nodes
    node.append("title")
        .text(d => d.name);

    // Update positions on each tick
    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);
    });

    // Initialize the simulation with nodes and links
    simulation.nodes(graph.nodes);
    simulation.force("link").links(graph.links);
});

// Drag function for nodes
function drag(simulation) {
    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }

    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }

    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }

    return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
}
