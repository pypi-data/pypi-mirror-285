#!/usr/bin/env python

from elasticsearch import Elasticsearch

FEATURE_MAPPINGS = {
    'date_detection': False,
    'properties': {
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

WIGOS_STATION_MAPPINGS = {
    'properties': {
        'geometry': {
            'type': 'geo_shape'
        },
        'properties': {
            'properties': {
                'name': {
                    'type': 'text',
                    'fields': {
                        'raw': {'type': 'keyword'}
                    }
                },
                'wigos_station_identifier': {
                    'type': 'text',
                    'fields': {
                        'raw': {'type': 'keyword'}
                    }
                },
                'traditional_station_identifier': {
                    'type': 'text',
                    'fields': {
                        'raw': {'type': 'keyword'}
                    }
                },
                'barometer_height': {
                    'type': 'float'
                },
                'facility_type': {
                    'type': 'text',
                    'fields': {
                        'raw': {'type': 'keyword'}
                    }
                },
                'territory_name': {
                    'type': 'text',
                    'fields': {
                        'raw': {'type': 'keyword'}
                    }
                },
                'wmo_region': {
                    'type': 'text',
                    'fields': {
                        'raw': {'type': 'keyword'}
                    }
                },
                'url': {
                    'type': 'text',
                    'fields': {
                        'raw': {'type': 'keyword'}
                    }
                },
            }
        }
    }
}

def create_feature_index():
    client = Elasticsearch('http://localhost:9200')
    client.indices.create(index="fm12_features", mappings=FEATURE_MAPPINGS)

def create_station_index():
    client = Elasticsearch('http://localhost:9200')
    client.indices.create(index="wigos_stations", mappings=WIGOS_STATION_MAPPINGS)

