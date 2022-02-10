# TypedDAG_on_HeteroMP
The evaluation source code for the paper "Type-aware Federated Scheduling for Typed DAG Tasks on Heterogeneous Multi-cores"
<br />
## Generators
Inside the genrators folder, we provide tools to 1) generate DAG tasks and 2) allocate the type infomation to generated DAG tasks with different configurations.
#### DAG Task generator
Run `python3 tasksets_generator_pure.py` to generate the pure DAG tasks without type information with the following configurations:
```
-m <the number of the task sets>
-a <the number of the available A type processors>
-b <the number of the available B type processors>
-q <the probability that two nodes have precedence constraints>
-d <the decision of whether -q command is applied. 0: probability \in [0.1, 0.9] by default; 1: probability \in [q, q+0.4]>
-u <the total utilization of the generated task set>
```
An additional parameter is `sparse`, which indicates the range of the number of tasks per set. 
`sp=0` by default, which means the number of tasks \in [0.5 * max{M_a, M_b}, 2 * max{M_a, M_b}].
The generated task sets will be stored under the path `..\experiments\inputs\tasks_pure`.
<br />
#### Type info allocation
Run `python3 tasksets_convertor.py` to allocate the type information to the generated DAG tasks, besides the aforemention configurations, we also provide:
```
-f <>
-s <>
-o <>
```
<br />

## Algorithms
The file `sched_ded.py` contains all these algorithms for schedulability test, including:
- `improved_federated_new`: The improved type-aware federated scheduling algorithm proposed in this paper (Sec. 7).
- `greedy_federated`: The greedy type-aware federated scheduling algorithm proposed in this paper (Sec. 5.2).
- `han`: federated scheduling algorithms proposed by Han et al. in [^1], both `EMU` mode and `Greedy` mode are implemented.





## References
[^1] M. Han, T. Zhang, Y. Lin, and Q. Deng. Federated scheduling for typed DAG tasks scheduling analysis on heterogeneous multi-cores. J. Syst. Archit., 112:101870, 2021.
