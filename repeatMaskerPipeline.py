#!/usr/bin/env python
import time
import os
from argparse import ArgumentParser
from glob import glob
from toil.job import Job
from toil.common import Toil
from sonLib.bioio import system, popenCatch, getTempDirectory

# There are 3 phases to the process: splitting the input, running
# repeatmasker, and concatenation of the repeat-masked pieces.

def concatenate_job(job, input_ids):
    output = os.path.join(job.fileStore.getLocalTempDir(), 'rm.out')
    input_paths = map(job.fileStore.readGlobalFile, input_ids)
    popenCatch("xargs -0 cat >> {output}".format(output=output),
               "\0".join(input_paths))
    return job.fileStore.writeGlobalFile(output)

def repeat_masking_job(job, input_fasta, species):
    temp_dir = getTempDirectory()
    os.chdir(temp_dir)
    local_fasta = os.path.join(temp_dir, 'input.fa')
    job.fileStore.readGlobalFile(input_fasta, local_fasta, cache=False)
    system("chmod a+rw %s" % local_fasta)
    system("RepeatMasker -pa 10 -species {species} {input}".format(species=species, input=local_fasta))
    output_path = local_fasta + '.out'
    masked_out = job.fileStore.writeGlobalFile(output_path)
    return masked_out

def split_fasta(input_fasta, work_dir):
    out_root = os.path.join(work_dir, "out") + '/'
    os.mkdir(out_root)
    system("faSplit byname {input} {out_root}".format(
        input=input_fasta,
        out_root=out_root))
    return glob(os.path.join(work_dir, "out/*"))

def split_fasta_job(job, input_fasta, opts):
    work_dir = job.fileStore.getLocalTempDir()
    local_fasta = os.path.join(work_dir, 'in.fa')
    job.fileStore.readGlobalFile(input_fasta, local_fasta)
    split_fastas = split_fasta(local_fasta, work_dir)
    split_fasta_ids = [job.fileStore.writeGlobalFile(f) for f in split_fastas]
    repeat_masked = [job.addChildJobFn(repeat_masking_job, id, opts.species, cores=8, memory='8G').rv() for id in split_fasta_ids]
    return job.addFollowOnJobFn(concatenate_job, repeat_masked).rv()

def parse_args():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('input_fasta')
    parser.add_argument('species')
    parser.add_argument('output')
    Job.Runner.addToilOptions(parser)
    return parser.parse_args()

def main():
    opts = parse_args()
    with Toil(opts) as toil:
        if opts.restart:
            result_id = toil.restart()
        else:
            input_fasta_id = toil.importFile('file://' + os.path.abspath(opts.input_fasta))
            job = Job.wrapJobFn(split_fasta_job, input_fasta_id, opts)
            result_id = toil.start(job)
        toil.exportFile(result_id, 'file://' + os.path.abspath(opts.output))

if __name__ == '__main__':
    main()
