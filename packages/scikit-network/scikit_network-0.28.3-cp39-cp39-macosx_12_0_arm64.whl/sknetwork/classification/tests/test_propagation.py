#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for label propagation"""

import unittest

from sknetwork.classification import Propagation
from sknetwork.data.test_graphs import *


class TestLabelPropagation(unittest.TestCase):

    def test_algo(self):
        for adjacency in [test_graph(), test_digraph(), test_bigraph()]:
            n = adjacency.shape[0]
            seeds = {0: 0, 1: 1}
            propagation = Propagation(n_iter=3, weighted=False)
            labels = propagation.fit_predict(adjacency, seeds)
            self.assertEqual(labels.shape, (n,))

            for order in ['random', 'decreasing', 'increasing']:
                propagation = Propagation(node_order=order)
                labels = propagation.fit_predict(adjacency, seeds)
                self.assertEqual(labels.shape, (n,))
