#
# Copyright 2019, Julian Catchen <jcatchen@illinois.edu>
#
# This file is part of RADinitio.
#
# RADinitio is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RADinitio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RADinitio. If not, see <http://www.gnu.org/licenses/>.
#

import os, sys, argparse
import radinitio as ri

PROG = sys.argv[0]
VERSION = ri.__version__

usage = f'''raditio version {VERSION}

radinitio --genome path --out-dir dir [pipeline-stage] [--chromosomes path] \
    [(demographic model options)] [(library options)] [(pcr options)] [(advanced options)]

Pipeline stages (these options are mutually exclusive):
    --simulate-all        Run all the RADinitio stages (simulate a population, make a library,
                          and sequence) (Default)
    --make-population     Simulate and process variants. Produces genome-wide VCF.
    --make-library-seq    Simulate and sequence a RAD library. Requires existing variants.
    --tally-rad-loci      Calculate the number of kept rad loci in the genome.

Input/Output files:
    -g, --genome:         Path to reference genome (fasta file, may be gzipped).  (Required)
    -o, --out-dir:        Path to an output directory where all files will be written.
                          (Required)

Input genome options
    -l, --chromosomes:    File containing the list of chromosomes (one per line) to simulate.
                          (default = None)
    -i, --min-seq-len:    Minimum length in bp required to load a sequence from the genome
                          fasta.  (default = 0)

Demographic model (simple island model)
    -p, --n-pops:         Number of populations in the island model.  (default = 2)
    -n, --pop-eff-size:   Effective population size of simulated demes.  (default = 5000)
    -s, --n-seq-indv:     Number of individuals sampled from each population.  (default = 10)

Library preparation/sequencing:
    -b, --library-type:   Library type (sdRAD or ddRAD).  (default = 'sdRAD')
    -e, --enz:            Restriction enzyme (SbfI, PstI, EcoRI, BamHI, etc.).
                          (default = 'SbfI')
    -d, --enz2:           Second restriction enzyme for double digest (MspI, MseI, AluI,
                          etc.).  (default = 'MspI')
    -m, --insert-mean:    Insert size mean in bp.  (default = 350)
    -t, --insert-stdev:   Insert size standard deviation in bp.  (default = 37)
    -j, --min-insert:     Minimum insert length in bp; overrides insert mean and stdev.
                          (default = None)
    -x, --max-insert:     Maximum insert length in bp; overrides insert mean and stdev.
                          (default = None)
    -v, --coverage:       Sequencing depth of coverage.  (default = 20)
    -r, --read-length:    Sequence read length in bp.  (default = 150)
    -f, --read-out-fmt:   Format for the output reads, FASTA or FASTQ.  (default = 'fasta')

PCR model options
    -c, --pcr-model:      PCR amplification model from decoratio. Available models are
                          log-normal ('lognormal'), log-skew-normal ('logskewnormal'),
                          inherited efficiency ('inheff'), and inherited efficiency beta
                          ('inheffbeta').  (default = None)
    -y, --pcr-cycles:     Number of PCR cycles.  (default = None)
    --pcr-deco-ratio:     Depth/complexity ratio.  (default = 0.1)
    --pcr-inheff-mean:    Mean amplification factor for inherited efficiency models.
                          (default = 0.7)
    --pcr-inheff-sd:      Stdev for the amplification factor in the inherited efficiency
                          models.  (default = 0.1)
    --pcr-lognormal-sd:   Stdev for log-normal and log-skew-normal models.  (default = 0.2)
    --pcr-lognormal-skew: Skew for log-skew-normal model.  (default = -1)

make-library-seq()-specific options:
    --make-pop-sim-dir:   Directory containing a previous radinitio.make_population
                          run. Cannot be the same as out-dir.

Additional options:
    -V, --version:        Print program version.
    -h, --help:           Display this help message.


Advanced options (can be left default for the majority of cases):
    --genome-rec-rate:    MsprimeOptions: Average per-base per-generation recombination
                          rate for the whole genome.  (default = 3e-8)
    --genome-mut-rate:    MsprimeOptions: Average per-base per-generation mutation rate
                          for the whole genome.  (default = 7e-8)
    --pop-mig-rate:       MsprimeOptions: Total per-population per-generation immigration
                          rate.  (default = 0.001)
    --pop-growth-rate:    MsprimeOptions: Population per-generation growth rate.
                          (default = 0.0)
    --lib-bar1-len:       LibraryOptions: Length of the forward-read barcode in bp.
                          (default = 5)
    --lib-bar2-len:       LibraryOptions: Length of the reverse-read barcode in bp.
                          (default = 0)
    --lib-5-error:        LibraryOptions: Frequency of errors at the 5' end of the
                          reads.  (default = 0.001)
    --lib-3-error:        LibraryOptions: Frequency of errors at the 3' end of the
                          reads.  (default = 0.01)
    --lib-min-dist:       LibraryOptions: Minimum distance between adjacent loci from
                          different cutsites in bp.  (default = 1000)
    --lib-base-len:       LibraryOptions: Base length for reference locus extraction in
                          bp.  (default = 1000)
    --lib-max-prop-n:     LibraryOptions: Maximum proportion of Ns that can be present
                          in the reference locus sequence.  (default = 0.1)
    --mut-indel-prob:     MutationModel: Probability of indels.  (default = 0.01)
    --mut-ins-del-ratio:  MutationModel: Ratio of insertions to deletions.  (default = 1.0)
    --mut-subs-model:     MutationModel: Substitution Model, equal probability (equal),
                          transitions (ts), or transversions (tv).  (default = equal)
    --pcr-pol-error:      PCRDups: Probability of PCR errors.  (default = 4.4e-7)
'''

