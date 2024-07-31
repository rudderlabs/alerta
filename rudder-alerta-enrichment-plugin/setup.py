from setuptools import setup, find_packages
setup(
    name='rudder-alerta-enrichment-plugin',
    version='1.0.0',
    packages=['rudder_enrichment', 'rudder_enrichment.rudder_enrichment_models', 'rudder_enrichment.rudder_enrichment_models.ditto'],
    url='https://github.com/rudderlabs/rudder-alerta-enrichment-plugin',
    license='',
    author='Rudderstack',
    author_email='varun@rudderstack.com',
    description='Rudderstack alerta enrichment plugin to enrich alerts delivered to end users, by adding context to alerts',
    include_package_data=True,
    install_requires=[
        'expiringdict==1.2.1',
        'requests==2.26.0'
    ],
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'rudder_enrichment = rudder_enrichment:RudderEnrichment'
        ]
    }
)
