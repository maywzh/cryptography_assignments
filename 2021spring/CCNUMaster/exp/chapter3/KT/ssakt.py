'''
Author       : maywzh
Date         : 2021-04-01 13:08:26
LastEditTime : 2021-04-11 20:36:01
LastEditors  : maywzh
Description  : 

Stacked variant of SAKT(Self-Attentive for Knowledge Tracing)--
The SSAKT model consists of a single attention block that uses exercise embeddings as queries and interaction embeddings as keys/values. 
The authors report a decrease in AUC when the attention block is stacked multiple times. SSAKT resolves this issue 
by applying self-attention on exercises before supplying them as queries. The outputs of the exercise selfattention block and
the exercise-interaction attention block enters the corresponding following blocks as inputs for their attention layers.

FilePath     : /ji_coursenotes/2021spring/CCNUMaster/exp/chapter3/KT/ssakt.py
License      : 
Copyright (c) 2017 maywzh.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from multihead_ffn import MultiHeadWithFFN
from utils import pos_encode, get_clones, ut_mask
import config

import torch
from torch import nn


class SSAKT(nn.Module):
    def __init__(self, n_encoder, n_decoder, enc_heads, dec_heads, total_ex, n_dims, total_cat, total_responses, seq_len, max_time=300+1):
        super(SSAKT, self).__init__()
        self.n_encoder = n_encoder
        self.n_decoder = n_decoder
        self.encoder = get_clones(EncoderBlock(
            enc_heads, n_dims, total_ex, total_cat, seq_len, max_time), n_encoder)
        self.exercise_block = ExerciseBlock(
            dec_heads, n_dims, total_ex, seq_len)
        self.fc = nn.Linear(n_dims, 1)

    def forward(self, in_exercise, in_category, in_response, in_etime):
        first_block = True
        categories = in_category
        print(in_exercise.shape)
        exercise = self.exercise_block(input_e=in_exercise)
        for n in range(self.n_encoder):
            if n >= 1:
                first_block = False
            enc = self.encoder[n](in_exercise, in_category, in_etime,
                                  in_response, exercise, first_block=first_block)
            in_exercise = enc
            in_category = enc
            in_etime = enc
        return torch.sigmoid(self.fc(enc)
                             )


class EncoderBlock(nn.Module):
    def __init__(self, n_heads, n_dims, total_ex, total_cat, seq_len, time_width):
        super(EncoderBlock, self).__init__()
        self.seq_len = seq_len
        self.exercise_embed = nn.Embedding(total_ex, n_dims)
        self.category_embed = nn.Embedding(total_cat, n_dims)
        self.position_embed = nn.Embedding(seq_len, n_dims)
        self.response_embed = nn.Embedding(total_ex, n_dims)
        self.elapsetime_embed = nn.Embedding(time_width, n_dims)
        self.layer_norm = nn.LayerNorm(n_dims)

        self.multihead = MultiHeadWithFFN(n_heads=n_heads,
                                          n_dims=n_dims)

    def forward(self, input_e, category, elapse_time, response, exercise, first_block=True):
        if first_block:
            _exe = self.exercise_embed(input_e)
            _cat = self.category_embed(category)
            _etime = self.elapsetime_embed(elapse_time)
            _response = self.response_embed(response)
            position_encoded = pos_encode(self.seq_len-1)
            if config.device == "cuda":
                position_encoded = position_encoded.cuda()

            _pos = self.position_embed(position_encoded)

            interaction = _cat + _exe + _etime + _response + _pos
        else:
            interaction = input_e
        output = self.multihead(q_input=exercise, kv_input=interaction)
        return output


class ExerciseBlock(nn.Module):
    def __init__(self, n_heads, n_dims, total_exercise, seq_len):
        super(ExerciseBlock, self).__init__()
        self.seq_len = seq_len
        self.exercise_embed = nn.Embedding(total_exercise, n_dims)
        self.position_embed = nn.Embedding(seq_len, n_dims)
        self.layer_norm = nn.LayerNorm(n_dims)
        self.multihead = MultiHeadWithFFN(n_heads=n_heads,
                                          n_dims=n_dims)

    def forward(self, input_e):
        _exe = self.exercise_embed(input_e)
        position_encoded = pos_encode(self.seq_len-1)
        if config.device == "cuda":
            position_encoded = position_encoded.cuda()
        _pos = self.position_embed(position_encoded)
        exercise = _exe + _pos
        out_norm = self.layer_norm(exercise)
        output = self.multihead(q_input=exercise, kv_input=exercise)
        output += out_norm
        return output
