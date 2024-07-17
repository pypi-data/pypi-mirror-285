  <!-- Side Menu -->
  <div id="mySidenav" class="sidenav">
    <a href="javascript:void(0)" class="closebtn" onclick="closeNav()">&times;</a>
      % for item in menu.get():
      <li><a href="${item['url']}">${item['value']}</a></li>
      % endfor
  </div>
