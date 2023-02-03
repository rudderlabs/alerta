from flask import jsonify, request
from . import api
from flask_cors import cross_origin

from alerta.auth.decorators import permission
from alerta.models.enums import Scope
from alerta.utils.response import jsonp
from alerta.exceptions import ApiError
from alerta.models.alert_metadata import AlertMetadata


@api.route('/alert-metadata', methods=['OPTIONS', 'POST', 'GET'])
@cross_origin()
@permission(Scope.write_alerts)
@jsonp
def alert_metadata():
    try:
        if request.method == 'POST':
            alert_metadata_dbo = None
            alert_metadata = AlertMetadata.parse(request.json)
            if AlertMetadata.find_by_alert(alert=alert_metadata.alert):
                alert_metadata_dbo = alert_metadata.update()
            else:
                alert_metadata_dbo = alert_metadata.create()
            return jsonify(status='ok', alertMetadata=alert_metadata_dbo.serialize), 200

        elif request.method == 'GET':
            alert_metadata_dbos = AlertMetadata.find_all()
            return jsonify(status='ok', alertMetadata=[am.serialize for am in alert_metadata_dbos]), 200
            
    except Exception as e:
        raise ApiError(str(e), 400)


@api.route('/alert-metadata/<alert>', methods=['OPTIONS', 'GET'])
@cross_origin()
@permission(Scope.write_alerts)
@jsonp
def get_alert_metadata(alert):
    try:
        alert_metadata_dbo = AlertMetadata.find_by_alert(alert=alert)
        return jsonify(status='ok', alertMetadata=alert_metadata_dbo.serialize), 200
    except Exception as e:
        raise ApiError(str(e), 400)


    