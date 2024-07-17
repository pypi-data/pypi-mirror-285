<%
    menu = [('devices'   ,'Elements'),
            ('grid'      ,'Dashboard'),
           ]
%>
   
<!-- Menu -->
  <ul class="menu">
    <li><a href="#" onclick="openNav()">&#9776;</a></li>     
% for item in menu:
%   if item[0] == active_menu:    
        <li class="active"><a href="/${item[0]}">${item[1]}</a></li>
%   else:
        <li><a href="/${item[0]}">${item[1]}</a></li>
%   endif
        
% endfor
  </ul>
<!-- EOF Menu -->