def parse_args():
    p = argparse.ArgumentParser(prog=PROG)
    s = p.add_mutually_exclusive_group() # For the different pipeline stages
    s.add_argument(      '--simulate-all',     action='store_true', default=True)
    s.add_argument(      '--make-population',  action='store_true')
    s.add_argument(      '--make-library-seq', action='store_true')
    s.add_argument(      '--tally-rad-loci',   action='store_true')
    p.add_argument('-g', '--genome',           required=True)
    p.add_argument('-o', '--out-dir',          required=True)
    p.add_argument('-l', '--chromosomes',      default=None)
    p.add_argument('-i', '--min-seq-len',      type=int, default=0)
    p.add_argument('-p', '--n-pops',           type=int, default=2)
    p.add_argument('-n', '--pop-eff-size',     type=float, default=5e3)
    p.add_argument('-s', '--n-seq-indv',       type=int, default=10)
    p.add_argument('-b', '--library-type',     default='sdRAD', choices=['sdRAD', 'ddRAD', 'sdrad', 'ddrad'])
    p.add_argument('-e', '--enz',              default='SbfI')
    p.add_argument('-d', '--enz2',             default='MspI')
    p.add_argument('-m', '--insert-mean',      type=int, default=350)
    p.add_argument('-t', '--insert-stdev',     type=int, default=37)

    p.add_argument('-v', '--coverage',         type=int, default=20)
    p.add_argument('-r', '--read-length',      type=int, default=150)
    p.add_argument('-f', '--read-out-fmt',     type=str, default='fasta', choices=['fasta', 'fastq', 'FASTA', 'FASTQ'])
    p.add_argument(      '--make-pop-sim-dir', default=None)
    p.add_argument('-V', '--version',          action='version', version=f'radinitio version {VERSION}\n')
    p.add_argument('-j', '--min-insert',       default=None)
    p.add_argument('-x', '--max-insert',       default=None)

    p.add_argument('-c', '--pcr-model',        default=None, choices=[None, 'lognormal', 'logskewnormal', 'inheff', 'inheffbeta'])
    p.add_argument('-y', '--pcr-cycles',       default=None)
    p.add_argument(      '--pcr-deco-ratio',   type=float, default=0.1)
    p.add_argument(      '--pcr-lognormal-sd', type=float, default=0.2)
    p.add_argument(      '--pcr-lognormal-skew', type=float, default=-1)
    p.add_argument(      '--pcr-inheff-mean',  type=float, default=0.7)
    p.add_argument(      '--pcr-inheff-sd',    type=float, default=0.1)
    p.add_argument(      '--pcr-pol-error',    type=float, default=4.4e-7)

    p.add_argument(      '--lib-bar1-len',     type=int, default=5)
    p.add_argument(      '--lib-bar2-len',     type=int, default=0)
    p.add_argument(      '--lib-5-error',      type=float, default=0.001)
    p.add_argument(      '--lib-3-error',      type=float, default=0.01)
    p.add_argument(      '--lib-min-dist',     type=int, default=1000)
    p.add_argument(      '--lib-base-len',     type=int, default=1000)
    p.add_argument(      '--lib-max-prop-n',   type=float, default=0.10)
    p.add_argument(      '--mut-indel-prob',   type=float, default=0.01)
    p.add_argument(      '--mut-ins-del-ratio',type=float, default=1.0)
    p.add_argument(      '--mut-subs-model',   type=str, default='equal', choices=['equal', 'ts', 'tv'])
    p.add_argument(      '--genome-rec-rate',  type=float, default=3e-8)
    p.add_argument(      '--genome-mut-rate',  type=float, default=7e-8)
    p.add_argument(      '--pop-mig-rate',     type=float, default=0.001)
    p.add_argument(      '--pop-growth-rate',  type=float, default=0.0)

    # Overwrite the help/usage behavior.
    p.format_usage = lambda : usage
    p.format_help = p.format_usage

    # Check input arguments
    args = p.parse_args()
    args.out_dir = args.out_dir.rstrip('/')
    assert args.n_pops >= 1
    if not os.path.exists(args.genome):
        sys.exit(f"Error: '{args.genome}' not found")
    if not os.path.exists(args.out_dir):
        sys.exit(f"Error: '{args.out_dir}': output directory does not exist.")
    if args.chromosomes is not None:
        if not os.path.exists(args.chromosomes):
            sys.exit(f"Error: '{args.chromosomes}' not found")
    if args.min_insert is not None:
        args.min_insert = int(args.min_insert)
    if args.max_insert is not None:
        args.max_insert = int(args.max_insert)
    if args.pcr_cycles is not None:
        args.pcr_cycles = int(args.pcr_cycles) 

    return args

