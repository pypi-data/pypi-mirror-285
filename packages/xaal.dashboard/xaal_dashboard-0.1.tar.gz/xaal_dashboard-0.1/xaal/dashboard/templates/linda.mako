<%inherit file="base.mako"/>
<%namespace name="widgets" file="widgets.mako" />

<link href="./static/css/btns.css" rel="stylesheet">

<div class="grid-background">
<div class="grid">

  <div class="grid-box">
    <b>QTRobot</b>
      ${widgets.list_devices_addr(['e0e9fa82-80c7-11eb-8400-a4badbf92501','e0e9fa82-80c7-11eb-8400-a4badbf92502',])}
  </div>

  
</div> <!-- end of grid -->
</div><!-- end of grib background -->

<script type="riot/tag" src="./static/tags/powerrelay.tag"></script>
<script type="riot/tag" src="./static/tags/powermeter.tag"></script>


<script type="riot/tag" src="./static/tags/generic_attrs.tag"></script>
<script type="riot/tag" src="./static/tags/clock.tag"></script>
