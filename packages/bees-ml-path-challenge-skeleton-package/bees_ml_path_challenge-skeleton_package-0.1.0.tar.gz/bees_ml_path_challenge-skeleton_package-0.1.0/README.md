# Fuel Efficiency Path Challenge

## Overview

Welcome to the Fuel Efficiency Path Challenge! In this coding exercise, you are tasked with implementing a series of entities and algorithms to map the most fuel-efficient path through various terrains. This challenge is designed to assess your skills in algorithm implementation, object-oriented programming, and problem-solving.

**NOTE**: Do NOT modify the tests in the `tests` folder. These tests are used to verify your code and should not be changed. 

## Solution Submission
Ensure your submission is zipped/compressed, does NOT change the tests, AND includes your `.git` file.

## Challenge Description

Your mission involves two key components: `entities` and `algorithms`. These are represented as two separate folders in the repository. Each folder contains files that define the structure and requirements of components you need to implement.

### Entities

The `entities` folder contains definitions for different objects in a grid that represents various terrains. Your task is to implement the functionality of these entities. The entities include:

- `DownHill`
- `Valley`
- `Position`
- `UpHill`
- `Node`
- `Plateau`

Each of these entities plays a role in the simulation of a vehicle moving through different terrains, affecting its fuel efficiency.

### Algorithms

The `algorithms` folder includes files that describe algorithms for pathfinding. These algorithms will be used to determine the most efficient path through the grid considering the different terrains. The algorithms you need to implement are:

- `Dijkstra`
- `PathFinding`
- `AStar`

You will need to understand and implement these algorithms to find the optimal path in terms of fuel efficiency.

## Testing

To assist you in this challenge, a suite of tests is provided. These tests will guide you through the implementation process and ensure your code meets the specified requirements. The tests can be found in the `tests` folder.

# CI/CD Implementation Requirements

As part of this project, you are required to set up a Continuous Integration and Continuous Deployment (CI/CD) pipeline using GitHub Actions. This pipeline will automate the testing and deployment of your code.

## Workflow Steps

1. **Testing with pytest**: Upon each push or pull request to the main branch, the CI pipeline should automatically execute tests using pytest. This ensures that all new changes are verified before deployment.

2. **Building the Package**: If the tests pass, the next step is to build the Python package. This process involves preparing the package for distribution, ensuring that it is ready for deployment to PyPI.

3. **Creating a GitHub Workflow Artifact**: After successful deployment to PyPI, create a downloadable artifact of your package within the GitHub Workflow. This artifact should be accessible from the GitHub Actions run, allowing users to directly download the package version from GitHub.

## Good Luck!

We look forward to seeing your innovative solutions to this unique and challenging problem. Good luck, and happy coding!

# Rubric for Fuel Efficiency Path Challenge

### Total Points: 100

#### 1. Implementation of Entities (30 points)
   - `DownHill` Implementation: 5 points
   - `Valley` Implementation: 5 points
   - `Position` Implementation: 5 points
   - `UpHill` Implementation: 5 points
   - `Node` Implementation: 5 points
   - `Plateau` Implementation: 5 points

#### 2. Implementation of Algorithms (30 points)
   - `Dijkstra` Algorithm Implementation: 15 points
   - `PathFinding` Algorithm Implementation: 15 points

#### 3. Code Quality and Style (10 points)
   - Readability: 5 points
   - Adherence to coding standards/conventions: 5 points

#### 4. Testing and Test Coverage (20 points)
   - Comprehensive test cases: 10 points
   - Test coverage (measured using a tool like `coverage.py`): 10 points

#### 5. CI/CD Pipeline Implementation (10 points)
   - Correct setup of GitHub Actions for pytest: 3 points
   - Successful building and packaging of the Python package: 3 points
   - Creation of a downloadable GitHub Workflow artifact: 4 points
