# Genetic Algorithm for Software Project Scheduling

## Project Description
This project implements a **Genetic Algorithm (GA)** to solve a **software project scheduling and staffing problem**.  
The objective is to assign developers to tasks while respecting task dependencies and optimizing project performance.

This work is a **replicata** of the research approach presented in the article:

> **“A Genetic Algorithm for Software Project Scheduling and Staffing”**

The goal of this project is **not to propose a new model**, but to:
- reproduce the main ideas of the article,
- implement them in Python,
- test the behavior of the algorithm on different input data sets,
- and analyze the obtained results.

---

## Problem Overview
In a software project:
- Each **task** has a type, an effort, and precedence constraints.
- Each **developer** has different skill levels depending on the task type.
- Several developers can work on the same task, but this creates coordination overhead.
- Developers can multitask, which reduces efficiency.

The challenge is to find a task–developer assignment that:
- minimizes total project duration,
- limits excessive multitasking,
- preserves continuity between dependent tasks,
- keeps workload balanced across staff levels.

---

## Solution Approach
We use a **Genetic Algorithm**, where:
- Each individual (chromosome) represents an assignment of developers to tasks.
- The population evolves through selection, crossover, and mutation.
- A simulation model evaluates how the project executes over time.

---

## Fitness Function
The global fitness is a weighted sum of four criteria:

| Metric | Meaning |
|------|--------|
| **CM** | Makespan score (project duration vs. optimistic lower bound) |
| **CE** | Concentration score (penalizes multitasking) |
| **CC** | Continuity score (shared developers across dependent tasks) |
| **BA** | Balance score (fair distribution of effort across staff levels) |

Two main experiment cases are used:
- **CaseAll**: all criteria have equal weight  
- **CaseTime**: only project duration (CM) is optimized

---

## Input Data Sets
We test the algorithm on **three different data sets**:

| Set | Developers | Tasks | Description |
|----|-----------|-------|-------------|
| Set1 | 7 | 11 | Small project |
| Set2 | 10 | 11 | Same tasks, larger team |
| Set3 | 10 | 21 | Larger and more complex project |

Each set is defined explicitly in the code.

## Note on Result Stability and Execution Setup

The code provided in the Code folder is written as a single integrated script. When executed as a whole, it produces stable and reproducible results across multiple runs. This is the version used to generate the results reported in the comparison table.
To run experiments on different datasets (Set1, Set2, or Set3), it is sufficient to modify the input data section inside the script.

When the code was tested in a Jupyter Notebook and divided into separate cells—where functions were defined in individual cells and called from a main cell—the results sometimes varied between executions. This behavior is due to the stochastic nature of the genetic algorithm and the influence of cell execution order on the random seed. For this reason, the integrated script version is recommended to obtain consistent and reproducible results.
