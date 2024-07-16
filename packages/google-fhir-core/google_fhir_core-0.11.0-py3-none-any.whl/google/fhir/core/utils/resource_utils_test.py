#
# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Test resource_utils functionality."""

from absl.testing import absltest
from google.fhir.r4.proto.core import datatypes_pb2
from google.fhir.r4.proto.core.resources import account_pb2
from google.fhir.r4.proto.core.resources import activity_definition_pb2
from google.fhir.r4.proto.core.resources import bundle_and_contained_resource_pb2
from google.fhir.r4.proto.core.resources import structure_definition_pb2
from google.fhir.core.utils import resource_utils

# TODO(b/176912972): These util tests should not be FHIR-specific.


def _bundle_with_single_structure_definition(
) -> bundle_and_contained_resource_pb2.Bundle:
  """Returns a `Bundle` with a single `StructureDefinition` entry."""
  return bundle_and_contained_resource_pb2.Bundle(entry=[
      bundle_and_contained_resource_pb2.Bundle.Entry(
          resource=bundle_and_contained_resource_pb2.ContainedResource(
              structure_definition=structure_definition_pb2.StructureDefinition(
                  name=datatypes_pb2.String(value='Test'))))
  ])


class ResourceUtilsTest(absltest.TestCase):
  """Performs unit tests targeting `resource_utils`."""

  def test_extract_resources_from_bundle_with_set_resource_succeeds(self):
    bundle = _bundle_with_single_structure_definition()
    actual = resource_utils.extract_resources_from_bundle(
        bundle, resource_type=structure_definition_pb2.StructureDefinition)
    self.assertLen(actual, 1)

  def test_extract_resources_from_bundle_with_unset_resource_returns_empty(
      self,
  ):
    bundle = _bundle_with_single_structure_definition()
    actual = resource_utils.extract_resources_from_bundle(
        bundle, resource_type=account_pb2.Account)
    self.assertEmpty(actual)

  def test_extract_resource_from_bundle_with_invalid_resource_raises(self):
    bundle = _bundle_with_single_structure_definition()
    with self.assertRaises(ValueError) as ve:
      # Use a nested message that has no mapping to ContainedResource oneof
      _ = resource_utils.extract_resources_from_bundle(
          bundle, resource_type=account_pb2.Account.StatusCode)
    self.assertIsInstance(ve.exception, ValueError)

  def test_extract_resource_from_bundle_with_non_bundle_raises(self):
    non_bundle = account_pb2.Account()
    with self.assertRaises(TypeError) as te:
      _ = resource_utils.extract_resources_from_bundle(
          non_bundle, resource_type=activity_definition_pb2.ActivityDefinition)
    self.assertIsInstance(te.exception, TypeError)

  def test_get_contained_resource_with_valid_contained_resource_succeeds(self):
    expected_account = account_pb2.Account(
        name=datatypes_pb2.String(value='TestAccount'))
    contained_resource = bundle_and_contained_resource_pb2.ContainedResource(
        account=expected_account)
    actual_account = resource_utils.get_contained_resource(contained_resource)
    self.assertEqual(actual_account, expected_account)

  def test_get_contained_resource_with_invalid_contained_resource_raises(self):
    not_contained_resource = account_pb2.Account()
    with self.assertRaises(TypeError) as te:
      _ = resource_utils.get_contained_resource(not_contained_resource)
    self.assertIsInstance(te.exception, TypeError)


if __name__ == '__main__':
  absltest.main()
