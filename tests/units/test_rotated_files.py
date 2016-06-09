# -*- coding: utf-8 -*-

# Copyright 2015-2016 Telefónica Investigación y Desarrollo, S.A.U
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

from mock import patch
from unittest import TestCase
from fiwareskuld.utils.rotated_files import rotate_files as rf
import os


class TestRotatedFiles(TestCase):
    def test_rotated_files_complete_files(self):
        # Given
        name = 'kk'
        max_level = 100
        rename_to = 'foo'

        # /usr/src/Python-1.5/Makefile
        with patch('fiwareskuld.utils.rotated_files.glob') as mockglob:
            mockglob.glob.return_value = ['kk', 'kk.001', 'kk.002', 'kk.003', 'kk.004', 'kk.005']
            expected_value = ['kk.001', 'kk.002', 'kk.003', 'kk.004', 'kk.005', 'kk.006']

            d = {k: v for k, v in zip(mockglob.glob.return_value, expected_value)}

            with patch.object(os, 'rename') as mockrename:
                mockrename.return_value = None

                # When
                rf(name=name, max_level=max_level, rename_to=rename_to)

                # Then
                # Check the number of calls to the os.rename method.
                self.assertEquals(mockrename.call_count, len(mockglob.glob.return_value),
                                  "The rename operator will not called for all the values in the directory")

                # Check that we made all the os.rename calls with the proper name file.
                for k, v in d.iteritems():
                    mockrename.assert_any_call(k, v)

    def test_rotated_files_with_only_one_file_with_number(self):
        # Given
        name = 'fake'
        max_level = 100
        rename_to = 'foo'

        # /usr/src/Python-1.5/Makefile
        with patch('fiwareskuld.utils.rotated_files.glob') as mockglob:
            mockglob.glob.return_value = ['fake.001']
            expected_value = ['fake.002']

            d = {k: v for k, v in zip(mockglob.glob.return_value, expected_value)}

            with patch.object(os, 'rename') as mockrename:
                mockrename.return_value = None

                # When
                rf(name=name, max_level=max_level, rename_to=rename_to)

                # Then
                self.assertEquals(mockrename.call_count, len(mockglob.glob.return_value),
                                  "The rename operator will not called for all the values in the directory")

                # Check that we made all the os.rename calls with the proper name file.
                for k, v in d.iteritems():
                    mockrename.assert_any_call(k, v)

    def test_rotated_files_with_only_one_file_without_number(self):
        # Given
        name = 'fake'
        max_level = 100
        rename_to = 'foo'

        # /usr/src/Python-1.5/Makefile
        with patch('fiwareskuld.utils.rotated_files.glob') as mockglob:
            mockglob.glob.return_value = ['fake']
            expected_value = ['fake.001']

            d = {k: v for k, v in zip(mockglob.glob.return_value, expected_value)}

            with patch.object(os, 'rename') as mockrename:
                mockrename.return_value = None

                # When
                rf(name=name, max_level=max_level, rename_to=rename_to)

                # Then
                self.assertEquals(mockrename.call_count, len(mockglob.glob.return_value),
                                  "The rename operator will not called for all the values in the directory")

                # Check that we made all the os.rename calls with the proper name file.
                for k, v in d.iteritems():
                    mockrename.assert_any_call(k, v)

    def test_rotated_files_with_max_level(self):
        # Given
        name = 'kk'
        max_level = 4
        rename_to = 'foo'

        # /usr/src/Python-1.5/Makefile
        with patch('fiwareskuld.utils.rotated_files.glob') as mockglob:
            mockglob.glob.return_value = ['kk', 'kk.001', 'kk.002', 'kk.003']
            expected_value = ['kk.001', 'kk.002', 'kk.003', 'foo']

            d = {k: v for k, v in zip(mockglob.glob.return_value, expected_value)}

            with patch.object(os, 'rename') as mockrename:
                mockrename.return_value = None

                # When
                rf(name=name, max_level=max_level, rename_to=rename_to)

                # Then
                self.assertEquals(mockrename.call_count, len(mockglob.glob.return_value),
                                  "The rename operator will not called for all the values in the directory")

                # Check that we made all the os.rename calls with the proper name file.
                for k, v in d.iteritems():
                    mockrename.assert_any_call(k, v)
