<door>

<span class="door">
  <span class="{class}">⚛</span>
</span>


<script>
  this.addr = opts.xaal_addr;
  this.class = 'close';
    
  receive(data) {
    state = data['attributes']['position'];
    if (state == true) {
       this.class = 'open'
    }
    else {
        this.class = 'close'
    }
    this.update();
  }
</script>

<style>
.open {
    font-weight: bold;
    color : var(--color3);
    align: center;
}

.close {
    font-weight: bold;
    color : var(--color2);
    align: center;
}
    
</style>

</door>
