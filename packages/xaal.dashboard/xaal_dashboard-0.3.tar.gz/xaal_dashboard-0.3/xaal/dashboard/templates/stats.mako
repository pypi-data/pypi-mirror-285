<%inherit file="base.mako"/>


<div class="content">

  <h1>Devices stats</h1>
  <div>Uptime: <b>${uptime}</b></div>
  <div>Total found devices : <b>${total}</b></div><br/>
  <table>
    <tr><th>Dev_types</th><th>counter</th></tr>
    % for dt in dev_types:
    <tr><td>${dt}</td><td>${dev_types[dt]}</td></tr>
    % endfor
    </table>
</div>
