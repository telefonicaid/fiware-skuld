#!/usr/bin/env python
# -- encoding: utf-8 --
#
# Copyright 2015 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-Core project.
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
#
author = 'chema'

import glob
import os


def rotate_files(name, max_level, rename_to):
    """
    rotate name, using suffix '.001', '.002' (...) '.999' until
    max_level is reached; then rename that rotation to rename_to.
    :param name: the name of the file without the suffix
    :param max_level: a number with the maximum level.
    :param rename_to: the name the last rotation will be renamed to
    :return: nothing
    """
    names = glob.glob(name + '*')
    names.sort()
    names.reverse()
    target = name + '.' + str(max_level).zfill(3)

    for path in names:
        if len(path) > len(name):
            next_name = name + '.' + str(int(path[-3:]) + 1).zfill(3)
        else:
            next_name = name + '.001'
        if next_name == target:
            os.rename(path, rename_to)
        else:
            os.rename(path, next_name)
