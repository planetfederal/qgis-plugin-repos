"""
Repo configuration
"""
# Validator metadata configuration
PLUGIN_MAX_UPLOAD_SIZE=1048576
PLUGIN_REQUIRED_METADATA=('name', 'description', 'version', 'qgisMinimumVersion', 'author', 'about', 'tracker', 'repository')
PLUGIN_OPTIONAL_METADATA=( 'homepage', 'changelog', 'qgisMaximumVersion', 'tags', 'deprecated', 'experimental', 'external_deps', 'server')
PLUGIN_BOOLEAN_METADATA=('experimental', 'deprecated', 'server')
