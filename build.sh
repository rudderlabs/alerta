rm -rf rudder-alerta-enrichment-plugin
git clone -b alert-enrichment-from-workspace-source-destination-tags git@github.com:rudderlabs/rudder-alerta-enrichment-plugin.git
docker build --build-arg=COMMIT_ID_VALUE="$(git log --format="%H" -n 1)" -t rudderlabs/alerta:notification-service-v2 .
rm -rf rudder-alerta-enrichment-plugin
