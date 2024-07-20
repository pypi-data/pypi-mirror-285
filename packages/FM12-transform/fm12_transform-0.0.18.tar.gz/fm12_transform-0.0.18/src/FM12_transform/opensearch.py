import os
import re
import time
import json
import click
import urllib3
import logging
import requests

from enum import Enum
from typing import Union

from datetime import datetime
from datetime import timedelta

from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth, helpers
from boto3 import Session

LOGGER = logging.getLogger(__name__)

WIGOS_STATION_MAPPINGS = {
    'mappings': {
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
}

FEATURE_MAPPINGS = {
    'mappings': {
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
}
    
class OpenSearchClient:
    def __init__(self, host: str, mapping: str, index: str):
        self.os_host = host
        self.os_index = index
        if index == 'wigos_stations':
            self.os_mapping = WIGOS_STATION_MAPPINGS
        else:
           self.os_mapping = FEATURE_MAPPINGS
        region = 'us-east-1'
        service = 'es'
        creds = Session().get_credentials()
        aws_auth = AWSV4SignerAuth(creds, region, service) 
        self.os_client = OpenSearch(
          hosts=[{'host': self.os_host, 'port': 443}],
          http_auth=aws_auth,
          use_ssl=True,
          verify_certs=True,
          connection_class=RequestsHttpConnection)

    def index_info(self):
       return self.os_client.info()

    def index_exists(self):
       return self.os_client.indices.exists(self.os_index)
    
    def create_index(self):
      if not self.os_client.indices.exists(self.os_index):
        result = self.os_client.indices.create(index=self.os_index, body=self.os_mapping)
        LOGGER.info(json.dumps(result))
      else:
        LOGGER.info("Index: " + self.os_index + " exists")
    
    def delete_index(self):
      if self.os_client.indices.exists(self.os_index):
        result = self.os_client.indices.delete(index=self.os_index)
        LOGGER.info(json.dumps(result))
      else:
        LOGGER.info("Index: " + self.os_index + " does not exist")
    
    def index_item(self, feature):
        if not self.os_client.indices.exists(self.os_index):
            LOGGER.debug(f'Index {self.os_index} does not exist.  Creating')
            result = self.os_client.indices.create(index=self.os_index, body=self.os_mapping)
            LOGGER.info(json.dumps(result))
        result = self.os_client.index(index=self.os_index, body=json.dumps(feature), id=feature['id'], refresh = True)
        LOGGER.info(json.dumps(result))
    
    def index_bulk_items(self, features):
        if not self.os_client.indices.exists(self.os_index):
            LOGGER.info(f'Index {self.os_index} does not exist.  Creating')
            result = self.os_client.indices.create(index=self.os_index, body=self.os_mapping)
            LOGGER.info(json.dumps(result))
    
        good = []
        bad = []
        def gendata(features):
            for feature in features:
                feature['properties']['id'] = feature['id']
                yield {
                    '_index': self.os_index,
                    '_id': feature['id'],
                    '_source': feature
                }
        for success, item in helpers.streaming_bulk(self.os_client, actions=gendata(features)):
            if success:
                good.append(item)
            else:
                bad.append(item)
    
        if len(bad) > 0:
            print(f"There were {len(bad)} errors:")
            for item in bad:
                print(item["index"]["error"])
    
        if len(good) > 0:
            print(f"Bulk-inserted {len(good)} items (streaming_bulk).")

    def station_info_lookup(self, tsi):
       if not self.os_client.indices.exists('wigos_stations'):
          LOGGER.error('wigos-stations index does not exist. Create station index and publish station list before looking up stations!')
          return None
       try:
          station_info = self.os_client.search(index='wigos_stations',
                                               body={'query':
                                                     {'match':
                                                      {'properties.traditional_station_identifier': tsi}}})['hits']['hits'][0]['_source']
          return station_info
       except Exception:
          LOGGER.error(f'Station {tsi} not found on wigos-stations index')
          return None
    
    
    #def copy_index(os_client=OpenSearch, self.os_source=str, self.os_target=str):
    #    LOGGER.info("Copying {os_index_source} to {os_index_target}")
    #    try:
    #        helpers.reindex(os_client, self.os_source, self.os_target)
    #    except helpers.BulkIndexError as e:
    #        LOGGER.error('Bulk indexing failed for some documents:')
    #        for err in e.errors:
    #            LOGGER.error(err)
    
    #def retention_delete_items(os_client=OpenSearch, self.os_index=str, days=int):
    #    before = datetime_days_ago(days)
    #    query_by_date = {
    #        'query': {
    #            'bool': {
    #                'should': [{
    #                    'range': {
    #                        'properties.fileTime': {
    #                            'lte': before
    #                        }
    #                    }
    #                }]
    #            }
    #        }
    #    }
    #
    #    LOGGER.debug(f'deleting documents older than {days} days ({before})')  # noqa
    #    result = self.os_client.delete_by_query(index=os_index, **query_by_date)
