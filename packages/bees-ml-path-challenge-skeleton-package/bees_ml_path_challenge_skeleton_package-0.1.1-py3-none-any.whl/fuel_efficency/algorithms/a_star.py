import heapq
import math
from typing import List, Dict

from fuel_efficency.algorithms.path_finding import PathfindingStrategy
from fuel_efficency.entities.node import Node
from fuel_efficency.entities.position import Position

class AStarStrategy(PathfindingStrategy):

    # Define the allowed directions for movement as positions
    allowed_directions = [Position(-1, 0), Position(0, -1), Position(0, 1), Position(1, 0)]

    @staticmethod
    def find_path(grid: List[List[Node]], start: Node, end: Node) -> List[Node]:
        # Initialize the open set (priority queue) with the start node
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from: Dict[Node, Node] = {}
        g_score = {start: 0}  # Cost from start to the current node
        f_score = {start: AStarStrategy.heuristic(start, end)}  # Estimated cost from start to end through the current node

        while open_set:
            # Pop the node with the lowest f_score from the open set
            _, current = heapq.heappop(open_set)

            # If the current node is the end node, reconstruct the path
            if current == end:
                path = AStarStrategy.reconstruct_path(came_from, start, end)
                return path[1:]  # Omitting the start position

            # Get the neighbors of the current node
            for neighbor in AStarStrategy.get_neighbors(grid, current):
                # Calculate the tentative g_score for the neighbor
                tentative_g_score = g_score[current] + AStarStrategy.calculate_distance(current, neighbor)
                # If the neighbor is not in g_score or the new g_score is lower, update it
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + AStarStrategy.heuristic(neighbor, end)
                    # Push the neighbor into the open set if it's not already in it
                    if neighbor not in [i[1] for i in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        # Return an empty list if no path is found
        return []

    @staticmethod
    def get_neighbors(grid: List[List[Node]], node: Node) -> List[Node]:
        neighbors = []
        x, y = node.position.x, node.position.y

        # Iterate through all allowed directions to find valid neighbors
        for direction in AStarStrategy.allowed_directions:
            nx, ny = x + direction.x, y + direction.y
            if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                neighbors.append(grid[nx][ny])

        return neighbors

    @staticmethod
    def calculate_distance(node1: Node, node2: Node) -> float:
        # Calculate the Manhattan distance between two nodes
        return abs(node1.position.x - node2.position.x) + abs(node1.position.y - node2.position.y)

    @staticmethod
    def heuristic(node1: Node, node2: Node) -> float:
        # Calculate the heuristic (estimated cost) using the Manhattan distance
        return abs(node1.position.x - node2.position.x) + abs(node1.position.y - node2.position.y)

    @staticmethod
    def reconstruct_path(came_from: Dict[Node, Node], start: Node, end: Node) -> List[Node]:
        current = end
        path = []
        # Backtrack from the end node to the start node to reconstruct the path
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)
        # Reverse the path to get the correct order from start to end
        path.reverse()
        return path
