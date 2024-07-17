#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""tests for push_relabel.py"""
import unittest

from sknetwork.flow import get_max_flow, find_excess
from scipy import sparse

class TestFlow(unittest.TestCase):
    def test_push_relabel_1(self):
        adj = sparse.csr_matrix([[0, 2, 3, 0, 0, 0, 0], [0, 0, 0, 3, 0, 0, 0],
        [0, 0, 0, 2, 0, 0, 0], [0, 0, 0, 0, 1, 3, 0], [0, 0, 0, 0, 0, 0, 2],
        [0, 0, 0, 0, 0, 0, 2], [0, 0, 0, 0, 0, 0, 0]])
        flow = get_max_flow(adj, 0, 6)
        self.assertEqual(3, flow[:, 6].sum())
        for i in range(1, 6):
            self.assertEqual(0, find_excess(flow, i))
