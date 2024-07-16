DEFAULT_ELASTIC_PORT: str = '9200'
DEFAULT_ELASTIC_HOST: str = 'localhost'
DEFAULT_ELASTIC_URL: str = f"http://{DEFAULT_ELASTIC_HOST}:{DEFAULT_ELASTIC_PORT}"
DEFAULT_ELASTIC_URL_JVM_OPTIONS: str = f"{DEFAULT_ELASTIC_URL}/_nodes?filter_path=**.jvm&pretty"

DEFAULT_KIBANA_PORT: str = '5601'
DEFAULT_KIBANA_HOST: str = 'localhost'
DEFAULT_KIBANA_URL: str = f"http://{DEFAULT_KIBANA_HOST}:{DEFAULT_KIBANA_PORT}"

ELASTIC_SEARCH_CONFIG_DIRECTORY: str = "/etc/elasticsearch"

ELASTIC_CONFIG_FILE: str = f"{ELASTIC_SEARCH_CONFIG_DIRECTORY}/elasticsearch.yml"
XPACK_SECURITY_SETTING_NAME: str = "xpack.security.enabled"

ELASTIC_JVM_OPTIONS_DIRECTORY: str = f"{ELASTIC_SEARCH_CONFIG_DIRECTORY}/jvm.options.d"
ELASTIC_JVM_OPTIONS_4GB_CUSTOM_FILE: str = f"{ELASTIC_JVM_OPTIONS_DIRECTORY}/4gb_memory_heap.options"
ELASTIC_JVM_OPTIONS_4GB_MEMORY_USAGE: list[str] = ['-Xms4g', '-Xmx4g']

UBUNTU_DEPENDENCY_PACKAGES: list[str] = ['apt-transport-https', 'openjdk-11-jdk', 'wget']
UBUNTU_ELASTIC_PACKAGE_NAME: str = 'elasticsearch'
UBUNTU_ELASTIC_SERVICE_NAME: str = 'elasticsearch'
UBUNTU_KIBANA_PACKAGE_NAME: str = 'kibana'
UBUNTU_KIBANA_SERVICE_NAME: str = 'kibana'
