<%inherit file="base.mako"/>

<script src="../static/js/sorttable.js"></script>


<!-- https://www.w3schools.com/howto/howto_js_filter_table.asp -->
<script>
function filterFunc(input_id,col) {
  // Declare variables 
  var input, filter, table, tr, td, i;
  input = document.getElementById(input_id);
  filter = input.value.toUpperCase();
  table = document.getElementById("devices");
  tr = table.getElementsByTagName("tr");

  // Loop through all table rows, and hide those who don't match the search query
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[col];
    if (td) {
      if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    } 
  }
}
</script>


<h2>Devices</h2>
<p>You can filter devices below. You can sort them too.</p>

<table width=100%>
<tr>
  <td width=20%><input type="text" id="address" onkeyup="filterFunc('address',0)" placeholder="Filter address"></td>
  <td width=15%><input type="text" id="devtype" onkeyup="filterFunc('devtype',1)" placeholder="Filter devtypes"></td>
  <td width=15%><input type="text" id="name" onkeyup="filterFunc('name',2)" placeholder="Filter name"></td>
  <td width=15%><input type="text" id="info" onkeyup="filterFunc('info',3)" placeholder="Filter info"></td>
  <td width=35%><input type="text" id="attributes" onkeyup="filterFunc('attributes',4)" placeholder="Filter attribute"></td>
  </tr>
</table>
<table width=100% class="sortable" id="devices">
  <tr><th width=20%>Address</th><th width=15%>devtype</th><th width=15%>Name</th><th width=15%>Info</th><th width=35%>Attributes</th></tr>
  % for dev in devs:  
  <tr>
    <td><a href="./generic/${dev.address}"><tt>${dev.address}<tt></a></td>
    <td>${dev.dev_type}</td>
    <td><a href="./edit_metadata/${dev.address}">➠</a> ${dev.display_name}</td>
    %if 'info' in dev.description.keys():
       <td>${dev.description['info']}</td>
    %else:
       <td>--</td>
    %endif
    %if 'embedded' in dev.attributes.keys():
        <td>embedded</td>
    %else:
        <td><div data-is="raw-attrs" xaal_addr=${dev.address}></div></td>
    %endif
  </tr>
  % endfor
</table>

<script type="riot/tag" src="./static/tags/raw_attrs.tag"></script>