#!/usr/bin/env python

from elasticsearch import Elasticsearch

FEATURE_MAPPINGS = {
    'properties': {
        'date_detection': False,
        'geometry': {
            'type': 'geo_shape'
        },
        'time': {
            'properties': {
                'interval': {
                    'type': 'date',
                    'null_value': '1850',
                    'format': 'year||year_month||year_month_day||date_time||t_time||t_time_no_millis',  # noqa
                    'ignore_malformed': True
                }
            }
        },
        'reportId': {
            'type': 'text',
            'fields': {
                'raw': {
                    'type': 'keyword'
                }
            }
        },
        'properties': {
            'properties': {
                'resultTime': {
                    'type': 'date',
                    'fields': {
                        'raw': {
                            'type': 'keyword'
                        }
                    }
                },
                'pubTime': {
                    'type': 'date',
                    'fields': {
                        'raw': {
                            'type': 'keyword'
                        }
                    }
                },
                'phenomenonTime': {
                    'type': 'text'
                },
                'station_identifier': {
                    'type': 'text',
                    'fields': {
                        'raw': {'type': 'keyword'}
                    }
                },
                'value': {
                    'type': 'float',
                    'coerce': True
                },
                'metadata': {
                    'properties': {
                        'value': {
                            'type': 'float',
                            'coerce': True
                        }
                    }
                }
            }
        }
    }
}

def create_feature_index():
    client = Elasticsearch('http://localhost:9200')
    client.indices.create(index="fm14_features", mappings=FEATURE_MAPPINGS)

