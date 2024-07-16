<generic-attrs>

<div class="generic-attrs">
<table width=100%>
  <tr><th>Name</th><th>value</th></tr>
  <tr each="{ value, key in attributes }">
    <td>{ key }</td>
    <td>{ value == null ? 'null' : value.toString()}</td>
  </tr>
</table>
</div>


<script>
  this.addr = opts.xaal_addr
  this.attributes = []

  receive(data) {
    this.attributes = data['attributes']
    this.update()
//     obj = this.attributes
//     Object.keys(obj).map((e) => console.log(`key=${e}  value=${obj[e]}`))
  }
</script>
</generic-attrs>
