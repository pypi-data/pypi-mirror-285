import dash_mantine_components as dmc
from icore.vo import moeda, get_pt_br, get_tipo_de_colunas
from datetime import date, timedelta
from dash_iconify import DashIconify
from icore.vo import moeda
import dash_ag_grid as dag


class icmp:

    @staticmethod
    def tendencia(valor: float, titulo=None, id_acao=False, **props):

        valor = round(valor, 3)
        comparar = round(float(props.get("comparar", 0)), 3)
        id = props.get("id", "icmpTendencia")
        icon = props.get("icon", "gravity-ui:equal")
        color = props.get("color", "blue")
        titulo = titulo if titulo else ""
        diferenca = 0
        participacaoTitulo = " "
        participacao = 100
        width = props.get("width", 30)
        display = "hidden"

        btnAcao = dmc.ActionIcon(
            style={"display": "none"},
        )
        if id_acao != False:
            btnAcao = dmc.ActionIcon(
                DashIconify(icon="gg:details-more"),
                color="gray",
                variant="transparent",
                p=0,
                id=id_acao,
            )

        diferenca = round(valor - comparar, 3)
        if comparar > 0:
            participacao = (diferenca / comparar) * 100

        participacaoTitulo = f"{participacao:.2f}%"
        display = "block"
        if diferenca < 0:
            icon = "uil:arrow-down"
            color = "red"
            participacaoTitulo = f"Diferença: {moeda(diferenca)} ({participacao:.2f}%) "
        elif diferenca > 0:
            icon = "uil:arrow-up"
            color = "green"
            participacaoTitulo = f"Diferença: {moeda(diferenca)} ({participacao:.2f}%) "
        elif diferenca == 0.0:
            participacaoTitulo = " "
            icon = "gravity-ui:equal"
            color = "blue"

        return dmc.Card(
            [
                dmc.Indicator(
                    [
                        btnAcao,
                        dmc.Text(
                            moeda(valor),
                            id=id,
                            style={"font-size": "clamp(1rem, 4vw, 4rem)"},
                            ta="right",
                        ),
                        dmc.Text(
                            moeda(comparar),
                            id=id,
                            fw=400,
                            c="gray",
                            ta="right",
                            style={
                                "position": "absolute",
                                "top": 0,
                                "right": 16,
                                "marginTop": -10,
                                "display": display,
                            },
                        ),
                        dmc.Flex(
                            [
                                DashIconify(
                                    icon=icon,
                                    width=width,
                                    color=dmc.DEFAULT_THEME["colors"][color][7],
                                ),
                                dmc.Text(
                                    participacaoTitulo,
                                    fw=700,
                                ),
                            ],
                            justify={"base": "center", "sm": "center"},
                        ),
                        dmc.Text(
                            titulo,
                            ta="center",
                            style={"font-size": "clamp(1rem, 2vw, 2rem)"},
                        ),
                    ],
                    inline=True,
                    color=color,
                    size=16,
                    autoContrast=True,
                    processing=True,
                ),
            ],
            withBorder=True,
            radius="md",
            flex="1",
            miw=350,
            style={
                "borderColor": color,
            },
            # miw=350,
        )

    @staticmethod
    def periodo(**props):
        value = props.get(
            "value",
            [
                date.today() - timedelta(days=1),
                date.today() - timedelta(days=1),
            ],
        )

        return dmc.DatesProvider(
            children=dmc.DatePicker(
                allowSingleDateInRange=True,
                allowDeselect=True,
                required=True,
                clearable=True,
                persistence=True,
                valueFormat="DD/MM/YYYY",
                type="range",
                value=value,
                **props,
            ),
            settings={
                "locale": "pt_br",
                "firstDayOfWeek": 0,
                "weekendDays": [0],
            },
        )

    @staticmethod
    def select(**props):
        return dmc.MultiSelect(
            persistence=True,
            searchable=True,
            clearable=True,
            hidePickedOptions=True,
            flex=1,
            nothingFoundMessage="Nenhum resultado encontrado!",
            **props,
        )

    @staticmethod
    def table(pivot=False, sideBar=False, **props):
        dashGridOptionsPadrao = {
            "localeText": get_pt_br(),
            "dataTypeDefinitions": get_tipo_de_colunas(),
            "sideBar": sideBar,
        }
        props.setdefault("dangerously_allow_code", True)
        props.setdefault("persistence", True)
        props.setdefault(
            "defaultColDef",
            {
                "sortable": True,
                "filter": True,
                "resizable": True,
                "enableRowGroup": True,
            },
        )

        props.setdefault(
            "persisted_props",
            [
                "width",
                "sortIndex",
                "sort",
                "rowGroupIndex",
                "rowGroup",
                "pivotIndex",
                "columnState",
                "hide",
                "pivot",
                "pinned",
                "flex",
                "aggFunc",
                "sortModel",
                "filterModel",
                "groupState",
                "columnState",
                "columnGroupState",
            ],
        )
        props.setdefault("dashGridOptions", dashGridOptionsPadrao)
        props.setdefault("style", {"height": "100%", "width": "100%"})

        if pivot == True:
            dashGridOptionsPadrao = {
                "pivotMode": True,
                "defaultToolPanel": "none",
                "localeText": get_pt_br(),
                "dataTypeDefinitions": get_tipo_de_colunas(),
                "sideBar": sideBar,
            }

        return dag.AgGrid(
            enableEnterpriseModules=True,
            licenseKey="Using_this_{AG_Grid}_Enterprise_key_{AG-061904}_in_excess_of_the_licence_granted_is_not_permitted___Please_report_misuse_to_legal@ag-grid.com___For_help_with_changing_this_key_please_contact_info@ag-grid.com___{illimitar}_is_granted_a_{Multiple_Applications}_Developer_License_for_{1}_Front-End_JavaScript_developer___All_Front-End_JavaScript_developers_need_to_be_licensed_in_addition_to_the_ones_working_with_{AG_Grid}_Enterprise___This_key_has_been_granted_a_Deployment_License_Add-on_for_{1}_Production_Environment___This_key_works_with_{AG_Grid}_Enterprise_versions_released_before_{18_June_2025}____[v3]_[01]_MTc1MDIwMTIwMDAwMA==e5874f8693a092413271e9b6821a8c68",
            **props,
        )
