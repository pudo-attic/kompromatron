/* jshint strict: true, es3: true */
/* global $: false, d3: false, Grano: false */

window.Grano = window.Grano || {};

Grano.graph = function(selector, domain, project, seed, options){
  'use strict';
  var schemas = {};
  var MIN_WEIGHT = 1;
  var depth = options.depth || 1;

  var color = d3.scale.category20b();

  d3.selection.prototype.moveToFront = function() {
    return this.each(function() {
      this.parentNode.appendChild(this);
    });
  };

  var w = $(selector).width(),
      h = $(selector).height(),
      r = 10,
      node,
      link;
  var nodeList = [];
  var linkList = [];

  var force = d3.layout.force()
    // .friction(0.5)
    // .chargeDistance(function(d){
    //   return 10 + Math.sqrt(d.source.weight + d.target.weight) * 2;
    // })
    // .size([w / 2, h / 2]);
    .charge(-60)
    .linkDistance(30)
    .size([w, h]);

  var vis = d3.select(selector).append('svg:svg')
      .attr('width', w)
      .attr('height', h);


  var node_filter_normal = function(d){
    return d.weight > MIN_WEIGHT || !!d.isRoot || !!d.isRelated;
  };

  var node_filter_large = function(d){
    return d.weight > MIN_WEIGHT * 20 || (!!d.isRoot || !!d.isRelated);
  };

  var link_filter_normal = function(d){
    return ((d.target.weight > MIN_WEIGHT && d.source.weight > MIN_WEIGHT) ||
       (!!d.target.isRoot || !!d.source.isRoot)
    );
  };

  var link_filter_large = function(d){
    return ((d.target.weight > MIN_WEIGHT * 100 || d.source.weight > MIN_WEIGHT * 100) &&
       (!!d.target.isRoot || !!d.source.isRoot)
    );
  };

  var node_filter = node_filter_normal;
  var link_filter = link_filter_normal;


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
          schema: r['schema.name'],
          isRelated: (r.source === graph.root || r.target === graph.root)
        });
        if (r.source === graph.root) {
          nodes[r.target].isRelated = true;
        }
        if (r.target === graph.root) {
          nodes[r.source].isRelated = true;
        }
      });

      nodes[graph.root].fixed = true;
      nodes[graph.root].isRoot = true;
      nodes[graph.root].x = w / 2;
      nodes[graph.root].y = h / 2;

      for (var nodeid in nodes) {
        nodes[nodeid].id = nodeid;
        nodeList.push(nodes[nodeid]);
        nodes[nodeid].index = nodeList.length - 1;
      }
      var addLink = function(nodeid) {
        return function(l){
          linkList.push({
            source: nodes[nodeid].index,
            target: nodes[l.target].index,
            schema: l.schema,
            isRelated: l.isRelated
          });
        };
      };
      for (var linknodeid in links) {
        links[linknodeid].forEach(addLink(linknodeid));
      }

      if (nodeList.length > 1500 && linkList.length > 1500) {
        console.log('big entity');
        // node_filter = node_filter_large;
        link_filter = link_filter_large;
      }

      update();
    });
  });

  function update() {
    var max_r = 20;
    var getRadius = function(d) {
      return d.isRoot ? 15 : Math.max(5, Math.min(max_r, Math.sqrt(d.weight * 4)));
    };

    var goodPos = [[w / 4, h / 3], [w * 3 / 4, h / 3]];

    force
        .gravity(0)
        .nodes(nodeList)
        .links(linkList)
        .start();

    nodeList = nodeList.filter(node_filter).map(function(d){
      var r = getRadius(d);
      if (r === max_r) {
        d.fixed = true;
        var pos = goodPos.pop();
        if (pos) {
          d.x = d.px = pos[0];
          d.y = d.py = pos[1];
        }
      }
      return d;
    });

    // Update the links…
    link = vis.selectAll('line.link')
        .data(linkList
           .filter(link_filter_normal)
        );

    // Enter any new links.
    link.enter().insert('svg:line', '.node')
        .attr('class', 'link')
        .attr('title', function(d){ return d.source.name + ' - ' + d.target.name; })
        .style('stroke', function(d) { return color(d.schema); });


    // Exit any old links.
    link.exit().remove();

    // Update the nodes…
    node = vis.selectAll('circle.node')
      .data(nodeList
      );

    var drag = force.drag()
      .on('dragstart', dragstart);

    node.
      enter().append('svg:circle')
        .classed('node', true)
        .classed('root', function(d){ return !!d.isRoot; })
        .classed('related', function(d){ return !d.isRoot; })
        // .classed('entity', function(d){ return !!d.isEntity; })
        // .attr('cx', function(d) { return d.x; })
        // .attr('cy', function(d) { return d.y; })
        .attr('r', getRadius)
        .attr('title', function(d){ return d.name; })
        // .style('fill', function(d){ return color(d.schema); })
        .on('click', click)
        .on('mouseover', function(d){
          var sel = d3.select(this);
          sel.moveToFront();
          var offset = $(selector).offset();
          var x = d.x + offset.left + 20;
          var y = d.y + offset.top  - 10;

          $(options.titleSelector)
            .text(d.name)
            .show()
            .css({'left': x + 'px', 'top': y + 'px'});
        })
        .on('mouseout', function(){
          $(options.titleSelector).hide();
        })
        .attr('cx', function(d) { return d.x; })
        .attr('cy', function(d) { return d.y; })
        .on('dblclick', dblclick)
        .call(drag);


    // Exit any old nodes.
    node.exit().remove();
  }
  force.on('tick', function() {
    link.attr('x1', function(d) { return d.source.x; })
        .attr('y1', function(d) { return d.source.y; })
        .attr('x2', function(d) { return d.target.x; })
        .attr('y2', function(d) { return d.target.y; });

    node.attr('cx', function(d) {
      d.x = Math.max(r, Math.min(w - r, d.x));
      return d.x;
    })
    .attr('cy', function(d) {
      d.y = Math.max(r, Math.min(h - r, d.y));
      return d.y;
    });
  });

  function click(d) {
    if (d3.event.shiftKey) {
      document.location.href = '/entities/' + d.id + '.html';
    }
  }

  function dblclick(d) {
    d3.select(this).classed("fixed", d.fixed = false);
  }

  function dragstart(d) {
    d3.select(this).classed("fixed", d.fixed = true);
  }

  $('#graph-search').keyup(function(){
    var val = $(this).val().toLowerCase();
    if (val) {
      nodeList.forEach(function(d){
        if (d.name.toLowerCase().indexOf(val) !== -1) {
          d.found = true;
        } else {
          d.found = false;
        }
      });
      
    } else {
      nodeList.forEach(function(d){
        d.found = false;
      });
    }
    node.classed('found', function(d){ return !!d.found; });
    vis.selectAll('.found').moveToFront();
  });

};