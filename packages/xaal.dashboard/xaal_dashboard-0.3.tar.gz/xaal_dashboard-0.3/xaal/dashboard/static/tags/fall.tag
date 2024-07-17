<fall>

<table width=80%>
  <tr>
    <td>
      <span class="motion">
        <span class="{class}">⚛</span>
      </span> 
    </td>
    <td>
      <span class="X"> X : { X }</span><br/>
      <span class="Y"> Y : { Y }</span><br/>
      <span class="Delay"> Delay : {Delay}&nbsp;s</span><br/>
    </td>
  </tr>
</table>

<script>
  this.addr = opts.xaal_addr
  this.X = null;
  this.Y = null;
  this.Delay = null;
  this.class = "no_motion"

  receive(data) {
    this.Delay = data['attributes']['Delay (s)']
    this.X = data['attributes']['X'];
    this.Y = data['attributes']['Y'];
    if (data.attributes['fall'] == true) {
       this.class = 'motion'
    }
    else {
        this.class = 'no_motion'
    }
    this.update()
  }
</script>

<style>
. {
    font-weight: bold;
    color : var(--color1);
}

.motion {
    font-weight: bold;
    color : var(--color3);
}

.no_motion {
    font-weight: bold;
    color : var(--color2);
    align: center;}

table, tr {border:hidden;}
td, th {border:hidden;}

motion.span {
  min-height: 100px;
  display: inline-flex;
  align-items: center;
}

fall.span {
  text-align: right;
}

</style>

</fall>


