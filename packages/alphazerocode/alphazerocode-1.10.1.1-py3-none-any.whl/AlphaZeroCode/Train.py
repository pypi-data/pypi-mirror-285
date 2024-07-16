#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @title Train

import math
import random
import copy
from tqdm import tqdm

""" Import PyTorch framework """
import torch
import torch.nn as nn
import torch.optim as optim

from . Util import Util

class Train():
    
    def __init__(self, model, CFG):
        self.model = model
        self.CFG = CFG
        self.util = Util(CFG)
        self.running_loss_policy = 0.0
        self.running_loss_value = 0.0
        self.epoch_loss = 0.0
        self.learning_rate = None
        self.num_epoch = CFG.num_epoch

        self.optimizer = optim.SGD(self.model.parameters(), 
                                   lr=CFG.learning_rate, 
                                   momentum=0.9, 
                                   weight_decay=CFG.weight_decay)

        self.util.save_model_info()

    def __call__(self, dataset):

        self.model.train()

        batch_iteration_size = math.ceil(len(dataset) / self.CFG.batch_size)

        if batch_iteration_size == 0:
            batch_iteration_size = 1

        """ Train loop """
        for epoch in (range(1, self.num_epoch + 1)):

            """ 全データセットをシャッフル """
            dataset = random.sample(dataset, len(dataset)) # 再定義しているので問題ない

            # iteration_size = math.ceil(len(dataset) / self.CFG.batch_size)

            for i in range(0, len(dataset), self.CFG.batch_size):
                input_features, pi, z = self.util.make_batch(dataset[i:i + self.CFG.batch_size])
                self.update(input_features, pi, z)

            self.util.output_train_log(epoch, self.running_loss_policy, self.running_loss_value, batch_iteration_size)

            self.running_loss_policy = 0.0
            self.running_loss_value = 0.0


    def update(self, input_features,  pi, z):
        """ 
        define (z - v)^2 - pi * log(p) + c||θ||2
        """

        """ Predict policy and state value """
        p, v = self.model(input_features)

        """ Categorical Cross-entropy Error """
        p = p + 1e-10
        policy_loss = -(pi * torch.log(p)).sum(dim=1).mean()

        """ Mean Square Error """
        value_loss = (z - v).pow(2).mean()

        """ L2 regularization c||θ||2 """
        """ weight decayとして、optimizerに組み込まれています。"""
      
        
        """ Loss function """
        loss = policy_loss + value_loss

        """ Update network paramters. """
        self.optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.model.parameters(), 0.5)
        self.optimizer.step()

        """ Running loss """
        self.running_loss_policy += policy_loss
        self.running_loss_value += value_loss
