## -*- coding: utf-8; -*-

<form action="${form.action_url}" method="GET" @submit.prevent="applyFilters()">

  <div style="display: flex; flex-direction: column; gap: 0.5rem;">
    <grid-filter v-for="key in filtersSequence"
                 :key="key"
                 :filter="filters[key]"
                 ref="gridFilters">
    </grid-filter>
  </div>

  <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">

    <b-button type="is-primary"
              native-type="submit"
              icon-pack="fas"
              icon-left="check">
      Apply Filters
    </b-button>

    <b-button v-if="!addFilterShow"
              icon-pack="fas"
              icon-left="plus"
              @click="addFilterInit()">
      Add Filter
    </b-button>

    <b-autocomplete v-if="addFilterShow"
                    ref="addFilterAutocomplete"
                    :data="addFilterChoices"
                    v-model="addFilterTerm"
                    placeholder="Add Filter"
                    field="key"
                    :custom-formatter="formatAddFilterItem"
                    open-on-focus
                    keep-first
                    icon-pack="fas"
                    clearable
                    clear-on-select
                    @select="addFilterSelect">
    </b-autocomplete>

    <b-button @click="resetView()"
              icon-pack="fas"
              icon-left="home">
      Default View
    </b-button>

    <b-button @click="clearFilters()"
              icon-pack="fas"
              icon-left="trash">
      No Filters
    </b-button>

    % if allow_save_defaults and request.user:
        <b-button @click="saveDefaults()"
                  icon-pack="fas"
                  icon-left="save"
                  :disabled="savingDefaults">
          {{ savingDefaults ? "Working, please wait..." : "Save Defaults" }}
        </b-button>
    % endif

  </div>

</form>
