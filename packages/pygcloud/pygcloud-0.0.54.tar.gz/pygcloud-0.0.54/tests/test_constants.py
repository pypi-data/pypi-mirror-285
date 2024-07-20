"""
@author: jldupont
"""
from pygcloud.constants import Instruction


def test_instruction():

    i = Instruction.ABORT_DEPLOY_ALL

    assert i.is_abort()
