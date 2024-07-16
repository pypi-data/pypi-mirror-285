<%inherit file="base.mako"/>


<h2>Meta Data</h2>

<form method=post>
<table width=100%>
  <tr><th>key</th><th>value</th></tr>
% for k in dev.db:
  <tr><td><input name="key_${loop.index}" value="${k}"></td><td><input name="value_${loop.index}" value="${dev.db[k]}"</td></tr>
% endfor   
  <tr><td><input name="key_add1"></td><td><input name="value_add1"></td></tr>
  <!--<tr><td><input name="key_add2"></td><td><input name="value_add2"></td></tr>-->
</table>
<input type="submit" value="Save">
</form>