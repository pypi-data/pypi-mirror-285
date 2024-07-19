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

import abc
from dataclasses import asdict
from typing import Any

from google.cloud.firestore_v1.base_query import FieldFilter

from googleads_housekeeper.domain.core import task


class AbstractRepository(abc.ABC):
  def __init__(self):
    self.seen = set()

  def add(self, task: task.Task):
    self._add(task)

  def delete(self, task_id: str):
    self._delete(task_id)

  def get(self, task_id) -> task.Task:
    return self._get(task_id)

  def get_by_conditions(self, conditions: dict[str, Any]) -> task.Task:
    return self._get_by_conditions(conditions)

  def get_by_condition(
    self, condition_name: str, condition_value: str
  ) -> task.Task:
    return self._get_by_conditions({condition_name: condition_value})

  def list(self) -> list[task.Task]:
    return self._list()

  def update(self, task_id: int, update_dict: dict[str, str]) -> task.Task:
    return self._update(task_id, update_dict)

  @abc.abstractmethod
  def _add(self, task: task.Task): ...

  @abc.abstractmethod
  def _get(self, task_id) -> task.Task: ...

  @abc.abstractmethod
  def _get_by_conditions(self, conditions: dict[str, Any]) -> task.Task: ...

  @abc.abstractmethod
  def _list(self) -> list[task.Task]: ...

  @abc.abstractmethod
  def _update(self, task_id, update_dict): ...

  @abc.abstractmethod
  def _delete(self, task_id): ...


class SqlAlchemyRepository(AbstractRepository):
  def __init__(self, session, entity=task.Task):
    super().__init__()
    self.session = session
    self.entity = entity

  def _add(self, task):
    self.session.add(task)

  def _get(self, task_id):
    return self.session.query(self.entity).filter_by(id=task_id).first()

  def _get_by_conditions(self, conditions: dict[str, Any]):
    query = self.session.query(self.entity)
    for condition_name, condition_value in conditions.items():
      query = query.filter(
        getattr(self.entity, condition_name) == condition_value
      )
    return query.all()

  def _list(self):
    return self.session.query(self.entity).all()

  def _update(self, task_id, update_dict):
    return (
      self.session.query(self.entity).filter_by(id=task_id).update(update_dict)
    )

  def _delete(self, task_id):
    return self.session.query(self.entity).filter_by(id=task_id).delete()


class FirestoreRepository(AbstractRepository):
  def __init__(self, client, entity=task.Task):
    super().__init__()
    self.client = client
    self.entity = entity
    self.collection_name = entity.__name__

  def _add(self, task):
    if hasattr(task, 'id'):
      element_id = task.id
    else:
      element_id = task._id
    element_dict = {}
    for key, value in asdict(task).items():
      if hasattr(value, 'name'):
        value = value.name
      element_dict[key] = value
    self.client.collection(self.collection_name).document(str(element_id)).set(
      element_dict
    )

  def _get(self, task_id: str):
    doc = self.client.collection(self.collection_name).document(task_id).get()
    if doc.exists:
      return self.entity(**doc.to_dict())
    return None

  def _get_by_conditions(self, conditions: dict[str, Any]):
    try:
      query = self.client.collection(self.collection_name)
      for condition_name, condition_value in conditions.items():
        query = query.where(
          filter=FieldFilter(condition_name, '==', condition_value)
        )
      results = [self.entity(**result.to_dict()) for result in query.stream()]
      return results
    except Exception:
      return []

  def _list(self):
    results = self.client.collection(self.collection_name).stream()
    entities = [self.entity(**result.to_dict()) for result in results]
    return entities

  def _update(self, task_id: str, update_dict: dict[str, Any]):
    if doc := self.client.collection(self.collection_name).document(task_id):
      doc.update(update_dict)

  def _delete(self, task_id: str) -> None:
    self.client.collection(self.collection_name).document(task_id).delete()
