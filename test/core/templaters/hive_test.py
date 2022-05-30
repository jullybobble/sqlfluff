"""Tests for templaters."""

from sqlfluff.core.templaters.hive import HiveTemplater

def test__set_hivevar():
    t = HiveTemplater(override_context={'w': '2'})
    instr = """SET hivevar:v = 1;
SELECT ${v} ${w};"""
    outstr, _ = t.process(
        in_str=instr, fname='test'
    )
    assert str(outstr.templated_str).strip() == "SELECT 1 2;"
