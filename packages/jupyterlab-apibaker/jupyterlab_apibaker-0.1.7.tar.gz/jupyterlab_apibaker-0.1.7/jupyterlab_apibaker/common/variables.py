# NSQ URLS
# URL_BASE = "http://10.111.64.25:3000"
URL_BASE = "http://api-baker-backend.api-baker-backend.svc.cluster.local:3000"
ENDPOINT = f"{URL_BASE}/endpoints"
README_URL = ENDPOINT + "/{}/versions/{}/readme"
GET_IMAGE_STATUS_URL = ENDPOINT + "/{}/versions/{}"
FUNCTION_EXECUTION_URL = ENDPOINT + "/{}/versions/{}/submit"  # POST
GET_WORKFLOWS_STATUS_URL = ENDPOINT + "/{}/versions/{}/workflows"
GET_EXECUTION_STATUS_URL = ENDPOINT + "/{}/versions/{}/workflows/{}"
GET_EXECUTION_LOG_URL = ENDPOINT + "/{}/versions/{}/workflows/{}/log"
LOGS_URL = (
    GET_EXECUTION_STATUS_URL
    + "/log?logOptions.container=main&grep&logOptions.follow=true"
)

GET_OWN_ENDPOINTS = ENDPOINT + "?owner={}"
GET_OWN_NOTEBOOK = ENDPOINT + "?owner={}&notebookName={}"
GET_OWN_FUNCTION = ENDPOINT + "?owner={}&functionName={}"
GET_ENDPOINT_VERSION = ENDPOINT + "/{}/versions/{}"
DELETE_ENDPOINT = ENDPOINT + "/{}"

CREATE_USER_API_KEY = ENDPOINT + "/{}/api-keys"
CREATE_ADMIN_API_KEY = URL_BASE + "/admin/api-keys"
GET_ALL_API_KEYS = ENDPOINT + "/{}/api-keys"
MODIFY_API_KEY = ENDPOINT + "/{}/api-keys/{}"
REFRESH_API_KEY = ENDPOINT + "/{}/api-keys/{}/refresh"
