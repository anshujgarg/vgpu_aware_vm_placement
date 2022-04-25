#Usage: python ilp_gurobi.py -n <val> -m <val> -s <seed_val> -o <outfile_name>
#First two arguments mandatory, seed's default value =1
#value of seed and output file are optional

#Here the assumption is that we have homogeneous GPUs:  Tesla P40 profiles. 

###Decision variables:
#r_ij: if request 'i is placed in GPU 'j'. Can take values {0,1}
#p_jk: if profile 'k' is selected for GPU 'j' or not. Can take values {0,1}



###Inputs
#M: total number of requests
#N: total number of GPUs  (N>=M)
#m_i : vGPU memory required by request 'i'
#n_jk : number of vGPUs associated with profile 'k' of GPU 'j'
#t_j: number of possible vGPU profiles associated with GPU 'j'
#a_jk: memory size of each vGPU associated with profile 'k' of GPU 'j'
#seed: seed for the randomly generating memory requests
#upper_mem_limit: upper limit on memory request size (in GB) !! shouldn't be more than available GPU memory
#lower_mem_limit: lower limit on memory request size (in GB) !!
#random memory requests will be generated with sizes between lower_mem_limit and upper_mem_limit


###Objective: Minimize the total number of active GPUs


from gurobipy import *
import time 
import random
import sys
import argparse

#define a model with name "vvmp" (Vgpu aware VM Placement)
model=Model("vvmp")

#model should minimize the objective function
model.modelSense=GRB.MINIMIZE

#Variables

M=0   
N=0

m_i =[]

t_j =[]   #total number of supported vGPU profiles for GPU 'j'
n_jk=[]   #number of available vGPUs with profile 'k' of GPU 'j'
a_jk =[]  #memory avaialable per vGPU for profile 'k' of GPU 'j'

#profile values for P100 arranged in decreasing order of available vGPU memory
n_k =[1,2,3,4,6,8,12,24]   
a_k=[24,12,8,6,4,3,2,1]

seed=1
outfile =""
upper_mem_limit =12
lower_mem_limit =1


#Output variable: total number of physical GPU used out of available 'N' GPUs
gpu_used=0

p_jk = []
r_ij = []



#variables to store runtime of program
start_time=0.0
end_time=0.0
elapsed_time=0.0 #total time taken to find the solution


#parsing the input arguments
parser = argparse.ArgumentParser()
parser.add_argument('-n',action="store",dest="num_gpu",type=int) #input value of N 
parser.add_argument('-m',action="store",dest="num_req",type=int) #input value of M
parser.add_argument('-s',action="store",dest="seed_val",type=int) #input value of seed
parser.add_argument('-o',action="store",dest="out_file")  #input value of output file
arg_val=parser.parse_args()

N =arg_val.num_gpu
M = arg_val.num_req
seed = arg_val.seed_val
outfile = arg_val.out_file
request_not_placed=M

#Values of M and N are mandatory

if N==None or M==None:
   print "Please specify value of M and N"
   print "usage: python vird.py -n <val> -m <val> -s <seed_val> -o <outfile_name>"
   exit()

if seed==None:
   seed=1

random.seed(seed)

#if output file name is specified in input


"""    m_i is filled with random memory values between  
       lower_mem_limit GB to upper_mem_limit GB :
       Default values are 1 GB and 12 GB respectively
"""
for i in range(M):
  m_i.append(random.randint(lower_mem_limit,upper_mem_limit))
#print m_i


"""
code to generate profiles for 'N' GPUs
Here the  GPUs are assumed to be Tesla P100 
which support 8 profiles:

	1Q,2Q,3Q,4Q,6Q,8Q,12Q and 24 Q

n_jk and a_jk stores the number of vGPUs and memory per
vgpu for the vGPU profiles respectively.



"""
	

for i in range(N):
   t_j.append(len(n_k))
   n_jk.append(n_k)
   a_jk.append(a_k)
#print n_jk
#print a_jk


print "M=", M, "N=", N


start_time =time.time()  #Measures time in second

#adding binary decision variable p_jk to the model
#p_jk[j][k] = 1 if profile 'k' is selected for GPU 'j'

for j in range(len(n_jk)):
    p_k = []
    for k in n_jk[j]:
        p_k.append(model.addVar(vtype=GRB.BINARY))
    p_jk.append(p_k)

#adding binary decision variable r_ij to the model
#r_ij[i][j] = 1, if request 'i' is assigned to GPU 'j'

