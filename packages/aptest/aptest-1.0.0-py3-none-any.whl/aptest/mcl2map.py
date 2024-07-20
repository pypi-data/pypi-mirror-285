import pandas as pd 
import argparse
from utils.protein_mcl import *
from exec.maincluster import *

#mcl: mcl result
#mapfile: prot2contigmap
#protmap:  protein cluster map
#protein_id,contig_id,cluster

#def make_protein_clusters_mcl(blast_fp, out_p, inflation=2):



def parsemcl(mcl,mapfile):
	pcidx = 0
	mapdf = pd.read_csv(mapfile,sep=',',header=0)
	prot2ctg = dict(zip(mapdf['protein_id'],mapdf['contig']))
	data = []
	for line in open(mcl,'r'):
		line = line.strip()
		info = line.split('\t')
		
		if len(info)<2:
			continue
		pc = "PC_"+str(pcidx)
		for protein in info:
			#print(protein,prot2ctg[protein],pc)
			data.append([protein,prot2ctg[protein],pc])
		pcidx += 1
		
	df = pd.DataFrame(data,columns=['protein_id','contig_id','cluster'])
	df.to_csv('tmp/protein_cluster_v2.csv',index=False)
	
	
	
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("contig",type=str)
	
	
	args = parser.parse_args()
	
	print("Running diamond alignment")
	#db_fp = make_diamond_db(args.contig+".faa", 'tmp', 4)
	#run_diamond(args.contig+".faa", db_fp, 4, 0.0001, 25, 'tmp/protein.diamond.tab')
	
	print("Creating protein family")
	'''
	mclres = make_protein_clusters_mcl('tmp/protein.diamond.tab', 'tmp')
	#mclres = "merged.self-diamond.tab_mcl20.clusters"
	parsemcl(mclres,"tmp/prot_contig_id.csv")
	'''
	clusterargs = Arg()
	setattr(clusterargs,'map',"tmp/prot_contig_id.csv")
	setattr(clusterargs,'tab','tmp/protein.diamond.tab')
	setattr(clusterargs,'prot',"tmp/protein_cluster_v2.csv")
	
	maincluster(clusterargs)

