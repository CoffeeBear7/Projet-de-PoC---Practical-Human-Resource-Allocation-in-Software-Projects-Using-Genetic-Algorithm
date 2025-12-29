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
It is important to note that the results presented in the comparison table were obtained by running the entire code at once for each dataset in Jupyter. For each set, the same full code was copied into a single cell, and only the input data (Set1, Set2, or Set3) was changed. Using this approach, the results were stable and reproducible across multiple executions.

However, after restructuring the code into multiple Jupyter cells (with functions defined once and then called separately in the main cell), the results started to vary between executions. This behavior is mainly due to the use of randomness in the genetic algorithm and the fact that the random seed (s) is affected by the execution order of cells in Jupyter. As a result, even with the same seed value, different execution paths can lead to different solutions.
