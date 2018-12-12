# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import requests
from urllib.parse import urljoin
from flask import current_app as app
import superdesk
from content_api import ELASTIC_PREFIX as CAPI_ELASTIC_PREFIX

from .index_from_mongo import IndexFromMongo

# this one is not configurable
SD_ELASTIC_PREFIX = 'ELASTICSEARCH'


class FlushElasticIndex(superdesk.Command):
    """Flush elastic index.

    It removes elastic index, creates a new one and index it from mongo.
    You must specify at least one elastic index to flush:
    ``--sd`` (superdesk) or ``--capi`` (content api)
    """

    option_list = [
        superdesk.Option('--sd', action='store_true', dest='sd_index'),
        superdesk.Option('--capi', action='store_true', dest='capi_index')
    ]

    def run(self, sd_index, capi_index):
        if not (sd_index or capi_index):
            raise SystemExit('You must specify at least one elastic index to flush. '
                             'Options: `--sd`, `--capi`')
        if sd_index:
            self._delete_elastic(superdesk.app.config['ELASTICSEARCH_INDEX'])
        if capi_index:
            self._delete_elastic(superdesk.app.config['CONTENTAPI_ELASTICSEARCH_INDEX'])

        self._index_from_mongo(sd_index, capi_index)

    def _delete_elastic(self, index):
        """Deletes elastic index

        :param str index: elastix index
        :raise: SystemExit exception if delete elastic index response status is not 200 or 404.
        """
        es_index_url = urljoin(
            superdesk.app.config['ELASTICSEARCH_URL'],
            index
        )
        print('- Removing elastic index "{}"'.format(index))
        resp = requests.delete(es_index_url)
        if resp.status_code == requests.status_codes.codes.OK:
            print('\t- "{}" elastic index was deleted'.format(index))
        if resp.status_code == requests.status_codes.codes.not_found:
            print('\t- "{}" elastic index was not found. Continue wihout deleting.'.format(index))
        else:
            SystemExit('\t- "{}" elastic index was not deleted. Server response: {}'.format(index, resp.text))

    def _index_from_mongo(self, sd_index, capi_index):
        """Index elastic search from mongo.

        if `sd_index` is true only superdesk elastic index will be indexed.
        if `capi_index` is true only content api elastic index will be indexed.

        :param bool sd_index: Flag to index superdesk elastic index.
        :param bool capi_index:nFlag to index content api elastic index.
        """
        # get all es resources
        app.data.init_elastic(app)
        resources = app.data.get_elastic_resources()

        for resource in resources:
            # get es prefix per resource
            es_backend = superdesk.app.data._search_backend(resource)
            resource_es_prefix = es_backend._resource_prefix(resource)

            if resource_es_prefix == SD_ELASTIC_PREFIX and sd_index:
                print('- Indexing mongo collections into "{}" elastic index.'.format(
                    superdesk.app.config['ELASTICSEARCH_INDEX'])
                )
                IndexFromMongo.copy_resource(
                    resource,
                    IndexFromMongo.default_page_size
                )

            if resource_es_prefix == CAPI_ELASTIC_PREFIX and capi_index:
                print('- Indexing mongo collections into "{}" elastic index.'.format(
                    superdesk.app.config['CONTENTAPI_ELASTICSEARCH_INDEX'])
                )
                IndexFromMongo.copy_resource(
                    resource,
                    IndexFromMongo.default_page_size
                )


superdesk.command('app:flush_elastic_index', FlushElasticIndex())
