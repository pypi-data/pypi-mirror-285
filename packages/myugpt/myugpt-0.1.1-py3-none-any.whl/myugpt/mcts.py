"""Monte Carlo Tree Search implementation"""

import math
import random

import numpy as np

from myugpt.code_env import validate_code
from myugpt.gpt import MyuGPT
from myugpt.schema import CodingEnv, ModelPrediction, Node


def uct_select(node: Node, exploration_weight=1.4) -> Node:
    # Select a child node with the highest UCT value
    # UCT = (wins/visits) + C * sqrt(log(parent.visits)/visits)
    # C is a constant determining the level of exploration
    assert len(node.children) > 0, "No children to select."
    best_value = float("-inf")
    # best_node = None
    for child in node.children:
        uct_value = child.wins / child.visits + exploration_weight * math.sqrt(
            2 * math.log(node.visits) / child.visits
        )
        if uct_value > best_value:
            best_value = uct_value
            best_node = child
    return best_node


def validate_and_score(
    node: Node,
    action: ModelPrediction,
):
    inputs = node.state.dataset_frame.inputs
    expected_outputs = node.state.dataset_frame.expected_outputs
    # Validate the code and calculate the score
    validation = validate_code(
        action,
        inputs,
        expected_outputs,
    )
    next_state = CodingEnv(
        **node.state.model_dump().copy(),
    )
    next_state.model_predictions.append(
        action,
    )
    next_state.validation = validation
    reward = next_state.score

    return next_state, reward


def expand(node: Node, gpt: MyuGPT, expand_size: int):
    # Add all possible next states as children to the node
    actions = gpt.sample(node.state, num_samples=expand_size)
    node.untried_actions = actions

    for action in node.untried_actions:
        next_state, _ = validate_and_score(
            node,
            action,
        )

        child_node = Node(state=next_state, parent=node)
        node.children.append(child_node)


def is_terminal(node: Node):
    # Check if the node is terminal node (i.e. no more actions possible)
    return np.isclose(node.state.score, 100.0, atol=1e-2)


def simulate(node: Node, gpt: MyuGPT):
    # Simulate a random playout from the node's state until a result is reached
    current_node = node
    while not is_terminal(current_node):
        possible_actions = gpt.sample(
            current_node.state,
        )
        action = random.choice(possible_actions)
        next_state, reward = validate_and_score(
            node,
            action,
        )

        current_node = Node(state=next_state)
        current_node.wins += reward  # Update the reward
    return current_node.wins


def backpropagate(node: Node, result: int):
    # Update the win/visit counts from the node to the root
    while node is not None:
        node.visits += 1
        node.wins += result
        node = node.parent


def mcts(root_env: CodingEnv, iterations: int, gpt: MyuGPT, expand_size: int):
    root = Node(state=root_env)
    expand(root, gpt, expand_size=expand_size)
    for _ in range(iterations):
        # Selection
        leaf = uct_select(root)

        # Expansion
        if not is_terminal(leaf):
            expand(leaf, gpt, expand_size=expand_size)

        # Simulation
        simulation_result = simulate(leaf, gpt)

        # Backpropagation
        backpropagate(leaf, simulation_result)

    # Return the action that leads to the best child of the root
    return max(root.children, key=lambda c: c.wins / c.visits).state
