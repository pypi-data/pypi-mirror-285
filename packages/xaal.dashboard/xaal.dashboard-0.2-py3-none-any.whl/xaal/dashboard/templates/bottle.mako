<%inherit file="base.mako"/>


<div class="content">

  <h1>HTTP Information</h1>

  <h2>Headers</h2>
  <table>
    <tr><th>Key</th><th>value</th></tr>
    % for k in headers:
    <tr><td>${k}</td><td>${headers[k]|h}</td></tr>
    % endfor
  </table>

  <h2>Query</h2>
  <table>
    <tr><th>Key</th><th>value</th></tr>
% for k in query:
    <tr><td>${k}</td><td>${query[k]|h}</td></tr>
% endfor
  </table>

  <h2>Environ</h2>
  <table>
    <tr><th>Key</th><th>value</th></tr>
% for k in environ:
    <tr><td>${k}</td><td>${environ[k]|h}</td></tr>
% endfor
  </table>
  
  <h2>User profile</h2>
  ${profile}
</div>
