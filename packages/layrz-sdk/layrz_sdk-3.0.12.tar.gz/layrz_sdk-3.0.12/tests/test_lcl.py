"""
Test LCL functions
"""

import json
import unittest
import zoneinfo
from datetime import datetime
from typing import Any

from layrz_sdk.lcl.core import LclCore


class TestLclFunctions(unittest.TestCase):
  """Test LCL functions"""

  def _process_and_convert(self, lcl: LclCore) -> Any:
    result = lcl.perform()
    try:
      result = json.loads(result)
    except json.JSONDecodeError:
      pass

    return result

  def test_GET_PARAM(self) -> None:
    formula = 'GET_PARAM("test.param", None)'
    lcl = LclCore(script=formula, payload={'test.param': 10})
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 10.0)

    lcl = LclCore(script=formula, payload={})
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_GET_SENSOR(self) -> None:
    formula = 'GET_SENSOR("test.sensor", None)'
    lcl = LclCore(script=formula, sensors={'test.sensor': 10})
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 10.0)

    lcl = LclCore(script=formula, sensors={})
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_CONSTANT(self) -> None:
    formula = 'CONSTANT(True)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    lcl = LclCore(script='CONSTANT(False)')
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    lcl = LclCore(script='CONSTANT(None)')
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

    lcl = LclCore(script='CONSTANT(10)')
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 10.0)

  def test_GET_CUSTOM_FIELD(self) -> None:
    formula = 'GET_CUSTOM_FIELD("test.custom_field")'
    lcl = LclCore(script=formula, custom_fields={'test.custom_field': 10})
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 10.0)

    lcl = LclCore(script=formula, custom_fields={})
    result = self._process_and_convert(lcl)
    self.assertEqual(result, '')

  def test_COMPARE(self) -> None:
    formula = 'COMPARE(CONSTANT(10), CONSTANT(10))'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'COMPARE(CONSTANT(10), None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

    formula = 'COMPARE(CONSTANT(10), None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

    formula = 'COMPARE(CONSTANT(10), CONSTANT(20))'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

  def test_OR_OPERATOR(self) -> None:
    formula = 'OR_OPERATOR(CONSTANT(True), CONSTANT(False))'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'OR_OPERATOR(CONSTANT(False), CONSTANT(False))'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    formula = 'OR_OPERATOR(CONSTANT(True), CONSTANT(True))'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'OR_OPERATOR(CONSTANT(False), CONSTANT(None))'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_AND_OPERATOR(self) -> None:
    formula = 'AND_OPERATOR(CONSTANT(True), CONSTANT(False))'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    formula = 'AND_OPERATOR(CONSTANT(False), CONSTANT(False))'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    formula = 'AND_OPERATOR(CONSTANT(True), CONSTANT(True))'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'AND_OPERATOR(CONSTANT(False), CONSTANT(None))'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_SUM(self) -> None:
    formula = 'SUM(CONSTANT(10), CONSTANT(20))'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 30.0)

    formula = 'SUM(CONSTANT(10), None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_SUBSTRACT(self) -> None:
    formula = 'SUBSTRACT(CONSTANT(10), CONSTANT(20))'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, -10.0)

    formula = 'SUBSTRACT(CONSTANT(20), CONSTANT(10))'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 10.0)

    formula = 'SUBSTRACT(CONSTANT(10), None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_MULTIPLY(self) -> None:
    formula = 'MULTIPLY(CONSTANT(10), CONSTANT(20))'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 200.0)

    formula = 'MULTIPLY(CONSTANT(20), CONSTANT(10))'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 200.0)

    formula = 'MULTIPLY(CONSTANT(10), None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_DIVIDE(self) -> None:
    formula = 'DIVIDE(CONSTANT(10), CONSTANT(20))'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 0.5)

    formula = 'DIVIDE(CONSTANT(20), CONSTANT(10))'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 2.0)

    formula = 'DIVIDE(CONSTANT(10), None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_TO_BOOL(self) -> None:
    formula = 'TO_BOOL(1)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'TO_BOOL(0)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    formula = 'TO_BOOL(None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

    formula = 'TO_BOOL("True")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'TO_BOOL("False")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)  # Why? Simple, any filled str is True

  def test_TO_STR(self) -> None:
    formula = 'TO_STR(1)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, '1')

    formula = 'TO_STR(1.1)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, '1.1')

    formula = 'TO_STR(True)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 'True')

    formula = 'TO_STR(None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_TO_INT(self) -> None:
    formula = 'TO_INT(1.5)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 1)

    formula = 'TO_INT("1")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 1)

    formula = 'TO_INT(True)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 1)

    formula = 'TO_INT(None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_CEIL(self) -> None:
    formula = 'CEIL(1.2)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 2)

    formula = 'CEIL(1.5)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 2)

    formula = 'CEIL("hola")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 'Invalid arguments - must be real number, not str')

    formula = 'CEIL(True)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 1)

    formula = 'CEIL(None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_FLOOR(self) -> None:
    formula = 'FLOOR(1.2)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 1)

    formula = 'FLOOR(1.5)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 1)

    formula = 'FLOOR("hola")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 'Invalid arguments - must be real number, not str')

    formula = 'FLOOR(True)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 1)

    formula = 'FLOOR(None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_ROUND(self) -> None:
    formula = 'ROUND(1.2)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 1)

    formula = 'ROUND(1.5)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 2)

    formula = 'ROUND("hola")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 'Invalid arguments - must be real number, not str')

    formula = 'ROUND(True)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 1)

    formula = 'ROUND(None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_SQRT(self) -> None:
    formula = 'SQRT(4)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 2)

    formula = 'SQRT(9)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 3)

    formula = 'SQRT("hola")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 'Invalid arguments - must be real number, not str')

    formula = 'SQRT(True)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 1)

    formula = 'SQRT(None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_CONCAT(self) -> None:
    formula = 'CONCAT("Hello", " ", "World")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 'Hello World')

    formula = 'CONCAT("Hello", None, "World")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

    formula = 'CONCAT("Hello", 10, "World")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 'Hello10World')

    formula = 'CONCAT("Hello", True, "World")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 'HelloTrueWorld')

  def test_NOW(self) -> None:
    formula = 'NOW()'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertIsInstance(result, (int, float))

  def test_RANDOM(self) -> None:
    formula = 'RANDOM(0, 1)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertIsInstance(result, float)
    self.assertGreaterEqual(result, 0.0)
    self.assertLessEqual(result, 1.0)

  def test_RANDOM_INT(self) -> None:
    formula = 'RANDOM_INT(1, 3)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertIsInstance(result, int)
    self.assertGreaterEqual(result, 1)
    self.assertLessEqual(result, 3)

  def test_GREATER_THAN_OR_EQUALS_TO(self) -> None:
    formula = 'GREATER_THAN_OR_EQUALS_TO(10, 10)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'GREATER_THAN_OR_EQUALS_TO(10, 20)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    formula = 'GREATER_THAN_OR_EQUALS_TO(20, 10)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'GREATER_THAN_OR_EQUALS_TO(10, None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

    formula = 'GREATER_THAN_OR_EQUALS_TO(None, 10)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_GREATER_THAN(self) -> None:
    formula = 'GREATER_THAN(10, 10)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    formula = 'GREATER_THAN(10, 20)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    formula = 'GREATER_THAN(20, 10)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'GREATER_THAN(10, None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

    formula = 'GREATER_THAN(None, 10)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_LESS_THAN_OR_EQUALS_TO(self) -> None:
    formula = 'LESS_THAN_OR_EQUALS_TO(10, 10)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'LESS_THAN_OR_EQUALS_TO(10, 20)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'LESS_THAN_OR_EQUALS_TO(20, 10)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    formula = 'LESS_THAN_OR_EQUALS_TO(10, None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

    formula = 'LESS_THAN_OR_EQUALS_TO(None, 10)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_LESS_THAN(self) -> None:
    formula = 'LESS_THAN(10, 10)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    formula = 'LESS_THAN(10, 20)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'LESS_THAN(20, 10)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    formula = 'LESS_THAN(10, None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

    formula = 'LESS_THAN(None, 10)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_DIFFERENT(self) -> None:
    formula = 'DIFFERENT(10, 10)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    formula = 'DIFFERENT(10, 20)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'DIFFERENT(20, 10)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'DIFFERENT(10, None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

    formula = 'DIFFERENT(None, 10)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

    formula = 'DIFFERENT("Hola", 10)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 'Invalid data types - arg1: str - arg2: float')

  def test_HEX_TO_STR(self) -> None:
    formula = 'HEX_TO_STR("48656c6c6f")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 'Hello')

    formula = 'HEX_TO_STR("0x48656c6c6f")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 'Hello')

    formula = 'HEX_TO_STR("1")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 'Invalid hex string')

  def test_STR_TO_HEX(self) -> None:
    formula = 'STR_TO_HEX("Hello")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, '48656c6c6f')

  def test_HEX_TO_INT(self) -> None:
    formula = 'HEX_TO_INT("0xff")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 255)

    formula = 'HEX_TO_INT("0x1")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 1)

    formula = 'HEX_TO_INT("Helo")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 'Invalid hex string')

  def test_INT_TO_HEX(self) -> None:
    formula = 'INT_TO_HEX(15)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 'f')

    formula = 'INT_TO_HEX(1)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, '1')

    formula = 'INT_TO_HEX("Hello")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 'Invalid int value')

  def test_TO_FLOAT(self) -> None:
    formula = 'TO_FLOAT(0)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 0.0)

    formula = 'TO_FLOAT(1)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 1.0)

    formula = 'TO_FLOAT(1.1)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 1.1)

    formula = 'TO_FLOAT("Hello")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 'Invalid arguments - must be real number, not str')

  def test_GET_DISTANCE_TRAVELED(self) -> None:
    formula = 'GET_DISTANCE_TRAVELED()'
    lcl = LclCore(script=formula, asset_constants={'distanceTraveled': 10})
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 10.0)

    lcl = LclCore(script=formula, asset_constants={})
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 0.0)

  def test_GET_PREVIOUS_SENSOR(self) -> None:
    formula = 'GET_PREVIOUS_SENSOR("test.sensor")'
    lcl = LclCore(script=formula, previous_sensors={'test.sensor': 10})
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 10.0)

    lcl = LclCore(script=formula, previous_sensors={})
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_IS_PARAMETER_PRESENT(self) -> None:
    formula = 'IS_PARAMETER_PRESENT("test.param")'
    lcl = LclCore(script=formula, payload={'test.param': 10})
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    lcl = LclCore(script=formula, payload={})
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

  def test_IS_SENSOR_PRESENT(self) -> None:
    formula = 'IS_SENSOR_PRESENT("test.sensor")'
    lcl = LclCore(script=formula, sensors={'test.sensor': 10})
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    lcl = LclCore(script=formula, sensors={})
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

  def test_INSIDE_RANGE(self) -> None:
    formula = 'INSIDE_RANGE(10, 20, 30)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    formula = 'INSIDE_RANGE(10, 5, 30)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'INSIDE_RANGE(10, 5, 15)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'INSIDE_RANGE(None, 15, 30)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

    formula = 'INSIDE_RANGE(10, None, 30)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

    formula = 'INSIDE_RANGE(10, 15, None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_OUTSIDE_RANGE(self) -> None:
    formula = 'OUTSIDE_RANGE(10, 20, 30)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'OUTSIDE_RANGE(10, 5, 30)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    formula = 'OUTSIDE_RANGE(10, 5, 15)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    formula = 'OUTSIDE_RANGE(None, 15, 30)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

    formula = 'OUTSIDE_RANGE(10, None, 30)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

    formula = 'OUTSIDE_RANGE(10, 15, None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_GET_TIME_DIFFERENCE(self) -> None:
    formula = 'GET_TIME_DIFFERENCE()'
    lcl = LclCore(script=formula, asset_constants={'timeElapsed': 10})
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 10)

    lcl = LclCore(script=formula, asset_constants={})
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 0)

  def test_IF(self) -> None:
    formula = 'IF(True, 10, 20)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 10.0)

    formula = 'IF(False, 10, 20)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 20.0)

    formula = 'IF(None, 10, 20)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

    formula = 'IF(True, None, 20)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

    formula = 'IF(False, 10, None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_REGEX(self) -> None:
    formula = 'REGEX("1. Hello world", "^[0-9]+\\.\\s")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'REGEX("1. Hello world", "^[0-9]+\\s")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    formula = 'REGEX("Hello world", "^[0-9]+\\s")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    formula = 'REGEX("Hello world", None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

    formula = 'REGEX(None, "^[0-9]+\\s")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_IS_NONE(self) -> None:
    formula = 'IS_NONE(None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'IS_NONE(10)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

  def test_NOT(self) -> None:
    formula = 'NOT(True)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    formula = 'NOT(False)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'NOT(None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

    formula = 'NOT(10)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

  def test_CONTAINS(self) -> None:
    formula = 'CONTAINS("Hello", "Hello World")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'CONTAINS("World", "Hello World")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'CONTAINS("Hello World", 15)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    formula = 'CONTAINS("Hello World", None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_STARTS_WITH(self) -> None:
    formula = 'STARTS_WITH("Hello", "Hello World")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'STARTS_WITH("World", "Hello World")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    formula = 'STARTS_WITH("Hello World", 15)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    formula = 'STARTS_WITH("Hello World", None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_ENDS_WITH(self) -> None:
    formula = 'ENDS_WITH("World", "Hello World")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, True)

    formula = 'ENDS_WITH("Hello", "Hello World")'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    formula = 'ENDS_WITH("Hello World", 15)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, False)

    formula = 'ENDS_WITH("Hello World", None)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_PRIMARY_DEVICE(self) -> None:
    formula = 'PRIMARY_DEVICE()'
    lcl = LclCore(script=formula, asset_constants={'primaryDevice': 'test'})
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 'test')

    formula = 'PRIMARY_DEVICE()'
    lcl = LclCore(script=formula, asset_constants={})
    result = self._process_and_convert(lcl)
    self.assertEqual(result, None)

  def test_SUBSTRING(self) -> None:
    formula = 'SUBSTRING("Hello World", 0, 5)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 'Hello')

    formula = 'SUBSTRING("Hello World", 6)'
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, 'World')

  def test_UNIX_TO_STR(self) -> None:
    formula = 'UNIX_TO_STR(NOW(), "%Y_%m_%d", "UTC")'
    now = datetime.now(zoneinfo.ZoneInfo('UTC'))
    lcl = LclCore(script=formula)
    result = self._process_and_convert(lcl)
    self.assertEqual(result, now.strftime('%Y_%m_%d'))


if __name__ == '__main__':
  unittest.main()
