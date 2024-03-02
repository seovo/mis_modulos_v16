from odoo import http
import msal
#from services.pbiembedservice import PbiEmbedService
import requests
import json
model_ir_config = 'ir.config_parameter'

class ControllerAngular(http.Controller):

    @http.route(['/ui/powerbi/<model("list.powerbi"):instance>'], type='http', auth="user",
                methods=['POST', 'GET'], website=True, csrf=True)
    def index(self, instance, **post):
        '''
        url_main = http.request.env[model_ir_config].sudo().search(
            [('key', '=', 'url_for_angular')])
        if url_main:
            url_main = url_main.value
        else:
            url_main = http.request.env[model_ir_config].sudo().create(dict(
                key='url_for_angular',
                value=http.request.env[model_ir_config].sudo().search(
                    [('key', '=', 'web.base.url')]).value
            ))
            url_main = url_main.value
        data = {
            'data': json.dumps(
                {
                    'token': '',
                    'id_sale': instance.id,
                    'url': url_main,
                }
            )
        }
        '''
        # str(request.session.session_token)
        action = http.request.env.ref('list_powerbi_report.action_list_powerbi')
        menu =  http.request.env.ref('list_powerbi_report.menu_list_powerbi')

        redirect  = f'/web#action={action.id}&model=list.powerbi&view_type=list&cids=1&menu_id={menu.id}'
        return http.request.render('list_powerbi_report.index', {
            'instance': instance ,
            'redirect': redirect
        })

    # metodos para llamda del api de power bi
    @http.route(['/getembedinfo/<model("list.powerbi"):instance>'], type='http', auth="public", methods=['GET'],
                website=True, csrf=False)
    def sale_angular(self,  instance , **kw):
        WORKSPACE_ID = instance.workspace_id
        REPORT_ID = instance.report_id
        try:
            embed_info = self.get_embed_params_for_single_report(WORKSPACE_ID,REPORT_ID,instance=instance)
            return embed_info
        except Exception as ex:
            return json.dumps({'errorMsg': str(ex)}), 500


    def get_embed_params_for_single_report(self, workspace_id, report_id, additional_dataset_id=None,instance=None):
        '''Get embed params for a report and a workspace

        Args:
            workspace_id (str): Workspace Id
            report_id (str): Report Id
            additional_dataset_id (str, optional): Dataset Id different than the one bound to the report. Defaults to None.

        Returns:
            EmbedConfig: Embed token and Embed URL
        '''

        report_url = f'https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}'
        api_response = requests.get(report_url, headers=self.get_request_header(instance))

        if api_response.status_code != 200:
            raise ValueError([api_response.status_code,f'Error while retrieving Embed URL\n{api_response.reason}:\t{api_response.text}\nRequestId:\t{api_response.headers.get("RequestId")}'])
            abort(api_response.status_code, description=f'Error while retrieving Embed URL\n{api_response.reason}:\t{api_response.text}\nRequestId:\t{api_response.headers.get("RequestId")}')

        api_response = json.loads(api_response.text)
        report = ReportConfig(api_response['id'], api_response['name'], api_response['embedUrl'])
        dataset_ids = [api_response['datasetId']]

        # Append additional dataset to the list to achieve dynamic binding later
        if additional_dataset_id is not None:
            dataset_ids.append(additional_dataset_id)

        embed_token = self.get_embed_token_for_single_report_single_workspace(report_id, dataset_ids, workspace_id , instance=instance)
        embed_config = EmbedConfig(embed_token.tokenId, embed_token.token, embed_token.tokenExpiry, [report.__dict__])
        return json.dumps(embed_config.__dict__)

    def get_embed_params_for_multiple_reports(self, workspace_id, report_ids, additional_dataset_ids=None,instance=None):
        '''Get embed params for multiple reports for a single workspace

        Args:
            workspace_id (str): Workspace Id
            report_ids (list): Report Ids
            additional_dataset_ids (list, optional): Dataset Ids which are different than the ones bound to the reports. Defaults to None.

        Returns:
            EmbedConfig: Embed token and Embed URLs
        '''

        # Note: This method is an example and is not consumed in this sample app

        dataset_ids = []

        # To store multiple report info
        reports = []

        for report_id in report_ids:
            report_url = f'https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}'
            api_response = requests.get(report_url, headers=self.get_request_header(instance))

            if api_response.status_code != 200:
                raise ValueError([api_response.status_code,
                                  f'Error while retrieving Embed URL\n{api_response.reason}:\t{api_response.text}\nRequestId:\t{api_response.headers.get("RequestId")}'])
                #abort(api_response.status_code,
                #      description=f'Error while retrieving Embed URL\n{api_response.reason}:\t{api_response.text}\nRequestId:\t{api_response.headers.get("RequestId")}')

            api_response = json.loads(api_response.text)
            report_config = ReportConfig(api_response['id'], api_response['name'], api_response['embedUrl'])
            reports.append(report_config.__dict__)
            dataset_ids.append(api_response['datasetId'])

        # Append additional dataset to the list to achieve dynamic binding later
        if additional_dataset_ids is not None:
            dataset_ids.extend(additional_dataset_ids)

        embed_token = self.get_embed_token_for_multiple_reports_single_workspace(report_ids, dataset_ids, workspace_id,instance=instance)
        embed_config = EmbedConfig(embed_token.tokenId, embed_token.token, embed_token.tokenExpiry, reports)
        return json.dumps(embed_config.__dict__)

    def get_embed_token_for_single_report_single_workspace(self, report_id, dataset_ids, target_workspace_id=None,instance=None):
        '''Get Embed token for single report, multiple datasets, and an optional target workspace

        Args:
            report_id (str): Report Id
            dataset_ids (list): Dataset Ids
            target_workspace_id (str, optional): Workspace Id. Defaults to None.

        Returns:
            EmbedToken: Embed token
        '''

        request_body = EmbedTokenRequestBody()

        for dataset_id in dataset_ids:
            request_body.datasets.append({'id': dataset_id})

        request_body.reports.append({'id': report_id})

        if target_workspace_id is not None:
            request_body.targetWorkspaces.append({'id': target_workspace_id})

        # Generate Embed token for multiple workspaces, datasets, and reports. Refer https://aka.ms/MultiResourceEmbedToken
        embed_token_api = 'https://api.powerbi.com/v1.0/myorg/GenerateToken'
        api_response = requests.post(embed_token_api, data=json.dumps(request_body.__dict__),
                                     headers=self.get_request_header(instance))

        if api_response.status_code != 200:
            raise ValueError([api_response.status_code,f'Error while retrieving Embed token\n{api_response.reason}:\t{api_response.text}\nRequestId:\t{api_response.headers.get("RequestId")}'])
            #abort(api_response.status_code,
            #      description=f'Error while retrieving Embed token\n{api_response.reason}:\t{api_response.text}\nRequestId:\t{api_response.headers.get("RequestId")}')

        api_response = json.loads(api_response.text)
        embed_token = EmbedToken(api_response['tokenId'], api_response['token'], api_response['expiration'])
        return embed_token

    def get_embed_token_for_multiple_reports_single_workspace(self, report_ids, dataset_ids, target_workspace_id=None , instance = None):
        '''Get Embed token for multiple reports, multiple dataset, and an optional target workspace

        Args:
            report_ids (list): Report Ids
            dataset_ids (list): Dataset Ids
            target_workspace_id (str, optional): Workspace Id. Defaults to None.

        Returns:
            EmbedToken: Embed token
        '''

        # Note: This method is an example and is not consumed in this sample app

        request_body = EmbedTokenRequestBody()

        for dataset_id in dataset_ids:
            request_body.datasets.append({'id': dataset_id})

        for report_id in report_ids:
            request_body.reports.append({'id': report_id})

        if target_workspace_id is not None:
            request_body.targetWorkspaces.append({'id': target_workspace_id})

        # Generate Embed token for multiple workspaces, datasets, and reports. Refer https://aka.ms/MultiResourceEmbedToken
        embed_token_api = 'https://api.powerbi.com/v1.0/myorg/GenerateToken'
        api_response = requests.post(embed_token_api, data=json.dumps(request_body.__dict__),
                                     headers=self.get_request_header(instance))

        if api_response.status_code != 200:
            raise ValueError([api_response.status_code,f'Error while retrieving Embed token\n{api_response.reason}:\t{api_response.text}\nRequestId:\t{api_response.headers.get("RequestId")}'])
            #abort(api_response.status_code,
            #      description=f'Error while retrieving Embed token\n{api_response.reason}:\t{api_response.text}\nRequestId:\t{api_response.headers.get("RequestId")}')

        api_response = json.loads(api_response.text)
        embed_token = EmbedToken(api_response['tokenId'], api_response['token'], api_response['expiration'])
        return embed_token

    def get_embed_token_for_multiple_reports_multiple_workspaces(self, report_ids, dataset_ids,
                                                                 target_workspace_ids=None,instance=None):
        '''Get Embed token for multiple reports, multiple datasets, and optional target workspaces

        Args:
            report_ids (list): Report Ids
            dataset_ids (list): Dataset Ids
            target_workspace_ids (list, optional): Workspace Ids. Defaults to None.

        Returns:
            EmbedToken: Embed token
        '''

        # Note: This method is an example and is not consumed in this sample app

        request_body = EmbedTokenRequestBody()

        for dataset_id in dataset_ids:
            request_body.datasets.append({'id': dataset_id})

        for report_id in report_ids:
            request_body.reports.append({'id': report_id})

        if target_workspace_ids is not None:
            for target_workspace_id in target_workspace_ids:
                request_body.targetWorkspaces.append({'id': target_workspace_id})

        # Generate Embed token for multiple workspaces, datasets, and reports. Refer https://aka.ms/MultiResourceEmbedToken
        embed_token_api = 'https://api.powerbi.com/v1.0/myorg/GenerateToken'
        api_response = requests.post(embed_token_api, data=json.dumps(request_body.__dict__),
                                     headers=self.get_request_header(instance))

        if api_response.status_code != 200:
            raise ValueError([api_response.status_code,'Error while retrieving Embed token\n{api_response.reason}:\t{api_response.text}\nRequestId:\t{api_response.headers.get("RequestId")}'])
            #abort(api_response.status_code,
            #      description=f'Error while retrieving Embed token\n{api_response.reason}:\t{api_response.text}\nRequestId:\t{api_response.headers.get("RequestId")}')

        api_response = json.loads(api_response.text)
        embed_token = EmbedToken(api_response['tokenId'], api_response['token'], api_response['expiration'])
        return embed_token

    def get_request_header(self,instance):
        '''Get Power BI API request header

        Returns:
            Dict: Request header
        '''


        return {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.get_access_token(instance)}


    def get_access_token(self,instance):
        '''Generates and returns Access token

        Returns:
            string: Access token
        '''
        AUTHENTICATION_MODE = instance.authentication_mode
        CLIENT_ID = instance.client_id
        AUTHORITY_URL= instance.authority_url
        POWER_BI_USER = instance.power_bi_user

        POWER_BI_PASS = instance.power_bi_pass
        TENANT_ID = instance.tenant_id
        CLIENT_SECRET = instance.client_secret
        SCOPE_BASE = [instance.scope_base]



        response = None
        try:
            if AUTHENTICATION_MODE.lower() == 'masteruser':

                # Create a public client to authorize the app with the AAD app
                clientapp = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY_URL)
                accounts = clientapp.get_accounts(username=POWER_BI_USER)

                if accounts:
                    # Retrieve Access token from user cache if available
                    response = clientapp.acquire_token_silent(SCOPE_BASE, account=accounts[0])

                if not response:
                    # Make a client call if Access token is not available in cache
                    response = clientapp.acquire_token_by_username_password(POWER_BI_USER, POWER_BI_PASS, scopes=SCOPE_BASE)

            # Service Principal auth is the recommended by Microsoft to achieve App Owns Data Power BI embedding
            elif AUTHENTICATION_MODE.lower() == 'serviceprincipal':
                authority = AUTHORITY_URL.replace('organizations', TENANT_ID)
                clientapp = msal.ConfidentialClientApplication(CLIENT_ID, client_credential=CLIENT_SECRET, authority=authority)

                # Make a client call if Access token is not available in cache
                response = clientapp.acquire_token_for_client(scopes=SCOPE_BASE)

            try:
                return response['access_token']
            except KeyError:
                raise Exception(response['error_description'])

        except Exception as ex:
            raise Exception('Error retrieving Access token\n' + str(ex))

