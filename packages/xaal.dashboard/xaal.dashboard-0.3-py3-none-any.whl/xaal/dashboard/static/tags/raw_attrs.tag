<raw-attrs>

<div class="raw-attrs">
  <div each="{ value, key in attributes }">{ key }: { value == null ? 'null' : value.toString()}</div>
</div>


<script>
  this.addr = opts.xaal_addr
  this.attributes = []

  receive(data) {
    this.attributes = data['attributes']
    this.update()
  }
</script>
</raw-attrs>
