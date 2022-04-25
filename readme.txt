***File details***

There are 3 files ilp_gurobi.py, vird.py and viri.py.
(A) ilp_gurobi.py implements the ILP mentioned in the file "ilp.pdf".
    Slide 17 to Slide 20.
    The variable used in program are same as used in ILP equations present in slides.

(B) vird.py implements the "first fit vGPU increasing requests decreasing (VIRD)"
    algorithm mention in the file "ilp.pdf"
    Slide 24 to Slide 25

(C) viri.py implements the "first fit vGPU increasing requests increasing (VIRI)"
    algorithm mention in the file "ilp.pdf"
    Slide 26 to Slide 27


***How to run***

#NOTE: Running ilp_gurboi.py requires installation of "gurobi 8.0.1" 

#Each file takes as input 
1. Number of physical GPUs (-n)
2. Number of user requests (-m)
3. Seed value for randomly generating user requests (-s).
	default value of seed is 1.
   User requests are in terms of vGPU memory required in GB
4. Name of output file (-o)

#Option 1 and 2 mandatory.

#Command to run files:

(1) python ilp_gurobi.py -n <num_gpus> -m <num_requests> -s <seed value> -o <output file name>

(2) python vird.py -n <num_gpus> -m <num_requests> -s <seed value> -o <output file name>

(3) python viri.py -n <num_gpus> -m <num_requests> -s <seed value> -o <output file name>


***Sample Output File***

#Three sample output files "sample_ilp_out", "sample_vird_out" and "sample_viri_out" are there which 
contains the sample output for ilp_gurobi.py, vird.py and viri.py respectively.

#The output file contain the results including "total gpus used", "execution time of algorithm",
"profile set per GPU" and "requests placed per gpu".

#For "ilp_gurobi.py", the output file contains the value of decision variables too. 




 