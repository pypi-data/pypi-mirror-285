<%inherit file="base.mako"/>
<%namespace name="widgets" file="widgets.mako" />

<link href="./static/css/btns.css" rel="stylesheet">

<div class="grid-background">
<div class="grid">

  <div class="grid-box">
    <b>Light</b>
      ${widgets.list_devices(['lamp_entree','lamp_couloir','lamp_salon','lamp_ambiance','aqara_gw'])}
  </div>

  <div class="grid-box">
    <b>Light</b>
      ${widgets.list_devices(['lamp_salle','lamp_cuisine','lamp_sdb','relay_spot'])}      
  </div>

  <div class="grid-box">
    <b>Powerrelay</b>
      ${widgets.list_devices(['relay_wifi','relay_bouilloire','relay_1','relay_2','relay_3','sonoff_l1','sonoff_l2'])}
  </div>


  <div class="grid-box">
    <b>Powerrelay</b>
      ${widgets.list_devices(['green_1r','green_2r','green_3r','green_4r','green_5r','green_6r'])}
  </div>

  <div class="grid-box">   
    <div style="text-align:center;">
     ${widgets.shutter('shutter_cuisine')}
    </div>
  </div>
  
  <div class="grid-box">
    <div style="text-align:center;">
     ${widgets.shutter('shutter_sdb')}
    </div>
  </div>

  <div class="grid-box">
    <b>Temperature</b>
    ${widgets.list_devices(['temp_netatmo','temp_owm','temp_bureau',])}
  </div>

  <div class="grid-box">
    <b>Humidity</b>
    ${widgets.list_devices(['rh_netatmo','rh_owm','rh_bureau'])}
  </div>


  <div class="grid-box">
    <b>Aquara</b>
    ${widgets.list_devices(['temp_aqara1','rh_aqara1','press_aqara1'])}
    ${widgets.list_devices(['temp_aqara2','rh_aqara2','press_aqara2'])}    
  </div>

  
  <div class="grid-box">
    <b>Contact</b>
    ${widgets.list_devices(['door1','door5','window1','window2'])}
  </div>


<div class="grid-box">
    <b>Contact</b>
    ${widgets.list_devices(['door2','door4','drawer1','drawer2','drawer3'])}
  </div>


  
  <div class="grid-box">
    <b>Power</b>
    ${widgets.list_devices(['pmeter_spot','pmeter_robot','pmeter_bouilloire','pmeter_1','pmeter_2','pmeter_3','pmeter_qtrobot'])}
  </div>

  <div class="grid-box">
    <b>Power</b>
    ${widgets.list_devices(['multi_pmeter1','multi_pmeter2','multi_pmeter3'])}
  </div>


  <div class="grid-box">
    <b>Power</b>
      ${widgets.list_devices(['green_1p','green_2p','green_3p','green_4p','green_5p','green_6p'])}
  </div>

  
  <div class="grid-box">
    <b>Motion</b>
    ${widgets.list_devices(['motion1','motion2','motion3','motion4','motion5'])}
  </div>
  
  <div class="grid-box">
    <b>CO2</b>
    ${widgets.list_devices(['co2_1','co2_2','co2_3','co2_4'])}
  </div>


  <div class="grid-box">
    <b>DTX</b>
    ${widgets.list_devices(['dtx_fauteuil','dtx_lit','dtx_robinet1','dtx_robinet2','btn_sonnette'])}
  </div>


  <div class="grid-box">
    <b>Zones</b>
    ${widgets.list_devices(['sf_1','sf_2','sf_3','sf_4','sf_5','sf_6'])}
  </div>



<!--

  <div class="grid-box">
    <b>TP</b>
    ${widgets.list_devices_addr(['dd1ccf22-8be1-11eb-ba36-0800279d8887','dd1cccac-8be1-11eb-ba36-0800279d8887','214c657a-80ea-11eb-8377-73dda5022638'])}
  </div>

  <div class="grid-box two">
  <b>Activity</b>
  ${widgets.device_addr('40e7df66-dd9e-11eb-9c34-509a4c5add63')} 
  </div>

  <div class="grid-box two">
  <b>IR Cam</b>
  ${widgets.device_addr('a2e5b57c-da8c-11eb-88bf-29e1f24a3566')}
  </div>

  <div class="grid-box two">
  <b>Xsens</b>
  ${widgets.device_addr('db206d28-da87-11eb-8902-509a4c5add63')}
  </div>

  <div class="grid-box two">
  <b>Fish Eye</b>
  ${widgets.device_addr('5a72250e-db0a-11eb-a785-1e00a23e8a62')} 
  </div>

-->



<!-- 
  <div class="grid-box two">
    <b>ZM100</b>
    ${widgets.device_addr('52351a1e-8c3c-11e9-a4af-b827ebe99203')}
    ${widgets.device_addr('52351a1e-8c3c-11e9-a4af-b827ebe99206')}
    ${widgets.list_devices_addr(['52351a1e-8c3c-11e9-a4af-b827ebe99201','52351a1e-8c3c-11e9-a4af-b827ebe99202',])}
  </div>
    

<div class="grid-box two">
  <div style="text-align:center;">
    <iframe src="https://aal.enstb.org/grafana/d-solo/mNvuqkJmz/xaal-lab?refresh=5s&panelId=24&orgId=1" width="310" height="100" frameborder="0"></iframe>
    <iframe src="https://aal.enstb.org/grafana/d-solo/mNvuqkJmz/xaal-lab?refresh=1m&panelId=27&orgId=1" width="310" height="100" frameborder="0"></iframe>    
  </div>
 </div>
 
  
  <div class="grid-box two" style="align:center;">
    	<img src="http://10.77.3.51/video3.mjpg" width=250>
  </div>
  
  
  <div class="grid-box" style="text-align:center;">
    <br/><br/><br/>
      <span data-is="clock"/>
  </div>
-->

  
</div> <!-- end of grid -->
</div><!-- end of grib background -->


<script type="riot/tag" src="./static/tags/lamp_color.tag"></script>
<script type="riot/tag" src="./static/tags/powerrelay.tag"></script>
<script type="riot/tag" src="./static/tags/hygrometer.tag"></script>
<script type="riot/tag" src="./static/tags/thermometer.tag"></script>
<script type="riot/tag" src="./static/tags/powermeter.tag"></script>
<script type="riot/tag" src="./static/tags/lamp.tag"></script>
<script type="riot/tag" src="./static/tags/shutter.tag"></script>
<script type="riot/tag" src="./static/tags/barometer.tag"></script>
<script type="riot/tag" src="./static/tags/co2meter.tag"></script>
<script type="riot/tag" src="./static/tags/motion.tag"></script>
<script type="riot/tag" src="./static/tags/door.tag"></script>
<script type="riot/tag" src="./static/tags/contact.tag"></script>


<script type="riot/tag" src="./static/tags/generic_attrs.tag"></script>
<script type="riot/tag" src="./static/tags/clock.tag"></script>
