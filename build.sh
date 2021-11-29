rm -rf rudder-alerta-enrichment-plugin
git clone -b alert-enrichment-from-workspace-source-destination-tags git@github.com:rudderlabs/rudder-alerta-enrichment-plugin.git
docker build -t rudderlabs/alerta:notification-service-v2 .
rm -rf rudder-alerta-enrichment-plugin