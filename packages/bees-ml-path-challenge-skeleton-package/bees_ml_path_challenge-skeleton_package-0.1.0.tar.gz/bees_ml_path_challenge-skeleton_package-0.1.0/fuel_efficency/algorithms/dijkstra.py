import heapq
import math
from typing import List, Dict

from fuel_efficency.algorithms.path_finding import PathfindingStrategy
from fuel_efficency.entities.node import Node
from fuel_efficency.entities.position import Position

class DijkstraStrategy(PathfindingStrategy):

    # Define the cardinal directions as positions for neighbor nodes
    cardinal_directions = [Position(-1, -1), Position(-1, 0), Position(-1, 1), Position(0, -1), Position(0, 1), Position(1, -1), Position(1, 0), Position(1, 1)]

    @staticmethod
    def find_path(grid: List[List[Node]], start: Node, end: Node) -> List[Node]:
        # Initialize the open set (priority queue) with the start node
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from: Dict[Node, Node] = {}
        cost_so_far = {start: 0}

        while open_set:
            # Pop the node with the lowest cost from the open set
            current_priority, current = heapq.heappop(open_set)

            # If the current node is the end node, reconstruct the path
            if current == end:
                return DijkstraStrategy.reconstruct_path(came_from, start, end)

            # Get the neighbors of the current node and iterate through them
            for neighbor in DijkstraStrategy.get_neighbors(grid, current):
                # Calculate the new cost to reach the neighbor
                new_cost = cost_so_far[current] + DijkstraStrategy.calculate_distance(current, neighbor)
                # If the neighbor is not in the cost_so_far or the new cost is lower, update it
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost
                    # Push the neighbor into the open set with the updated priority
                    heapq.heappush(open_set, (priority, neighbor))
                    came_from[neighbor] = current

        # Return an empty list if no path is found
        return []

    @staticmethod
    def get_neighbors(grid: List[List[Node]], node: Node) -> List[Node]:
        neighbors = []
        x, y = node.position.x, node.position.y

        # Iterate through all cardinal directions to find valid neighbors
        for direction in DijkstraStrategy.cardinal_directions:
            nx, ny = x + direction.x, y + direction.y
            if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                neighbors.append(grid[nx][ny])

        return neighbors

    @staticmethod
    def calculate_distance(node1: Node, node2: Node) -> float:
        # Calculate the Euclidean distance between two nodes
        return math.sqrt((node1.position.x - node2.position.x) ** 2 + (node1.position.y - node2.position.y) ** 2)

    @staticmethod
    def reconstruct_path(came_from: Dict[Node, Node], start: Node, end: Node) -> List[Node]:
        current = end
        path = []
        # Backtrack from the end node to the start node to reconstruct the path
        while current != start:
            path.append(current)
            current = came_from[current]
        # Reverse the path to get the correct order from start to end
        path.reverse()
        return path