for i in range(M):
    r_j = []
    for j in range(N):
        r_j.append(model.addVar(vtype=GRB.BINARY))
    r_ij.append(r_j)


#print(len(n_jk))
model.update()

#Adding objective function to model	
model.setObjective(
    sum(
        sum((p_jk[j][k]+a_jk[j][k]*p_jk[j][k]) for k in range(t_j[j]))
        for j in range(N)
        ),
     GRB.MINIMIZE
    )

#Adding constraints to model
for i in range(M):
    for j in range(N):
        model.addConstr(m_i[i]*r_ij[i][j] <= (sum(a_jk[j][k]*p_jk[j][k] for k in range(t_j[j]))))        


#Adding constraints to model
for j in range(N):
        model.addConstr(sum(m_i[i]*r_ij[i][j] for i in range(M)) <= (sum(n_jk[j][k]*a_jk[j][k]*p_jk[j][k] for k in range(t_j[j]))))        



#Adding constraints to model
for j in range(N):
    model.addConstr(sum(r_ij[i][j] for i in range(M)) <= (sum(n_jk[j][k]*p_jk[j][k] for k in range(t_j[j])))) 

#Adding constraints to model
for i in range(M):
    model.addConstr(sum(r_ij[i][j] for j in range(N)) == 1) 

#Adding constraints to model
for j in range(N):
    model.addConstr(sum(p_jk[j][k] for k in range(t_j[j])) <= 1) 


#Adding constraints to model
model.addConstr( sum(
        sum(r_ij[i][j] for j in range(N))
        for i in range(M)
        ) == M
    )

model.update()

#Executing the model
model.optimize()

#print(model.objVal)


per_gpu_request = []
per_gpu_vgpus = []
per_gpu_memory = []

for i in range(N):
	per_gpu_request.append(0)
	per_gpu_vgpus.append(0)
	per_gpu_memory.append(0)


#going through value of decision variable p_jk
#print("vGPU Profile Values")
j=1
for p_j in p_jk:
  k=1
  for p_j_k in p_j:
     if p_j_k.x==1:
	#print "p[",j,"][",k,"]=",p_j_k.x
	per_gpu_vgpus[j-1] = n_jk[j-1][k-1]
	per_gpu_memory[j-1] = a_jk[j-1][k-1]
	gpu_used=gpu_used+1
     k=k+1
  j=j+1

#going through value of decision variable r_ij
#print("Mapping Values")
i=1
for r_i in r_ij:
  j=1
  for r_i_j in r_i:
     if r_i_j.x==1:
	#print "r[",i,"][",j,"]=", r_i_j.x
	per_gpu_request[j-1] = per_gpu_request[j-1]+1
     j=j+1
  i=i+1

end_time= time.time()


elapsed_time=end_time - start_time

print "elasped time (seconds)=", elapsed_time, "GPU used = ", gpu_used


##Writing output to outfile

if outfile!=None:  
  write_file=open(outfile,"w")
  print>>write_file, "Total GPUs = ", N, " Total input requests = ",M, " seed value = ",seed
  print>>write_file, "Total GPUs used = ", gpu_used, " Out of ", N, "GPUs"
  #Write("vGPU Profile Values")
  print>>write_file, "#Index of  GPUs  with their selected vGPU profile index. p[j][k]: profile 'k' of GPU 'j' is selected "
  j=1
  for p_j in p_jk:
    k=1
    for p_j_k in p_j:
       if p_j_k.x==1:
	  print>>write_file, "p[",j,"][",k,"]=",p_j_k.x
       k=k+1
    j=j+1

  #Write("Mapping Values")
  i=1
  print>>write_file, "#r[i][j]: request 'i' is placed on GPU 'j' "
  for r_i in r_ij:
    j=1
    for r_i_j in r_i:
       if r_i_j.x==1:
 	  print>>write_file, "r[",i,"][",j,"]=", r_i_j.x
       j=j+1
    i=i+1
  print>>write_file, "#Stats per GPU "
  for i in range(N):
     print >>write_file, "Requests placed in GPU" ,i+1, "=" , per_gpu_request[i] , " Num vGPUs =" , per_gpu_vgpus[i] , " vGPU memory= " , per_gpu_memory[i]
     # print "Requests placed in GPU",i+1, "=", per_gpu_request[i], " Num vGPUs =", per_gpu_vgpus[i], " vGPU memory= ",per_gpu_memory[i]
  
  print>>write_file, "\nTotal time taken in seconds to find the solution = " ,float(elapsed_time)


