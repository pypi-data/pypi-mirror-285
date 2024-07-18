## -*- coding: utf-8; -*-

<%def name="app_title()">${rattail_app.get_node_title()}</%def>

<%def name="global_title()">${"[STAGE] " if not request.rattail_config.production() else ''}${self.app_title()}</%def>

<%def name="extra_styles()"></%def>

<%def name="favicon()">
  <link rel="icon" type="image/x-icon" href="${request.rattail_config.get('tailbone', 'favicon_url', default=request.static_url('tailbone:static/img/rattail.ico'))}" />
</%def>

<%def name="header_logo()">
  ${h.image(request.rattail_config.get('tailbone', 'header_image_url', default=request.static_url('tailbone:static/img/rattail.ico')), "Header Logo", style="height: 49px;")}
</%def>

<%def name="footer()">
  <p class="has-text-centered">
    powered by ${h.link_to("Rattail", url('about'))}
  </p>
</%def>
