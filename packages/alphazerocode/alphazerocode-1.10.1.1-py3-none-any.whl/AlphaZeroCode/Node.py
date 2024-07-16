#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @title Node

""" Import libraries Original """
import copy

class Node():
    """
    Node: Represents a game state
    """
    def __init__(self, CFG, state=None):
        self.states = None
        self.is_root = False
        self.child_nodes = []
        self.action = None
        self.actions = [0] * CFG.history_size # for one-hot
        self.player = CFG.first_player
        self.input_features = None
        self.test = "default"
        self.CFG = CFG

        if state:
            self.set_default_states(state)

        """ Edge """
        self.n = 0 # 訪問回数 (visit count)
        self.w = 0 # 累計行動価値 (total action-value)
        self.p = 0 # 事前確率 (prior probability)
        self.Q = 0 # 平均行動価値 (action-value)

    def set_default_states(self, state):
        state = copy.deepcopy(state) 
        w = self.CFG.board_width
        h = self.CFG.history_size #
        self.states = [[[0 for i in range(w)] for j in range(w)] for _ in range(h)]
        self.states.insert(0,state)
        self.states.pop(-1)
