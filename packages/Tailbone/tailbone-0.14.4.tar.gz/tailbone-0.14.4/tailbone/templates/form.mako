## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="object_helpers()"></%def>

<%def name="render_form_buttons()"></%def>

<%def name="render_form_template()">
  ${form.render_deform(buttons=capture(self.render_form_buttons))|n}
</%def>

<%def name="render_form()">
  <div class="form">
    ${form.render_vuejs_component()}
  </div>
</%def>

<%def name="page_content()">
  % if main_form_collapsible:
      <${b}-collapse class="panel"
                     % if request.use_oruga:
                         v-model:open="mainFormPanelOpen"
                     % else:
                         :open.sync="mainFormPanelOpen"
                     % endif
                     >
        <template #trigger="props">
          <div class="panel-heading"
               role="button"
               style="cursor: pointer;">

            ## TODO: for some reason buefy will "reuse" the icon
            ## element in such a way that its display does not
            ## refresh.  so to work around that, we use different
            ## structure for the two icons, so buefy is forced to
            ## re-draw

            <b-icon v-if="props.open"
                    pack="fas"
                    icon="caret-down">
            </b-icon>

            <span v-if="!props.open">
              <b-icon pack="fas"
                      icon="caret-right">
              </b-icon>
            </span>

            &nbsp;
            <strong>${main_form_title}</strong>
          </div>
        </template>
        <div class="panel-block">
          <div class="form-wrapper">
            <br />
            ${self.render_form()}
          </div>
        </div>
      </${b}-collapse>
  % else:
      <div class="form-wrapper">
        <br />
        ${self.render_form()}
      </div>
  % endif
</%def>

<%def name="render_this_page()">
  <div style="display: flex; justify-content: space-between;">

    <div class="this-page-content">
      ${self.page_content()}
    </div>

    <div style="display: flex; align-items: flex-start;">

      ${before_object_helpers()}

      <div class="object-helpers">
        ${self.object_helpers()}
      </div>

      <ul id="context-menu">
        ${self.context_menu_items()}
      </ul>
    </div>

  </div>
</%def>

<%def name="before_object_helpers()"></%def>

<%def name="render_this_page_template()">
  % if form is not Undefined:
      ${self.render_form_template()}
  % endif
  ${parent.render_this_page_template()}
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  % if main_form_collapsible:
      <script>
        ThisPageData.mainFormPanelOpen = ${'false' if main_form_autocollapse else 'true'}
      </script>
  % endif
</%def>

<%def name="finalize_this_page_vars()">
  ${parent.finalize_this_page_vars()}
  % if form is not Undefined:
      <script type="text/javascript">

        ${form.component_studly}.data = function() { return ${form.component_studly}Data }

        Vue.component('${form.component}', ${form.component_studly})

      </script>
  % endif
</%def>


${parent.body()}
