# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.publish.formatters import Formatter
import superdesk
import re
from eve.utils import config
from superdesk.utils import json_serialize_datetime_objectId
from superdesk.errors import FormatterError
from superdesk.metadata.item import ITEM_TYPE, PACKAGE_TYPE
from bs4 import BeautifulSoup
from .field_mappers.locator_mapper import LocatorMapper
from apps.publish.formatters.aap_formatter_common import set_subject
import json


class AAPBulletinBuilderFormatter(Formatter):
    """
    Bulletin Builder Formatter
    """
    def format(self, article, subscriber):
        """
        Formats the article as require by the subscriber
        :param dict article: article to be formatted
        :param dict subscriber: subscriber receiving the article
        :return: tuple (int, str) of publish sequence of the subscriber, formatted article as string
        """
        try:

            article['slugline'] = self.append_legal(article=article, truncate=True)
            pub_seq_num = superdesk.get_resource_service('subscribers').generate_sequence_number(subscriber)
            body_html = self.append_body_footer(article).strip('\r\n')
            soup = BeautifulSoup(body_html, 'html.parser')

            if not len(soup.find_all('p')):
                for br in soup.find_all('br'):
                    # remove the <br> tag
                    br.replace_with(' {}'.format(br.get_text()))

            for p in soup.find_all('p'):
                # replace <p> tag with two carriage return
                for br in p.find_all('br'):
                    # remove the <br> tag
                    br.replace_with(' {}'.format(br.get_text()))

                para_text = p.get_text().strip()
                if para_text != '':
                    p.replace_with('{}\r\n\r\n'.format(para_text))
                else:
                    p.replace_with('')

            article['body_text'] = re.sub(' +', ' ', soup.get_text())
            # get the first category and derive the locator
            category = next((iter(article.get('anpa_category', []))), None)
            if category:
                locator = LocatorMapper().map(article, category.get('qcode').upper())
                if locator:
                    article['place'] = [{'qcode': locator, 'name': locator}]

                article['first_category'] = category
                article['first_subject'] = set_subject(category, article)

            odbc_item = {
                'id': article.get(config.ID_FIELD),
                'version': article.get(config.VERSION),
                ITEM_TYPE: article.get(ITEM_TYPE),
                PACKAGE_TYPE: article.get(PACKAGE_TYPE, ''),
                'headline': article.get('headline', '').replace('\'', '\'\''),
                'slugline': article.get('slugline', '').replace('\'', '\'\''),
                'data': superdesk.json.dumps(article, default=json_serialize_datetime_objectId).replace('\'', '\'\'')
            }

            return [(pub_seq_num, json.dumps(odbc_item, default=json_serialize_datetime_objectId))]
        except Exception as ex:
            raise FormatterError.bulletinBuilderFormatterError(ex, subscriber)

    def can_format(self, format_type, article):
        return format_type == 'AAP BULLETIN BUILDER'