class EmbedToken:

    # Camel casing is used for the member variables as they are going to be serialized and camel case is standard for JSON keys

    tokenId = None
    token = None
    tokenExpiry = None

    def __init__(self, token_id, token, token_expiry):
        self.tokenId = token_id
        self.token = token
        self.tokenExpiry = token_expiry
class ReportConfig:

    # Camel casing is used for the member variables as they are going to be serialized and camel case is standard for JSON keys

    reportId = None
    reportName = None
    embedUrl = None
    datasetId = None

    def __init__(self, report_id, report_name, embed_url, dataset_id = None):
        self.reportId = report_id
        self.reportName = report_name
        self.embedUrl = embed_url
        self.datasetId = dataset_id

class EmbedConfig:

    # Camel casing is used for the member variables as they are going to be serialized and camel case is standard for JSON keys

    tokenId = None
    accessToken = None
    tokenExpiry = None
    reportConfig = None

    def __init__(self, token_id, access_token, token_expiry, report_config):
        self.tokenId = token_id
        self.accessToken = access_token
        self.tokenExpiry = token_expiry
        self.reportConfig = report_config


class EmbedTokenRequestBody:

    # Camel casing is used for the member variables as they are going to be serialized and camel case is standard for JSON keys

    datasets = None
    reports = None
    targetWorkspaces = None

    def __init__(self):
        self.datasets = []
        self.reports = []
        self.targetWorkspaces = []