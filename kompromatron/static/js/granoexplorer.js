/* jshint strict: true, quotmark: false, es3: true */
/* global $: false, d3: false, Grano: false */

window.Grano = window.Grano || {};

Grano.graph = function(selector, domain, project, seed, options){
  "use strict";
  var schemas = {};
  var depth = options.depth || 1;

  var color = d3.scale.category20b();


  var w = $(selector).width(),
      h = $(selector).height(),
      node,
      link;
  var nodeList = [];
  var linkList = [];

  var force = d3.layout.force()
    .charge(function(d) { return d.isRoot ? -80 : -60; })
    .linkDistance(function(d) { return d.isRoot ? 50 : 30; })
    .size([w, h]);

  var vis = d3.select(selector).append("svg:svg")
      .attr("width", w)
      .attr("height", h);

  var getEntity = function(entity){
    return $.getJSON(domain + '/api/1/entities/' + entity);
  };
  var getGraph = function(entity, depth){
    depth = depth || 2;
    return $.getJSON(domain + '/api/1/entities/' + entity + '/graph?depth=' + depth);
  };

  $.getJSON(domain + '/api/1/projects/' + project + '/schemata').then(function(obj){
    obj.results.forEach(function(s){
      schemas[s.name] = s;
    });
    getGraph(seed, depth).done(function(graph){
      var nodes = {};
      var links = {};
      graph.relations.forEach(function(r){
        if (nodes[r.source] === undefined) {
          nodes[r.source] = {
            name: graph.entities[r.source]['property.name']
          };
        }
        if (nodes[r.target] === undefined) {
          nodes[r.target] = {
            name: graph.entities[r.target]['property.name']
          };
        }
        if (links[r.source] === undefined) {
          links[r.source] = [];
        }
        links[r.source].push({
          target: r.target,
          schema: r['schema.name']
        });
      });

      nodes[graph.root].fixed = true;
      nodes[graph.root].isRoot = true;
      nodes[graph.root].x = w / 2;
      nodes[graph.root].y = h / 2;

      var nodeid;
      for (nodeid in nodes) {
        nodes[nodeid].id = nodeid;
        nodeList.push(nodes[nodeid]);
        nodes[nodeid].index = nodeList.length - 1;
      }
      var addLink = function(l){
        linkList.push({
          source: nodes[nodeid].index,
          target: nodes[l.target].index,
          schema: l.schema
        });
      };
      for (nodeid in links) {
        links[nodeid].forEach(addLink);
      }
      update();
    });
  });

  function update() {
    // Restart the force layout.
    force
        .nodes(nodeList)
        .links(linkList)
        .start();

    // Update the links…
    link = vis.selectAll("line.link")
        .data(linkList);

    // Enter any new links.
    link.enter().insert("svg:line", ".node")
        .attr("class", "link")
        .style("stroke", function(d) { return color(d.schema); });


    // Exit any old links.
    link.exit().remove();

    // Update the nodes…
    node = vis.selectAll("circle.node")
      .data(nodeList);

    node.enter().append("svg:circle")
        .classed("node", true)
        .classed("root", function(d){ return !!d.isRoot; })
        .classed("related", function(d){ return !d.isRoot; })
        // .classed("entity", function(d){ return !!d.isEntity; })
        // .attr("cx", function(d) { return d.x; })
        // .attr("cy", function(d) { return d.y; })
        .attr("r", function(d){ return d.isRoot ? 15 : 5; })
        .attr('title', function(d){ return d.name; })
        // .style("fill", function(d){ return color(d.schema); })
        .on("click", click)
        .on("mouseover", function(d){
          $(options.titleSelector).text(d.name);
        })
        .attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; })
        .call(force.drag);

    // Exit any old nodes.
    node.exit().remove();
  }
  force.on("tick", function() {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.filter('.related').attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });
  });

  // Color leaf nodes orange, and packages white or blue.

  // Toggle children on click.
  function click(d) {
    document.location.href = '/entities/' + d.id;
  }

};