# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES.
# SPDX-FileCopyrightText: All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .api_endpoint import ApiEndpoint


class Flags(ApiEndpoint):
    '''
    Flags API endpoint class
    '''

    def make_url(self):
        '''
        Make the URL for the API endpoint

        Parameters:
            None
        Returns:
            url (str): The URL for the API endpoint
        '''
        return '/api/v1/status/flags'
