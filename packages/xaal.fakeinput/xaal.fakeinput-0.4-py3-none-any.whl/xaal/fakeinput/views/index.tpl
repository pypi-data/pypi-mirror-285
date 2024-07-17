<html>
<head>
  <title>xAAL Fake buttons, switches, contacts</title>
  <script type="text/javascript" src="/static/jquery.min.js"></script>
  <script type="text/javascript" src="/static/site.js"></script>
  <link rel=stylesheet type="text/css" href="/static/style.css">
<body>
<h1>xAAL Fake buttons, switches, contacts</h1>

<table>
<tr><th>Addr</th><th>Type</th><th>Name</th><th>Actions</th></tr>
  % for d in devices:
    <tr>
      <td>{{d.dev.address}}</td>
      <td>{{d.dev.dev_type}}</td>
      <td>{{d.name}}</td>

    % if (d.dev.dev_type == 'button.basic'):
      <td>
        <button class="button ripple" onClick="on_click(this)" xaal-addr="{{d.dev.address}}">Click</button>
        <button class="button ripple" onClick="on_dclick(this)" xaal-addr="{{d.dev.address}}">DClick</button>
      </td>
    % end

    % if (d.dev.dev_type in ['switch.basic','contact.basic','motion.basic']):
    <td>
      <label class="switch"><input type="checkbox" onClick="on_toggle(this)" {{d.state}} xaal-addr="{{d.dev.address}}">
      <span class="slider round"></span>
      </label>
    </td>
    % end
    </tr>
  % end
</table>

</body>
</html>
