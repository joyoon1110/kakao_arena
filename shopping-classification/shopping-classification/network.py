# -*- coding: utf-8 -*-
# Copyright 2017 Kakao, Recommendation Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import tensorflow as tf

import keras
from keras.models import Model
from keras.layers.merge import dot
from keras.layers import Dense, Input
from keras.layers.core import Reshape

from keras.layers.embeddings import Embedding
from keras.layers.core import Dropout, Activation

# 모델의 층 그래프 그리기 기능 추가
from keras.utils import plot_model

from misc import get_logger, Option
opt = Option('C:/Users/Yoon-sang/kakao_arena/shopping-classification/config.json')


def top1_acc(x, y):
    return keras.metrics.top_k_categorical_accuracy(x, y, k=1)


class TextOnly:
    def __init__(self):
        self.logger = get_logger('textonly')

    def get_model(self, num_classes, activation='sigmoid'):
	    # 사용할 텍스트의 길이 = 32
        max_len = opt.max_len
		# 특성으로 사용할 단어 수(voca_size) = 100000+1
        voca_size = opt.unigram_hash_size + 1
        
		# embd_size = 256
        with tf.device('/gpu:0'):
            embd = Embedding(voca_size,
                             opt.embd_size,
                             name='uni_embd')

            t_uni = Input((max_len,), name="input_1")
            t_uni_embd = embd(t_uni)  # token

            w_uni = Input((max_len,), name="input_2")
            w_uni_mat = Reshape((max_len, 1))(w_uni)  # weight

            uni_embd_mat = dot([t_uni_embd, w_uni_mat], axes=1)
            uni_embd = Reshape((opt.embd_size, ))(uni_embd_mat)

            embd_out = Dropout(rate=0.25)(uni_embd)
            relu = Activation('relu', name='relu1')(embd_out)
            outputs = Dense(opt.embd_size, activation=activation)(relu)
            model = Model(inputs=[t_uni, w_uni], outputs=outputs)

            # 모델의 층 그래프 그리기 기능
            plot_model(model, to_file='C:/Users/Yoon-sang/kakao_arena/shopping-classification/model1.png')
            # 모델의 층 그래프 그리기 기능(크기 정보 추가)
            plot_model(model, show_shapes=True, to_file='C:/Users/Yoon-sang/kakao_arena/shopping-classification/model2.png')

            optm = keras.optimizers.Nadam(opt.lr)
            model.compile(loss='binary_crossentropy',
                        optimizer=optm,
                        metrics=[top1_acc])
            model.summary(print_fn=lambda x: self.logger.info(x))
        return model
