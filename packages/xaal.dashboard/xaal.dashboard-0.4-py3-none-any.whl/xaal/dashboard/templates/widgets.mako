<%def name="thermometer(addr)">
<a href="./warp10/graph/${addr}">
  <div data-is="thermometer" xaal_addr=${addr}></div>
</a>
</%def>

<%def name="hygrometer(addr)">
<a href="./warp10/graph/${addr}">
  <div data-is="hygrometer" xaal_addr=${addr}></div>
</a>
</%def>

<%def name="powerrelay(addr)">
  <div data-is="powerrelay" xaal_addr=${addr}></div>
</%def>

<%def name="lamp(addr)">
  <div data-is="lamp" xaal_addr=${addr}></div>
</%def>


<%def name="lamp_color(addr)">
  <div data-is="lamp_color" xaal_addr=${addr}></div>
</%def>


<%def name="generic(addr)">
  <div data-is="generic-attrs" xaal_addr=${addr}></div>
</%def>


<%def name="powermeter(addr)">
<a href="./warp10/graph/${addr}">
  <div data-is="powermeter" xaal_addr=${addr}></div>
</a>
</%def>

<%def name="barometer(addr)">
<a href="./warp10/graph/${addr}">
  <div data-is="barometer" xaal_addr=${addr}></div>
</a>
</%def>

<%def name="co2meter(addr)">
<a href="./warp10/graph/${addr}">
  <div data-is="co2meter" xaal_addr=${addr}></div>
</a>
</%def>


<%def name="luxmeter(addr)">
<a href="./warp10/graph/${addr}">
  <div data-is="luxmeter" xaal_addr=${addr}></div>
</a>
</%def>


<%def name="motion(addr)">
  <div data-is="motion" xaal_addr=${addr}></div>
</%def>

<%def name="door(addr)">
  <div data-is="door" xaal_addr=${addr}></div>
</%def>


<%def name="contact(addr)">
  <div data-is="contact" xaal_addr=${addr}></div>
</%def>


<%def name="shutter(nickname)">
<% dev = devices.fetch_one_kv('nickname',nickname) %>
% if dev:
  <b>${dev.display_name}</b>
  <span data-is="shutter" xaal_addr=${dev.address}></span>
% else:
  device not found: <b>${nickname}</b>
% endif
</%def>


<%!
  def tag(dev):
      type_ = dev.dev_type
      if type_.startswith('thermometer.')   : return 'thermometer'
      if type_.startswith('hygrometer.')    : return 'hygrometer'
      if type_.startswith('shutter.')       : return 'shutter'
      if type_.startswith('lamp.color')     : return 'lamp_color'
      if type_.startswith('lamp.')          : return 'lamp'
      if type_.startswith('powerrelay.')    : return 'powerrelay'
      if type_.startswith('powermeter.')    : return 'powermeter'
      if type_.startswith('barometer.')     : return 'barometer'
      if type_.startswith('co2meter.')      : return 'co2meter'
      if type_.startswith('motion.')        : return 'motion'  
      if type_.startswith('door.')          : return 'door'
      if type_.startswith('contact.')       : return 'contact'
      if type_.startswith('luxmeter.')      : return 'luxmeter'
      return 'generic'
%>


<%def name="device(nickname)">
<% dev = devices.fetch_one_kv('nickname',nickname) %>
% if dev:
    ${ self.template.get_def(tag(dev)).render(dev.address) } 
% else:
     Device not found ${nickname}
% endif
</%def>

<%def name="device_addr(addr)">
<%
	uuid = tools.get_uuid(addr)
	dev = devices.get_with_addr(uuid)
%>
% if dev:
     ${ self.template.get_def(tag(dev)).render(dev.address) }
% else:
     Device not found [${addr}]
% endif
</%def>


<%def name="list_devices(values)">
<table width=98%>
% for nick in values:
<% dev = devices.fetch_one_kv('nickname',nick) %>
% if dev:
<tr>
  <td><a href="./generic/${dev.address}">➠</a>${dev.display_name}</td>
  <td>${ self.template.get_def(tag(dev)).render(dev.address) }</td>
</tr>
% endif
% endfor
</table>
</%def>


<%def name="list_all_devices()">
<table width=98% border=1>
% for dev in devices:
% if tag(dev)!= 'generic':
<tr>
  <td><a href="./generic/${dev.address}">➠</a>${dev.display_name}</td>
  <td>${self.template.get_def(tag(dev)).render(dev.address) }</td>
</tr>
% endif
% endfor
</table>
</%def>


<%def name="list_devices_addr(values)">
<table width=98%>
% for addr in values:
<%
	uuid = tools.get_uuid(addr)
	dev = devices.get_with_addr(uuid)
%>
% if dev:
<tr>
  <td><a href="./generic/${dev.address}">➠</a>${dev.display_name}</td>
  <td>${ self.template.get_def(tag(dev)).render(dev.address) }</td>
</tr>
% endif
% endfor
</table>
</%def>

