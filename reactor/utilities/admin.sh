#
#=========================================================================================
# Nexical Interface Utilities
#

function nexical_interface_setup_admin () {
  namespace="$1"
  service_name="$2"
  ssh_pod="$(kubectl get pods -n "$namespace" --no-headers -o custom-columns=':metadata.name' | grep "$service_name")"

  "${__binary_dir}/kubectl" exec -n "$namespace" "$ssh_pod" -- /setup 1>>"$(logfile)" 2>&1
}
