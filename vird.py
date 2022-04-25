#Usage: python vird.py -n <val> -m <val> -s <seed_val> -o <outfile_name>
#First two arguments mandatory, seed's default value =1
#value of seed and output file are optional



###Heuristics based vGPU aware VM placement
# Here we are sorting the n_jk[][] in decreasing order and
#     correspinding a_jk[][] in increasing order of memory

#in this way we will get the best fit of memory for the requests.
#Also we are sorting requests in decreasing order of their memory requirements.

#NOTE That this will give the optimal solution as far as placement of
# requests based on memory is concerned!!!

###Inputs
#M: total number of requests
#N: total number of GPUs (N>=M)
#m_i : vGPU memory required by request 'i'
#n_jk : number of vGPUs associated with profile 'k' of GPU 'j'
#t_j: number of possible vGPU profiles associated with GPU 'j'
#a_jk: memory size of each vGPU associated with profile 'k' of GPU 'j'
#set_vgpu: List of GPUs whose vGPU profile has been set
#notset_set: List of GPUs whose vGPU profile is not set
#seed: seed for the randomly generating memory requests
#upper_mem_limit: upper limit on memory request size (in GB) !! shouldn't be more than available GPU memory
#lower_mem_limit: lower limit on memory request size (in GB) !!
#random memory requests will be generated with sizes between lower_mem_limit and upper_mem_limit



###Objective: Minimize the total number of active GPUs

"""

"""
import sys
import time
import random
import argparse

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

gpu_id= [] #stores index or id's of physical GPUs
set_vgpu = [] #List of GPUs whose vGPU profile is set: stores the gpu_id of GPU
notset_vgpu = [] #List of GPUs whose vGPU profile is not set: stores the gpu_id of GPU
request_placed=0 #Total number of requests placed
request_not_placed=0 #total number of requests not placed



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


"""    m_i is filled with random memory values between  
       lower_mem_limit GB to upper_mem_limit GB :
       Default values are 1 GB and 12 GB respectively
"""

for i in range(M):
  m_i.append(random.randint(lower_mem_limit,upper_mem_limit))
#print m_i


for i in range(N):
   t_j.append(len(n_k))
   n_jk.append(n_k)
   a_jk.append(a_k)
#print n_jk
#print a_jk

print "M=", M, "N=", N


start_time =time.time()  #Measures time in second

#sort requests in decreasing order of memory requirement
#sort n_jk in decreasing order of available vGPUs
#sort a_jk in increasing order of available memory

m_i.sort(reverse=True)
for ele in n_jk:
    ele.sort(reverse=True)
for ele in a_jk:
    ele.sort()

#print n_jk
#print a_jk
for i in range(N):
   gpu_id.append(i)

per_gpu_request = []
per_gpu_vgpus = []
per_gpu_memory = []
remain_vgpu = []
for i in range(len(gpu_id)):
	notset_vgpu.append(gpu_id[i])
	

#print notset_vgpu
#print gpu_id

for i in range(N):
	per_gpu_request.append(0)
	per_gpu_vgpus.append(0)
	per_gpu_memory.append(0)
        remain_vgpu.append(0)


#Algorithm begins

for req_mem in m_i:
  found=0
  #print "Current request =", req_mem
  #print set_vgpu
  #print notset_vgpu
  if len(set_vgpu)>0:
     for sg in set_vgpu:
        if ((per_gpu_memory[sg]>=req_mem) and (remain_vgpu[sg]>0)):
    	   per_gpu_request[sg]=per_gpu_request[sg]+1
	   remain_vgpu[sg]=remain_vgpu[sg]-1
	   #print "request placed", req_mem, "in GPU", sg
	   found=1
	   request_placed=request_placed+1
	   request_not_placed=request_not_placed-1
	   break
       
  if found==0 :
     i=-1
     for ug in notset_vgpu:
        i=i+1
	j=0
	if found==1:
	  break
        for vgpu_mem in a_jk[ug]:
	   if vgpu_mem>=req_mem:
	      found=1
       	      set_vgpu.append(ug)
	      notset_vgpu.pop(i)
	      per_gpu_request[ug]=per_gpu_request[ug]+1
	      per_gpu_vgpus[ug]=n_jk[ug][j]
	      per_gpu_memory[ug]=a_jk[ug][j]	
	      remain_vgpu[ug]=per_gpu_vgpus[ug]-1 
              request_placed=request_placed+1
	      request_not_placed=request_not_placed-1
              #print "request placed", req_mem, "in GPU ", ug
	      break
	   j=j+1
             
  if found==0:
     print "Couldn't find vGPU for the request"
#Algorithm ends

end_time= time.time()
elapsed_time=end_time - start_time

print "elasped time =", elapsed_time

#Printing results to File

if outfile!=None:  
  write_file=open(outfile,"w")
  print>>write_file, "Total GPUs = ", N, " Total input requests = ",M, " seed value = ",seed
  print>>write_file, "Total GPUs used = ", len(set_vgpu), " Out of ", N, "GPUs"
  for i in range(N):
    print>>write_file, "Requests placed in GPU",i+1, "=", per_gpu_request[i], " Num vGPUs =", per_gpu_vgpus[i], " vGPU memory= ",per_gpu_memory[i], " Unused vGPUs = ",remain_vgpu[i]

  print>>write_file, "\nRequests placed = ", request_placed, ", Requests not placed = ", request_not_placed, ", GPUs used =" , len(set_vgpu), ", GPUs not used =", len(notset_vgpu)
  print>>write_file, "\nTotal time taken in seconds to find the solution = " ,float(elapsed_time)


#Printing results to terminal
if outfile==None:
  print  "Total GPUs = ", N, " Total input requests = ",M, " seed value = ",seed
  print  "Total GPUs used = ", len(set_vgpu), " Out of ", N, "GPUs"
 
  for i in range(N):
     print "Requests placed in GPU",i+1, "=", per_gpu_request[i], " Num vGPUs =", per_gpu_vgpus[i], " vGPU memory= ",per_gpu_memory[i], " Unused vGPUs = ",remain_vgpu[i]
  print "Requests placed = ", request_placed, ", Requests not placed = ", request_not_placed, ", GPUs used =" , len(set_vgpu), ", GPUs not used =", len(notset_vgpu)

