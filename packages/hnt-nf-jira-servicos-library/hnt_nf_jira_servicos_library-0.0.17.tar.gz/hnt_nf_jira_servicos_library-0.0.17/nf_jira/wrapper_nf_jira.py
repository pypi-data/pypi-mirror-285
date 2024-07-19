import requests
import locale

from .entities.nota_servico import NotaServico
from .entities.miro import Miro
from .entities.fatura import Fatura
from .entities.constants import *

from .entities.classes.form_jira import FormJira
from .entities.classes.issue_jira import (
    IssueJira,
    AttachmentJira,
    TransitionJira,
    CommentJira,
)

from .entities.classes.issue_fields import IssueFields
from .entities.classes.helper import JiraFieldsHelper, JsonHelper, GuiandoHelper
from .entities.classes.n8n_domain import N8NDomain
from .entities.classes.factories import Factories


class wrapper_jira:

    def __init__(self, miro_is_active=False, debug=False):
        locale.setlocale(locale.LC_ALL, ("pt_BR.UTF-8"))
        self._test_mode = debug
        self._miro_is_active = miro_is_active
        self._instance_class()
        pass

    def _instance_class(self):
        self.FormJira = FormJira()
        self.IssueJira = IssueJira()
        self.AttachmentJira = AttachmentJira()
        self.TransitionJira = TransitionJira()
        self.CommentJira = CommentJira()
        self.JiraFieldsHelper = JiraFieldsHelper()
        self.GuiandoHelper = GuiandoHelper()
        self.JsonHelper = JsonHelper()
        self.IssueFields = IssueFields()
        self.N8NDomain = N8NDomain()
        self.Factories = Factories()
        pass

    def get_document_by_issue(self, issue_key):


        issue = self._get_issue_by_key(issue_key)
        issue_sap_json = {
            "jira_info": issue["jira_info"],
        }
        issue_transition = issue_sap_json["jira_info"]["transition_type"]

        if issue_transition == SAP_NOTA_FISCAL:
            nota_pedido_factory = self.Factories.nota_pedido_servico_factory(issue)
            nota_pedido_model = NotaServico(**nota_pedido_factory).model_dump()
            issue_sap_json["nota_pedido"] = nota_pedido_model

            if self._miro_is_active:
                miro_factory = self.Factories.miro_factory(issue)
                miro_model = Miro(**miro_factory).model_dump()
                issue_sap_json["miro"] = miro_model

        elif issue_transition == SAP_FATURA:
            fatura_factory = self.Factories.fatura_factory(issue)
            fatura_model = Fatura(**fatura_factory).model_dump()
            issue_sap_json["fatura"] = fatura_model

        if self._test_mode:
            for json in issue_sap_json:
                self.JsonHelper.save_json(f"{json}_{issue_key}", issue_sap_json[json])
            self.JsonHelper.save_json(f"sap_model_{issue_key}", issue_sap_json)

        return issue_sap_json

    def _get_issue_by_key(self, issue_key):

        issue_json = self._get_nf_jira(issue_key)

        issue_attachment = issue_json["model_data"]
        jira_info = issue_json["jira_info"]

        centro_domain = (
            self.N8NDomain.get_nf_domain(
                CENTRO_N8N_DOMAIN, issue_attachment[CNPJ_DO_CLIENTE]
            )
        )
        domain = {"centro": centro_domain, "sap_service": None}
        if issue_attachment[CODIGO_SAP_SERVICO] is not None:
            domain['sap_service'] = (
                self.N8NDomain.get_nf_sap_domain(
                    issue_attachment[CODIGO_SAP_SERVICO][0]
                )
            )

        issue = {
            "issue_data": issue_json["issue_data"],
            "json_data": issue_attachment,
            "domain_data": domain,
            "pdf_data": issue_json["pdf_data"],
            "jira_info": jira_info,
        }

        if self._test_mode:
            self.JsonHelper.save_json(f"Issue_data_{issue_key}", issue)

        return issue

    def _get_nf_jira(self, issue_id):
        try:

            issue_data = self.IssueJira.get_issue(issue_id)
            donwload_attachment = self.AttachmentJira.download_attachments(issue_data)

            request_template = self.GuiandoHelper.get_template_form(issue_data)
            request_type = self.GuiandoHelper.get_request_type(issue_data)

            complement_form = self._get_issue_fields_by_keys(issue_id, request_template)
            self.GuiandoHelper.check_guiando_form(complement_form, request_type)

            attachment = self.AttachmentJira.get_attachment(issue_data)
            model_data = self.GuiandoHelper.prepare_attachment(
                attachment, complement_form, request_type
            )

            # automation_form_id = None
            automation_form_id = self.FormJira.get_form_id(
                issue_id, FORM_TEMPLATE_AUTOMACAO
            )

            nf_jira_json = {
                "issue_data": issue_data,
                "model_data": model_data,
                "jira_info": {
                    "issue_id": issue_id,
                    "form_id": automation_form_id,
                    "request_type": request_type,
                    "transition_type": self.GuiandoHelper.get_transition_type(
                        complement_form
                    ),
                },
                "pdf_data": donwload_attachment,
            }

            return nf_jira_json

        except requests.exceptions.HTTPError as e:
            raise Exception(f"Erro ao receber a Nota Fiscal:\n{e}")

        except Exception as e:
            raise Exception(f"Erro ao receber a Nota Fiscal:\n{e}")

    def _get_issue_fields_by_keys(self, issue_key, form_template, debug=False):

        form_jira_keys = self.FormJira.get_form_jira_keys(issue_key, form_template)
        form_fields = self.FormJira.get_form_fields(issue_key, form_template)
        jira_fields = self.IssueJira.get_issue_fields_data(issue_key)
        fields_by_jira_and_form = self.IssueFields.get_fields_by_form_and_jira(
            form_jira_keys, form_fields, jira_fields
        )
        (
            JsonHelper().save_json(
                f"Fields_From_Keys_{issue_key}", fields_by_jira_and_form
            )
            if debug
            else None
        )

        return fields_by_jira_and_form