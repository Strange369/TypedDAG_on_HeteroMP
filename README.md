# TypedDAG_on_HeteroMP
The evaluation source code for the paper "Type-aware Federated Scheduling for Typed DAG Tasks on Heterogeneous Multi-cores"
<br />
## Before starting
The Dirichlet-Rescale (DRS) algorithm[^1] is applied for generate utilizations of task sets randomly
```
pip3 install drs
```
If you only want to reproduce the results in our paper, you can run these bash scripts that we provide:
```
1. ./generators/generate_all.sh <generate all the pure task sets.>
2. ./generators/converte_all.sh <allocate the type for each node of these tasks>
3. ./experiments/improved_fed_new.sh <schedulability test for the federated based approach in our paper>
4. ./experiments/greedy.sh <schedulability test for the greedy approach in our paper>
5. ./experiments/han.sh <schedulability test for the approached in Han et al.>
```
**Please note:**
- If you don't want to generate the tasksets by yourself, you can download the generated task sets from https://tu-dortmund.sciebo.de/s/9j7limbr8DvfVdT directly, which are the same as what we presented in our paper. You should unzip the downloaded file and put all these task sets files to the folder `/experiments/inputs/tasks_pure`, and continue the Step 2.
- Step 2 can start once all the pure task sets have been generated.
- Step 3, 4, and 5 can be executed in parallel once all the typed-DAG task sets have been generated from Step 2.

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
The generated task sets will be stored under the path `..\experiments\inputs\tasks_pure`.<br />
Currently, there are some task sets that are generated from the configurations in our paper.
<br />
#### Type info allocation
Run `python3 tasksets_convertor.py` to allocate the type information to the generated DAG tasks, besides the aforemention configurations, we also provide several parameters from the description of our paper:
```
-f <the $P_{\ell}$ \in {10%, 5%, 1%} controls the skewness of the skewed tasks>
-s <the $r$ controls the percentage of skewed tasks>
-o <controls if both heavy_a and heavy_b tasks can be skewed tasks with the same possibility or based on the ratio of M_a/M_b. The default `0` means the possibilities are the same regardless of the ration of M_a/M_b>
```
The generated task sets will be stored under the path `..\experiments\inputs\tasks_new`.
<br />

## Algorithms
Inside the `algorithms` folder, the file `sched_ded.py` contains all these algorithms for schedulability test, including:
- `improved_federated_new`: The improved type-aware federated scheduling algorithm proposed in this paper (Sec. 7).
- `greedy_federated`: The greedy type-aware federated scheduling algorithm proposed in this paper (Sec. 5.2).
- `han`: federated scheduling algorithms proposed by Han et al. in [^2], both `EMU` mode and `Greedy` mode are implemented.

## Experiments
In the `experiments` folder, we provide the tools to operate the schedulability tests with different approaches. <br />
The results will be stored in the folder `outputs/results`. Currently, there are some results based on our paper's configurations.<br />
In addition, we provide two scripts to draw the figures according to the obtained results, i.e., `draw_sched_6_1/2.py`.

## Figures
These two figures in the folder `figures` are the results in our paper.

## References
[^1]: https://pypi.org/project/drs/ 
[^2]: M. Han, T. Zhang, Y. Lin, and Q. Deng. Federated scheduling for typed DAG tasks scheduling analysis on heterogeneous multi-cores. J. Syst. Archit., 112:101870, 2021.
