#!/usr/bin/env python2.7
from __future__ import division, print_function
import sys, os

def main(args):
    print("gene\tchromsome\tchrom_start\tchrom_end\tgene_start\tgene_end\tznf_size\tidentity\tcoverage\tlen_chrom\tlen_gene\tsize_ratio\tmatch\tmismatch\tcigar")
    for line in open(sys.argv[1]):
    	if line.startswith("#") and "name" not in line:
    			gene = line.lstrip("#").rstrip()
    	elif "name" not in line:
    		line = line.split()
    		chrom = line[0]
    		chrom_start = line[1]
    		chrom_end = line[2]
    		gene_start = line[4]
    		gene_end = line[5]
    		size2 = line[7]
    		identity = float(line[8].rstrip("%"))
    		coverage = float(line[10].rstrip("%"))
    		len1 = int(line[11])
    		len2 = int(line[12])
    		size_ratio = len1 / len2
    		match = line[13]
    		mismatch = line[14]
    		cigar = line[15]
	        print("\t".join(map(str,[gene,chrom,chrom_start,chrom_end,gene_start,gene_end,size2,identity,coverage,len1,len2,size_ratio,match,mismatch,cigar])))             


if __name__ == "__main__":
    sys.exit(main(sys.argv))
