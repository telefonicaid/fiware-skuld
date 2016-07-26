# -*- coding: utf-8 -*-

# Copyright 2015 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FIWARE project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at:
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For those usages not covered by the Apache version 2.0 License please
# contact with opensource@tid.es


from fiwareskuld.expired_users import ExpiredUsers
from fiwareskuld.conf import settings
from fiwareskuld.users_management import UserManager
from fiwareskuld.user_resources import UserResources
from commons.configuration import TENANT_NAME, USERNAME, PASSWORD
from commons.logger_utils import get_logger
import datetime

__author__ = 'fla'
__copyright__ = "Copyright 2015"
__license__ = " Apache License, Version 2.0"

__logger__ = get_logger("qautils")


def before_scenario(context, scenario):
    """
    HOOK: To be executed before each Scenario:
        - Init test variables
    """

    __logger__.info("Starting execution of scenario")
    __logger__.info("##############################")
    __logger__.info("##############################")

    context.expiredusers = ExpiredUsers(TENANT_NAME, USERNAME, PASSWORD)
    context.user_manager = UserManager()
    context.expiredusers.finalList = []
    context.expiredusers.listUsers = []
    context.expiredusers.token = None
    context.user_manager.delete_community_users()
    context.user_manager.delete_trial_users()
    context.user_manager.delete_basic_users()
    context.user_resources = []
    context.out_trial = str(datetime.date.today() -
                            datetime.timedelta(days=settings.TRIAL_MAX_NUMBER_OF_DAYS+1))
    context.out_notified_trial = str(datetime.date.today() - datetime.timedelta(days=7))
    context.out_community = str(datetime.date.today() -
                                datetime.timedelta(days=settings.COMMUNITY_MAX_NUMBER_OF_DAYS+1))

    context.out_notified_community = str(datetime.date.today() -
                                         datetime.timedelta(days=settings.COMMUNITY_MAX_NUMBER_OF_DAYS - 30))


def after_scenario(context, scenario):
    """
    HOOK: To be executed after each Scenario:
    """
    context.user_manager.delete_community_users()
    context.user_manager.delete_trial_users()
    context.user_manager.delete_basic_users()

    __logger__.info("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    __logger__.info("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    __logger__.info("Ending execution of scenario")


def after_all(context):
    """
    HOOK: To be executed after all:
        - None (so far)
    """

    __logger__.info("Teardown")
