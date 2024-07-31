class Workspace:
    def __init__(self, id, name, token, owner, organization, *args, **kwargs):
        self.id = id
        self.name = name
        self.token = token
        self.owner = owner
        self.organization = organization

    def enrich_alert(self, alert):
        if not isinstance(alert.enriched_data, dict) and not alert.enriched_data:
            alert.enriched_data = {}
        alert.enriched_data['admin_email'] = self.admin_email
        settings = self.organization['settings']
        is_pro = settings.get('pro', False)
        is_enterprise = settings.get('enterprise', False)
        is_paid = any([is_pro, is_enterprise])
        is_trail = not is_paid
        alert.properties = {"freetrail": is_trail}
        return alert

    @property
    def company_name(self):
        return self.organization['name']

    @property
    def admin_email(self):
        try:
            return self.owner['email']
        except Exception as e:
            return None

    @staticmethod
    def from_json(json_dict: dict):
        return Workspace(**json_dict)

    @staticmethod
    def attach_customer_information():
        pass
