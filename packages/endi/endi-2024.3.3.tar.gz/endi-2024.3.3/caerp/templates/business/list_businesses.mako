<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/utils.mako" import="format_text" />
<%namespace file="/base/utils.mako" import="company_list_badges"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='content'>

${searchform()}

<div>
    <div>
        ${records.item_count} Résultat(s)
    </div>
    <div class="align_right">
        <small>Les montants sont exprimés TTC</small>
    </div>
    <div class='table_container'>
        <table class="hover_table">
            % if is_admin:
                <% nb_columns = 10 %>
                <% total_colspan = 5 %>
            % else:
                <% nb_columns = 9 %>
                <% total_colspan = 4 %>
            % endif
            % if records:
            <thead>
                <tr>
                    <th scope="col" class="col_status" title="Statut"><span class="screen-reader-text">Statut</span></th>
                    <th scope="col" class="col_text">Intitulé de l'affaire</th>
                    % if is_admin:
                        <th scope="col" class="col_text">Enseigne</th>
                    % endif
                    <th scope="col" class="col_text">Client</th>
                    <th scope="col" class="col_text">Documents</th>
                    <th scope="col" class="col_number">Devisé</th>
                    <th scope="col" class="col_number">Facturé</th>
                    <th scope="col" class="col_number">À facturer</th>
                    <th scope="col" class="col_number">Restant dû</th>
                    <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
                </tr>
            </thead>
            % endif
            <tbody>
            % if records:
                <% total_estimated = sum(record.get_total_estimated('ttc') for id_, record in records) %>
                <% total_invoiced = sum(record.get_total_income('ttc') for id_, record in records) %>
                <% total_to_invoice = sum(record.amount_to_invoice('ttc') for id_, record in records) %>
                <% total_to_pay = sum(record.get_topay() for id_, record in records) %>
                <tr class="row_recap">
                    <th scope='row' colspan='${total_colspan}' class='col_text'>Total</th>
                    <th class='col_number'>${api.format_amount(total_estimated, precision=5)}&nbsp;€</th>
                    <th class='col_number'>${api.format_amount(total_invoiced, precision=5)}&nbsp;€</th>
                    <th class='col_number'>${api.format_amount(total_to_invoice, precision=5)}&nbsp;€</th>
                    <th class='col_number'>${api.format_amount(total_to_pay, precision=5)}&nbsp;€</th>
                    <th scope='row' class='col_text'></th>
                </tr>
                % for id_, record in records:
                    <% url = request.route_path('/businesses/{id}', id=record.id) %>
                    <% onclick = "document.location='{url}'".format(url=url) %>
                    <% tooltip_title = "Cliquer pour voir l'affaire « " + record.name + " »" %>
                    <tr>
                        <td class="col_status"
                        % if record.status == 'success':
                            title="${tooltip_title}"
                        % else:
                            title="Des éléménts sont manquants - ${tooltip_title}"
                        % endif
                        onclick="${onclick}"
                        >
                            <span class='icon status ${record.status}'>
                                <svg><use href="${request.static_url('caerp:static/icons/endi.svg')}#${record.status}"></use></svg>
                            </span>
                        </td>
                        <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                            ${record.name | n}<br/>
                            <small>${record.business_type.label}</small>
                        </td>
                        % if is_admin:
                            <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                                <% company = record.project.company %>
                                <% company_url = request.route_path('/companies/{id}', id=company.id) %>
                                % if request.has_permission('view.company', company):
                                    <a href="${company_url}" title="Cliquer pour voir l'enseigne « ${company.name} »" aria-label="Cliquer pour voir l'enseigne « ${company.name} »">${company.full_label | n}</a>
                                    % if request.has_permission('admin_company', company):
                                        ${company_list_badges(company)}
                                    % endif
                                % else:
                                    ${company.full_label | n}
                                % endif
                            </td>
                        % endif
                        <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                            % if record.tasks:
                                <% customer = record.tasks[0].customer %>
                                <% customer_url = request.route_path('customer', id=customer.id) %>
                                <a href="${customer_url}" title="Cliquer pour voir le client « ${customer.label} »" aria-label="Cliquer pour voir le client « ${customer.label} »">${customer.label}</a>
                            % else:
                                <em>Cette affaire est vide</em>
                            % endif
                        </td>
                        <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                            % if record.tasks:
                                <ul>
                                % for t in (t for t in record.tasks if t.status == "valid"):
                                    % if t.official_number:
                                        <% task_name = t.official_number %>
                                    % else:
                                        <% task_name = t.internal_number %>
                                    % endif
                                    <li><a href="${api.task_url(t)}" title="${task_name}" aria-label="${task_name}">${task_name}</a></li>
                                % endfor
                                </ul>
                            % else:
                                <em>Cette affaire est vide</em>
                            % endif
                        </td>
                        <td class="col_number" onclick="${onclick}" title="${tooltip_title}">
                            ${api.format_amount(record.get_total_estimated('ttc'), precision=5)}&nbsp;€
                        </td>
                        <td class="col_number" onclick="${onclick}" title="${tooltip_title}">
                            ${api.format_amount(record.get_total_income('ttc'), precision=5)}&nbsp;€
                        </td>
                        <td class="col_number" onclick="${onclick}" title="${tooltip_title}">
                            ${api.format_amount(record.amount_to_invoice('ttc'), precision=5)}&nbsp;€
                        </td>
                        <td class="col_number" onclick="${onclick}" title="${tooltip_title}">
                            ${api.format_amount(record.get_topay(), precision=5)}&nbsp;€
                        </td>
                        ${request.layout_manager.render_panel('action_buttons_td', links=stream_actions(record))}
                    </tr>
                % endfor
                <tr class="row_recap">
                    <th scope='row' colspan='${total_colspan}' class='col_text'>Total</th>
                    <th class='col_number'>${api.format_amount(total_estimated, precision=5)}&nbsp;€</th>
                    <th class='col_number'>${api.format_amount(total_invoiced, precision=5)}&nbsp;€</th>
                    <th class='col_number'>${api.format_amount(total_to_invoice, precision=5)}&nbsp;€</th>
                    <th class='col_number'>${api.format_amount(total_to_pay, precision=5)}&nbsp;€</th>
                    <th scope='row' class='col_text'></th>
                </tr>
            % else:
                <tr>
                    <td colspan="${nb_columns}" class="col_text"><em>Aucune affaire correspondant à ces critères</em></td>
                </tr>
            % endif
            </tbody>
        </table>
    </div>
    ${pager(records)}
</div>
</%block>
