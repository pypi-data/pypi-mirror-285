# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Module for defining configuration entities."""

from __future__ import annotations

import dataclasses
import uuid


@dataclasses.dataclass
class Config:
  """Holds application configuration parameters.

  Attributes:
      mcc_id:
          MCC account to fetch data from.
      email_address:
          Admin email address to get notifications.
      always_fetch_youtube_preview_mode:
          Whether to force fetch YouTube data in preview mode.
      save_to_db:
          Whether to saved parsed data to DB.
      id:
          Unique config identifier.
  """

  mcc_id: str
  email_address: str
  always_fetch_youtube_preview_mode: bool = True
  save_to_db: bool = True
  id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))


@dataclasses.dataclass
class CustomerIds:
  """Contains all information on a single Google Ads account.

  Attributes:
      mcc_id: Id of an MCC account associated with a given child account.
      account_name: Name of Google Ads account.
      id: Id of Google Ads account.
  """

  mcc_id: str
  account_name: str
  id: str


@dataclasses.dataclass
class MccIds:
  """Contains all information on a single Google Ads MMC account.

  Attributes:
      id: Id of an MCC account.
      account_name: Name of Google Ads MMC account.
  """

  id: str
  account_name: str
