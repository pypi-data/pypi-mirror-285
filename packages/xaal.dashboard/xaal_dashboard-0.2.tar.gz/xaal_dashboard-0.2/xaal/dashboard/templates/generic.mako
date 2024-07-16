<%inherit file="base.mako"/>


<table width=100%>
<tr valign=top><td>
<h2>Information</h2>
<table width=100%>
  <tr><th>Name</th><th>value</th></tr>
  <tr><td>address</td><td>${dev.address}</td></tr>
  <tr><td>dev_type</td><td>${dev.dev_type}</td></tr>
</table>
</td>
<td>
<h2>Description</h2>
<table width=100%>
  <tr><th>Name</th><th>value</th></tr>
% for k in dev.description:
<%
    value = dev.description[k]
    if not value:
        continue
%>
  <tr><td>${k}</td><td>${value}</td></tr>
% endfor
</table>
</td></tr>
</table>

<h2>Attributes</h2>
<div data-is="generic-attrs" xaal_addr="${dev.address}"></div>
<script type="riot/tag" src="../static/tags/generic_attrs.tag"></script>

<h2>Meta Data</h2>
<table width=100%>
  <tr><th>key</th><th>value</th></tr>
% for k in dev.db:
  <tr><td>${k}</td><td>${dev.db[k]}</td></tr>
% endfor   
</table>
<a href="../edit_metadata/${dev.address}">Edit meta-data</a>