def main():
    sys_stdout_bak = sys.stdout
    try:
        args = parse_args()
        # Check the pipeline stage being run
        pipeline = None
        if args.make_population:
            pipeline = 'make_population'
        elif args.tally_rad_loci:
            pipeline = 'tally_rad_loci'
        elif args.make_library_seq:
            pipeline = 'make_library_seq'
        else:
            pipeline = 'simulate'
        # Open log file and begin
        sys.stdout = open(f'{args.out_dir}/radinitio.log', "w")
        print(f'RADinitio version {VERSION}', flush=True)
        print(f'radinitio.{pipeline} started on {ri.now()}.\n', flush=True)
        ri.print_dependencies()



        # Some general options
        # ====================
        # Parse chromosomes
        chromosomes = None
        if args.chromosomes is not None:
            chromosomes = open(args.chromosomes).read().split()
        # TODO: Add to the chrom.list file if available?
        recomb_rate = args.genome_rec_rate

        # ===================
        # RADinito options
        # Mutations
        muts_opts = ri.MutationModel(
            substitution_matrix=args.mut_subs_model,
            indel_prob=args.mut_indel_prob,
            ins_del_ratio=args.mut_ins_del_ratio)
        # Library configuration
        library_opts = ri.LibraryOptions(
            library_type = args.library_type,
            renz_1 = args.enz,
            renz_2 = args.enz2,
            insert_mu = args.insert_mean,
            insert_sigma = args.insert_stdev,
            insert_min = args.min_insert,
            insert_max = args.max_insert,
            coverage = args.coverage,
            read_len = args.read_length,
            barcode_len=args.lib_bar1_len,
            barcode2_len=args.lib_bar2_len,
            ierr=args.lib_5_error,
            ferr=args.lib_3_error,
            min_distance=args.lib_min_dist,
            base_locus_length=args.lib_base_len,
            max_n_prop=args.lib_max_prop_n,
            output_format=args.read_out_fmt)

        #
        # Check stage arguments:
        # ======================
        # If only generating variants
        if args.make_population is True:
            # Define msprime population options
            msprime_simulate_args = ri.simple_msp_island_model(
                n_seq_indv=args.n_seq_indv,
                pop_eff_size=args.pop_eff_size,
                n_pops=args.n_pops,
                mutation_rate=args.genome_mut_rate,
                pop_immigration_rate=args.pop_mig_rate,
                growth_rate=args.pop_growth_rate)
            # Call radinitio.make_population
            ri.make_population(
                out_dir = args.out_dir,
                genome_fa = args.genome,
                chromosomes = chromosomes,
                chrom_recomb_rates = recomb_rate,
                msprime_simulate_args = msprime_simulate_args,
                mutation_opts = muts_opts,
                min_seq_len = args.min_seq_len)

        #
        # =========================
        # If only tallying cutsites
        elif args.tally_rad_loci is True:
            # Call radinitio.tally_rad_loci
            ri.tally_rad_loci(
                out_dir = args.out_dir,
                genome_fa = args.genome,
                chromosomes = chromosomes,
                library_opts = library_opts,
                min_seq_len = args.min_seq_len)

        #
        # =========================================
        # If only generating library and sequencing
        # Previous run of `make-populations` needed
        elif args.make_library_seq is True:
            # Check inputs
            if args.make_pop_sim_dir is None:
                sys.exit('Need to specify `make_populations` directory when simulating library & sequencing')
            # Define pcr_options
            pcr_opts = ri.PCRDups(
                pcr_main_model = args.pcr_model,
                pcr_cycles = args.pcr_cycles,
                deco_ratio = args.pcr_deco_ratio,
                log_normal_sd = args.pcr_lognormal_sd,
                log_normal_skew = args.pcr_lognormal_skew,
                inheff_mean = args.pcr_inheff_mean,
                inheff_sd = args.pcr_inheff_sd,
                pol_error = args.pcr_pol_error,
                library_opts = library_opts)
            # Call radinitio.make-library_seq
            ri.make_library_seq(
                out_dir = args.out_dir,
                genome_fa = args.genome,
                chromosomes = chromosomes,
                make_pop_sim_dir = args.make_pop_sim_dir, 
                library_opts = library_opts,
                mutation_opts = muts_opts,
                pcr_opts = pcr_opts,
                min_seq_len = args.min_seq_len)

        #
        # =================================================
        # Default to running the whole pipeline - radinitio.simulate()
        else:
            # Define msprime population options
            msprime_simulate_args = ri.simple_msp_island_model(
                n_seq_indv=args.n_seq_indv,
                pop_eff_size=args.pop_eff_size,
                n_pops=args.n_pops,
                mutation_rate=args.genome_mut_rate,
                pop_immigration_rate=args.pop_mig_rate,
                growth_rate=args.pop_growth_rate)
            # Define pcr_options
            pcr_opts = ri.PCRDups(
                pcr_main_model = args.pcr_model,
                pcr_cycles = args.pcr_cycles,
                deco_ratio = args.pcr_deco_ratio,
                log_normal_sd = args.pcr_lognormal_sd,
                log_normal_skew = args.pcr_lognormal_skew,
                inheff_mean = args.pcr_inheff_mean,
                inheff_sd = args.pcr_inheff_sd,
                pol_error = args.pcr_pol_error,
                library_opts = library_opts)
            # Call radinitio.simulate
            ri.simulate(
                out_dir = args.out_dir,
                genome_fa = args.genome,
                chromosomes = chromosomes,
                chrom_recomb_rates = recomb_rate,
                msprime_simulate_args = msprime_simulate_args,
                library_opts = library_opts,
                mutation_opts = muts_opts,
                pcr_opts = pcr_opts,
                min_seq_len = args.min_seq_len)

        print(f'\nradinitio.{pipeline} completed completed on {ri.now()}.', flush=True)
    finally:
        sys.stdout = sys_stdout_bak

if __name__ == '__main__':
    main()
