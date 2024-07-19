from . import native_user, integration_sso, identities, integration_external_api, datastore, sidecar, integration_datahub, encryption, metrics, work_os, audit, satellite, integration_github, integration_slack, search, integration_mfa, integration_kms, inventory, etl, admin, cord, integration_app, permissions, registry, integration_log, integration_code_repository, integration_cloud, policies
import grpc

SERVER_URL = "adminv2.api.formalcloud.net:443"

class Client(object):
	"""Formal Admin API Client"""

	def __init__(self, api_key):
		"""Constructor.

		Args:
			api_key: Formal API Key
		"""
		self.NativeUserClient = native_user.NativeUserService(SERVER_URL, api_key)
		self.SsoClient = integration_sso.SsoService(SERVER_URL, api_key)
		self.UserClient = identities.UserService(SERVER_URL, api_key)
		self.GroupClient = identities.GroupService(SERVER_URL, api_key)
		self.ExternalApiClient = integration_external_api.ExternalApiService(SERVER_URL, api_key)
		self.DataStoreClient = datastore.DataStoreService(SERVER_URL, api_key)
		self.SidecarClient = sidecar.SidecarService(SERVER_URL, api_key)
		self.DatahubClient = integration_datahub.DatahubService(SERVER_URL, api_key)
		self.FieldEncryptionPolicyClient = encryption.FieldEncryptionPolicyService(SERVER_URL, api_key)
		self.FieldEncryptionClient = encryption.FieldEncryptionService(SERVER_URL, api_key)
		self.MetricsClient = metrics.MetricsService(SERVER_URL, api_key)
		self.DSyncClient = work_os.DSyncService(SERVER_URL, api_key)
		self.AuditLogsClient = audit.AuditLogsService(SERVER_URL, api_key)
		self.SatelliteClient = satellite.SatelliteService(SERVER_URL, api_key)
		self.GithubClient = integration_github.GithubService(SERVER_URL, api_key)
		self.SlackClient = integration_slack.SlackService(SERVER_URL, api_key)
		self.SearchClient = search.SearchService(SERVER_URL, api_key)
		self.IntegrationMfaClient = integration_mfa.IntegrationMfaService(SERVER_URL, api_key)
		self.KmsClient = integration_kms.KmsService(SERVER_URL, api_key)
		self.InventoryClient = inventory.InventoryService(SERVER_URL, api_key)
		self.ETLClient = etl.ETLService(SERVER_URL, api_key)
		self.DevClient = admin.DevService(SERVER_URL, api_key)
		self.CordClient = cord.CordService(SERVER_URL, api_key)
		self.AppClient = integration_app.AppService(SERVER_URL, api_key)
		self.PermissionClient = permissions.PermissionService(SERVER_URL, api_key)
		self.RegistryClient = registry.RegistryService(SERVER_URL, api_key)
		self.LogsClient = integration_log.LogsService(SERVER_URL, api_key)
		self.CodeRepositoryClient = integration_code_repository.CodeRepositoryService(SERVER_URL, api_key)
		self.CloudClient = integration_cloud.CloudService(SERVER_URL, api_key)
		self.PolicyClient = policies.PolicyService(SERVER_URL, api_key)
