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
from __future__ import annotations

import functools
import json
import logging
import time
from dataclasses import asdict

from googleads_housekeeper.domain import events


class BasePublisher: ...


def emit_with_retry(max_retries: int = 3, retry_delay: float = 1.0) -> callable:
  """Decorator that retries a function if it raises an exception.

  Args:
      max_retries: Maximum number of retries (default: 3).
      retry_delay: Delay in seconds between retries (default: 1.0).

  Returns:
      The decorated function.
  """

  def decorator_emit_with_retry(func: callable) -> callable:
    @functools.wraps(func)
    def wrapper_emit_with_retry(*args: any, **kwargs: any) -> any:
      retries = 0
      while retries <= max_retries:
        try:
          return func(*args, **kwargs)
        except Exception as e:  # Consider catching more specific exceptions
          logging.warning(
            f'Error emitting: {e}. Retrying in {retry_delay} seconds...'
          )
          retries += 1
          time.sleep(retry_delay)

      logging.error('Maximum retries reached. Emission failed.')

    return wrapper_emit_with_retry

  return decorator_emit_with_retry


class RedisPublisher(BasePublisher):
  def __init__(
    self, client: 'redis.Redis', topic_prefix: str | None = None
  ) -> None:
    self.client = client
    self.topic_prefix = topic_prefix

  @emit_with_retry(max_retries=1, retry_delay=1)
  def publish(self, topic: str, event: events.Event) -> None:
    if self.topic_prefix:
      topic = f'{self.topic_prefix}_{topic}'
    self.client.publish(topic, json.dumps(asdict(event), default=str))


class GoogleCloudPubSubPublisher(BasePublisher):
  def __init__(
    self,
    client: 'google.cloud.pubsub_v1.PublisherClient',
    project_id: str,
    topic_prefix: str | None = None,
  ) -> None:
    self.client = client
    self.project_id = project_id
    self.topic_prefix = topic_prefix

  @emit_with_retry
  def publish(self, topic: str, event: events.Event) -> None:
    if self.topic_prefix:
      topic = f'{self.topic_prefix}_{topic}'
    topic_name = f'projects/{self.project_id}/topics/{topic}'
    data = str(json.dumps(asdict(event), default=str)).encode('utf-8')
    future = self.client.publish(topic_name, data=data)
    future.result()


class LogPublisher(BasePublisher):
  def __init__(self, topic_prefix: str | None = None) -> None:
    self.topic_prefix = topic_prefix

  def publish(self, topic: str, event: events.Event) -> None:
    if self.topic_prefix:
      topic = f'{self.topic_prefix}_{topic}'
    logging.info("Published to topic '%s': %s", topic, asdict(event))
