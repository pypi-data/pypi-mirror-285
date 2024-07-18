
# MyuGPT

![PyPI - Downloads](https://img.shields.io/pypi/dm/MyuGPT)
[![PyPI - Version](https://img.shields.io/pypi/v/MyuGPT)](https://pypi.org/project/MyuGPT/)
[![codecov](https://codecov.io/gh/AdityaNG/MyuGPT/branch/main/graph/badge.svg?token=MyuGPT_token_here)](https://codecov.io/gh/AdityaNG/MyuGPT)
[![CI](https://github.com/AdityaNG/MyuGPT/actions/workflows/main.yml/badge.svg)](https://github.com/AdityaNG/MyuGPT/actions/workflows/main.yml)
[![GitHub License](https://img.shields.io/github/license/AdityaNG/MyuGPT)](https://github.com/AdityaNG/MyuGPT/blob/main/LICENSE)


MyuZero Paper: https://arxiv.org/abs/1911.08265

MyuZero uses AI guided Monte Carlo tree search to make good decisions and hence play games like Atari, Go, Chess, Shogi at a super-human level.
Tesla has shown that it has recently applied a similar approach of AI Guided Tree Search for Path Planning. The difference being, at the moment Tesla likely uses their hard-coded simulator for training (along with their large dataset of user data).
LLMs can takes the a programming problem statement as input along with the current code and its output and produces new code to process as output

There is potential to build a super human coding agent using LLMs and MyuZero

# Inspiration

![MyuZero](https://github.com/AdityaNG/MyuGPT/raw/main/media/MyuZero.png)

To summarise the MyuZero Paper, there are three neural networks:
- h(img) -> S : Environment Encoder takes an image as input and provides a latent space representation as output
- f(S) -> P,V : Policy-Value Function takes the environment state as input and produces a distribution of policies to take P, and their corresponding future reward value V.
- g(Si, Ai) -> Ri Si+1 : Dynamics Model takes a state action pair (S, A) for a given frame i as input and produces the next state Si+1 along with the reward Ri for the action Ai.
- The Environment Encoder is used to convert the sensor reading to a latent space. The Policy-Value Function is used to produce good candidate branches to explore further in the Monte Carlo Tree Search. The Dynamics Model facilitates the system to look into the future. Thus the the networks along with the Monte Carlo Tree Search framework is able to make an informed decision by looking down branches with potential and picking the one with the highest reward.

In the context of LLMs as coding agents, this is how it would translate:
- h(env) -> S : Environment Encoder takes the problem statement, current code written and the output of the compiled code and wraps it all up into a text prompt for GPT
- f(S) -> P,V : Policy-Value Function is an LLM. We would have to prompt it to produce a value as well (ask it to score itself). By varying the temperature of the model, we can sample multiple possible chains of thought and follow the most likely path
- g(Si, Ai) -> Ri Si+1 : Dynamics Model is the code interpreter which the code request from GPT as output, runs the code and updates the environment (new code and output) Monte Carlo Tree search, guided by the three networks will be used to explore potential trajectories the car can take in the near future (say 1 to 5 seconds) and the trajectory with the highest reward is picked.

What would we have to look into:
1. Prompt engineering to translate the environment to a prompt
2. We will have to look into how this reward is calulated

# Datasets

AlphaCode's Code Contests Dataset
- https://huggingface.co/datasets/deepmind/code_contests

CodeForces Dataset
- https://www.kaggle.com/datasets/immortal3/codeforces-dataset

LeetCode Dataset
- https://www.kaggle.com/datasets/gzipchrist/leetcode-problem-dataset
- 1,825 Leetcode problems and was last updated in April 2021


## Usage

```bash
$ python -m myugpt
#or
$ myugpt
```

## Development

Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.
