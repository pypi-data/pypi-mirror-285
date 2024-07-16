#
# Copyright 2020 Google LLC
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
"""Test fhir_types functionality."""

from absl.testing import absltest
from google.fhir.r4.proto import fhirproto_extensions_pb2
from google.fhir.r4.proto import uscore_pb2
from google.fhir.r4.proto.core import datatypes_pb2
from google.fhir.r4.proto.core.resources import patient_pb2
from google.fhir.core.utils import fhir_types


class FhirTypesTest(absltest.TestCase):
  """Tests functionality provided by the fhir_types module."""

  def test_is_code_with_code_returns_true(self):
    """Tests that is_code returns True when given a Code."""
    self.assertTrue(fhir_types.is_code(datatypes_pb2.Code()))

  def test_is_code_with_profile_of_code_returns_false(self):
    """Tests that is_code returns False when given a profile of Code."""
    self.assertFalse(fhir_types.is_code(datatypes_pb2.Address.UseCode()))

  def test_is_profile_of_code_with_profile_of_code_returns_true(self):
    """Tests that is_profile_of_code returns True for a profile of Code."""
    self.assertTrue(
        fhir_types.is_profile_of_code(datatypes_pb2.Address.UseCode()))

  def test_is_profile_of_code_with_code_returns_false(self):
    """Tests that is_profile_of_code returns False for a base Code."""
    self.assertFalse(fhir_types.is_profile_of_code(datatypes_pb2.Code()))

  def test_is_type_or_profile_of_code_with_profile_of_code_returns_true(self):
    """Tests that is_type_or_profile_of_code returns True for a profile."""
    self.assertTrue(
        fhir_types.is_type_or_profile_of_code(datatypes_pb2.Address.UseCode()))

  def test_is_type_or_profile_of_code_with_code_returns_true(self):
    """Tests that is_type_or_profile_of_code returns True for a base Code."""
    self.assertTrue(fhir_types.is_type_or_profile_of_code(datatypes_pb2.Code()))

  def test_is_type_or_profile_of_code_with_non_code_returns_false(self):
    """Tests that is_type_or_profile_of_code returns False for a non-Code."""
    self.assertFalse(
        fhir_types.is_type_or_profile_of_code(patient_pb2.Patient()))

  def test_is_coding_with_coding_returns_true(self):
    """Tests that is_coding returns True when given a Coding instance."""
    self.assertTrue(fhir_types.is_coding(datatypes_pb2.Coding()))

  def test_is_coding_with_profile_of_coding_returns_false(self):
    """Tests that is_coding returns False when given a profile."""
    self.assertFalse(fhir_types.is_coding(datatypes_pb2.CodingWithFixedCode()))

  def test_is_profile_of_coding_with_coding_returns_true(self):
    """Tests that is_profile_of_coding returns True for a profile."""
    self.assertTrue(
        fhir_types.is_profile_of_coding(datatypes_pb2.CodingWithFixedCode()))

  def test_is_profile_of_coding_with_coding_returns_false(self):
    """Tests that is_profile_of_coding returns False for a base Coding type."""
    self.assertFalse(fhir_types.is_profile_of_coding(datatypes_pb2.Coding()))

  def test_is_type_or_profile_of_coding_with_coding_returns_true(self):
    """Tests that is_type_or_profile_of_coding returns True for profile."""
    self.assertTrue(
        fhir_types.is_type_or_profile_of_coding(
            datatypes_pb2.CodingWithFixedCode()))

  def test_is_type_or_profile_of_coding_with_non_coding_returns_false(self):
    """Tests that is_type_or_profile_of_coding returns False for non-Coding."""
    self.assertFalse(
        fhir_types.is_type_or_profile_of_coding(patient_pb2.Patient()))

  def test_is_period_with_period_returns_true(self):
    """Tests that is_period returns True when given a Period instance."""
    self.assertTrue(fhir_types.is_period(datatypes_pb2.Period()))

  def test_is_period_with_coding_returns_false(self):
    """Tests that is_period returns False when given a profile of Coding."""
    self.assertFalse(fhir_types.is_period(datatypes_pb2.Coding()))

  def test_is_date_time_with_date_time_returns_true(self):
    """Tests that is_date_time returns True when given a DateTime instance."""
    self.assertTrue(fhir_types.is_date_time(datatypes_pb2.DateTime()))

  def test_is_date_time_with_coding_returns_false(self):
    """Tests that is_date_time returns False when given a profile of Coding."""
    self.assertFalse(fhir_types.is_date_time(datatypes_pb2.Coding()))

  def test_is_boolean_with_boolean_returns_true(self):
    """Tests that is_boolean returns True when given a Boolean instance."""
    self.assertTrue(fhir_types.is_boolean(datatypes_pb2.Boolean()))

  def test_is_boolean_with_coding_returns_false(self):
    """Tests that is_boolean returns False when given a profile of Coding."""
    self.assertFalse(fhir_types.is_boolean(datatypes_pb2.Coding()))

  def test_is_string_with_string_returns_true(self):
    """Tests that is_string returns True when given a String instance."""
    self.assertTrue(fhir_types.is_string(datatypes_pb2.String()))

  def test_is_string_with_coding_returns_false(self):
    """Tests that is_date_time returns False when given a profile of Coding."""
    self.assertFalse(fhir_types.is_string(datatypes_pb2.Coding()))

  def test_is_extension_with_extension_returns_true(self):
    """Tests that is_extension returns True when given an Extension."""
    self.assertTrue(fhir_types.is_extension(datatypes_pb2.Extension()))

  def test_is_extension_with_date_time_returns_false(self):
    """Tests that is_extension returns False when given a DateTime."""
    self.assertFalse(fhir_types.is_extension(datatypes_pb2.DateTime()))

  def test_is_profile_of_extension_with_base64_binary_separator_stride_returns_true(
      self,
  ):
    """Tests that is_profile_of_extension returns True for valid profile."""
    self.assertTrue(
        fhir_types.is_profile_of_extension(
            fhirproto_extensions_pb2.Base64BinarySeparatorStride()))

  def test_is_type_or_profile_of_extension_with_extension_returns_true(self):
    """Tests that is_type_or_profile_of_extension returns True for Extension."""
    self.assertTrue(
        fhir_types.is_type_or_profile_of_extension(datatypes_pb2.Extension()))

  def test_is_type_or_profile_of_extension_with_extension_profile_returns_true(
      self,
  ):
    """Tests that is_type_or_profile_of_extension returns True for  profile."""
    self.assertTrue(
        fhir_types.is_type_or_profile_of_extension(
            fhirproto_extensions_pb2.Base64BinarySeparatorStride()))

  def test_is_type_or_profile_of_extensions_with_date_time_returns_false(self):
    """Tests that is_type_or_profile_of_extension returns False for DateTime."""
    self.assertFalse(
        fhir_types.is_type_or_profile_of_extension(datatypes_pb2.DateTime()))

  def test_is_type_or_profile_of_patient_with_patient_returns_true(self):
    """Tests that IsTypeOfProfileOfPatient returns True for a Patient type."""
    self.assertTrue(
        fhir_types.is_type_or_profile_of_patient(patient_pb2.Patient()))

  def test_is_type_or_profile_of_patient_with_coding_returns_false(self):
    """Tests that IsTypeOfProfileOfPatient returns False for a Coding type."""
    self.assertFalse(
        fhir_types.is_type_or_profile_of_patient(datatypes_pb2.Coding()))

  def test_is_type_or_profile_of_patient_with_patient_profile_returns_true(
      self,
  ):
    """Tests that IsTypeOfProfileOfPatient returns True for Patient profile."""
    self.assertTrue(
        fhir_types.is_type_or_profile_of_patient(
            uscore_pb2.USCorePatientProfile()))


if __name__ == '__main__':
  absltest.main()
