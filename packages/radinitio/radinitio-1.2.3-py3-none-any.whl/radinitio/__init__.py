import random, re, gzip, sys, argparse, os, multiprocessing, math, pkg_resources, datetime
import numpy as np
import scipy as sc
from scipy.stats import poisson, binom
import msprime
import decoratio

#
# Copyright 2023:
#     Julian Catchen <jcatchen@illinois.edu>
#     Angel G. Rivera-Colon <angelgr2@illinois.edu>
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

try:
    __version__ = pkg_resources.get_distribution('radinitio').version
except Exception:
    __version__ = 'unknown'

def now():
    '''
    Print current date and time
    '''
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def date():
    '''Print today's date'''
    return f'{datetime.datetime.now().strftime("%Y%m%d")}'

def print_dependencies():
    text = f'''Dependency versions:
    msprime:                 {msprime.__version__}
    decoratio:               {decoratio.__version__}
    numpy:                   {np.__version__}
    scipy:                   {sc.__version__}\n'''
    print(text, flush=True)

#
# function to reverse complete sequence. It finds complement and inverts the order
def rev_comp(sequence):
    rev = []
    for nt in sequence.upper():
        if nt == 'A':
            rev.append('T')
        elif nt == 'C':
            rev.append('G')
        elif nt == 'G':
            rev.append('C')
        elif nt == 'T':
            rev.append('A')
        elif nt not in ['A', 'C', 'G', 'T']:
            rev.append('N')
    return ''.join(rev[::-1])

#
# function to load chromosome list into a set
# structure:      set('chrom1', 'chrom2', ... )
def chrom_set(chrom_list_path):
    chrom_s = set()
    found_bracket = False
    for line in open(chrom_list_path, 'r'):
        line = line.strip('\n')
        if line.startswith('>'):
            found_bracket = True
        chrom_s.add(line)
    return chrom_s

# Print a warning if the brackets from the
# fasta headers (>) are present in the IDs
def check_brackets_in_chr_ids(chromosomes):
    '''
    Check for the fasta header bracket (>) in a list
    of chromosome IDs
    Args:
        chromosomes : (list) list of chromosome IDs
    Returns:
        None'''
    found_bracket = False
    for chromosome in chromosomes:
        if chromosome.startswith('>'):
            found_bracket = True
    if found_bracket:
        print('    Warning: \'>\' found in the chromosome list.', flush=True)
        # TODO: @Gio: Color the warning characters?
        sys.stderr.write('Warning: \'>\' found in the chromosome list. Program will run assuming these are part of the sequence IDs.\n')


#
# Create a chromosome class
class Chromosome:
    def __init__(self, chrom_id, chrom_sequence):
        self.id = chrom_id
        self.seq = chrom_sequence
        self.len = len(self.seq)
        self.rec = None
    def __str__(self):
        return f'{self.id} : {self.len:,} bp : {self.rec}'

#
# function to generate genome dictionary
# structure of this dictionary:     { chromosome_id : chrom_object }
# TODO: how to handle other recombination rates; perhaps a tsv with chrom_id<tab>rec_rate that is matched with chrom id
#   @Nicolas 2019-05-06: See my comment at the Chrom class; it's too early to assign recombination rates.
def load_genome(fasta_f, chrom_selection=None, min_seq_len=0):
    '''
    Load a genome sequence in FASTA format.

    Args:
        fasta_f : (str) Path to genome FASTA (can be gzipped)
        chrom_selection : (list or None) IDs of target sequence IDs
        min_seq_len : (int) Minimum lenght of the sequences

    Returns:
        genome_dict : (dict) Dictionary of the selected genomic sequences
    '''
    print('\nLoading the genome...', flush=True)
    if chrom_selection is not None:
        chrom_selection = set(chrom_selection)
    genome_dict = dict()
    seqs_read = 0
    with gzip.open(fasta_f, 'rt') if fasta_f.endswith('.gz') else open(fasta_f) as f:
        name = None
        seq = list()
        for line in f:
            line = line.strip('\n')
            # Ignore empty lines
            if len(line) == 0:
                continue
            # Check if its ID or sequence
            if line.startswith('>'):
                seqs_read += 1
                if name is not None:
                    if chrom_selection is None or name in chrom_selection:
                        chrom_sequence = ''.join(seq)
                        if len(chrom_sequence) >= min_seq_len:
                            genome_dict[name] = Chromosome(name, chrom_sequence)
                name = line.lstrip('>').split()[0]
                seq = list()
            elif line[0] in ['#', '.']:
                # Ignore comment lines
                continue
            else:
                # if it is sequence
                seq.append(line.upper())
    if chrom_selection is None or name in chrom_selection:
        chrom_sequence = ''.join(seq)
        if len(chrom_sequence) >= min_seq_len:
            genome_dict[name] = Chromosome(name, chrom_sequence)
    # Report sequences loaded
    n_chrs = len(genome_dict)
    print(f'    Read {seqs_read:,} sequences from the input FASTA.', flush=True)
    print(f'    Loaded {n_chrs:,} chromosome/scaffold sequences.', flush=True)
    # Check for invalid characters in the genome
    check_invalid_chars_in_genome(genome_dict)
    # Return genome dictionary
    return genome_dict

# Function to go over chromosome dictionary and tally characters
# Will return error if they are non 'ACGTN' characters present
def check_invalid_chars_in_genome(genome_dict):
    assert type(genome_dict) == dict
    # list to house all possible ascii chars
    ascii_char_list = np.zeros(128, dtype=int)
    # loop over chrom dict
    for chrom in sorted(genome_dict):
        chromosome = genome_dict[chrom]
        assert isinstance(chromosome, Chromosome)
        for bp in chromosome.seq:
            index = ord(bp)
            ascii_char_list[index] += 1
    # Check the found characters
    found_chars = list()
    for i in range(len(ascii_char_list)):
        if ascii_char_list[i] != 0:
            found_chars.append(chr(i))
    found_chars = set(found_chars)
    # Check for equality
    if found_chars.issubset('ACGTN') is False:
        sys.exit('''ERROR: Genome contains non-canonical characters.
Only characters allowed in the sequence are \'A\', \'C\', \'G\', \'T\', and \'N\'.
Check the `radinitio.fix_genome_bases()` function for how to correct the FASTA sequence.''')

# Function to generate the popmap from msprime model
def write_popmap(popmap_file, population_configurations, ploidy = 2):
    popmap = open(popmap_file, 'w')
    sample = 0
    sam_list = []
    # parse the population configurations and count samples
    for i, pop in enumerate(population_configurations):
        assert pop.sample_size % ploidy == 0
        for _ in range(pop.sample_size // ploidy):
            sam_list.append( (sample, i) )
            sample += 1
    # determine padding for samples and populations
    pad_s = '0{}d'.format(len(str(sam_list[-1][0])))
    pad_p = '0{}d'.format(len(str(sam_list[-1][1])))
    # Write popmap from sample list
    for s in sam_list:
        sam = 'msp_' + str(format(s[0], pad_s))
        pop = 'pop'  + str(format(s[1], pad_p))
        popmap.write('{}\t{}\n'.format(sam, pop))

#
# Make simple msprime island model
# TODO: Upgrade to MSPRIME v1
def simple_msp_island_model(n_seq_indv, pop_eff_size, n_pops, mutation_rate=7e-8, pop_immigration_rate=0.001, growth_rate=0.0):
    # Msprime parameters
    # Create the population(s).
    pops = [
        msprime.PopulationConfiguration(
            sample_size = 2 * n_seq_indv,
            initial_size = pop_eff_size,
            growth_rate = growth_rate)
        for i in range(n_pops) ]
    msprime_simulate_args = {
        'mutation_rate' : mutation_rate,
        'population_configurations' : pops }
    if n_pops > 1:
        # Create the (symmetric) migration matrix.
        # In msprime, each element `M[j,k]` of the migration matrix defines the fraction
        # of population `j` that consists of migrants from population `k` in each generation.
        # Additionally, there should be zeroes on the diagonal.
        # `pop_immigration_rate` = Total per-population per-generation immigration rate.
        m = pop_immigration_rate / (n_pops - 1)
        migration_matrix = [ [
                0 if k == j else m
                for k in range(n_pops) ]
                for j in range(n_pops) ]
        msprime_simulate_args['migration_matrix'] = migration_matrix
    return msprime_simulate_args

# Print msprime parameters
def print_msp_params(msprime_simulate_args, log_file):
    # Print msprime options
    pop_conf = msprime_simulate_args['population_configurations']
    print(f'''\nmsprime demographic model options:
    Mutation rate:           {msprime_simulate_args['mutation_rate']:.6g}
    Number of populations:   {len(pop_conf)}''', file=log_file, flush=True)
    for i in range(len(pop_conf)):
        print(f'    Pop {i+1} Ne:                {pop_conf[i].initial_size}', file=log_file, flush=True)
        print(f'    Pop {i+1} sample size:       {pop_conf[i].sample_size//2}', file=log_file, flush=True)
    if len(pop_conf) > 1:
        print('    Migration matrix:',  file=log_file, flush=True)
        mig_mat = msprime_simulate_args['migration_matrix']
        for row in mig_mat:
            print('            ', row,  file=log_file, flush=True)

# Function to do msprime simulations for one chromosome
def sim_one_chromosome(msprime_simulate_args, chromosome, vcf_path):
    assert isinstance(chromosome, Chromosome)
    assert chromosome.rec is not None and type(chromosome.rec) == float
    simulation = msprime.simulate(
        **msprime_simulate_args,
        length = chromosome.len,
        recombination_rate = chromosome.rec)
    with gzip.open(vcf_path, 'wt') as vcf_file:
        simulation.write_vcf(vcf_file, 2)

# TODO: Update reporting here
def sim_all_chromosomes(msprime_simulate_args, genome_dict, out_dir):
    assert os.path.isdir(out_dir)
    for chrom_name in sorted(genome_dict):
        print('    {}...'.format(chrom_name), flush=True)
        chromosome = genome_dict[chrom_name]
        vcf_path = '{}/{}.vcf.gz'.format(out_dir.rstrip('/'), chrom_name)
        sim_one_chromosome(msprime_simulate_args, chromosome, vcf_path)

# Compatible enzymes
known_enzymes = { e[0].lower() : e for e in [
    # 4 cutters
    ('AluI',    'AG/CT'),
    ('BfaI',    'C/TAG'),
    ('BfuCI',   '/GATC'),
    ('Csp6I',   'G/TAC'),
    ('CviQI',   'G/TAC'),
    ('DpnII',   '/GATC'),
    ('HaeIII',  'GG/CC'),
    ('HinP1I',  'G/CGC'),
    ('HpaII',   'C/CGG'),
    ('MluCI',   '/AATT'),
    ('MseI',    'T/TAA'),
    ('MspI',    'C/CGG'),
    ('NlaIII',  '/CATG'),
    ('RsaI',    'GT/AC'),
    ('Sau3AI',  '/GATC'),
    ('TaqI',    'T/CGA'),
    # 6 cutters
    ('AgeI',    'A/CCGGT'),
    ('AseI',    'AT/TAAT'),
    ('BamHI',   'G/GATCC'),
    ('BglII',   'A/GATCT'),
    ('BspDI',   'AT/CGAT'),
    ('ClaI',    'AT/CGAT'),
    ('EcoRI',   'G/AATTC'),
    ('EcoRV',   'GAT/ATC'),
    ('EcoT22I', 'A/TGCAT'),
    ('HinDIII', 'A/AGCTT'),
    ('KpnI',    'G/GTACC'),
    ('NcoI',    'C/CATGG'),
    ('NdeI',    'CA/TATG'),
    ('NheI',    'G/CTAGC'),
    ('NsiI',    'A/TGCAT'),
    ('PstI',    'C/TGCAG'),
    ('SacI',    'G/AGCTC'),
    ('SphI',    'G/CATGC'),
    ('SpeI',    'A/CTAGT'),
    ('XbaI',    'T/CTAGA'),
    ('XhoI',    'C/TCGAG'),
    # 8 cutters
    ('NotI',    'GC/GGCCGC'),
    ('SbfI',    'CC/TGCAGG')
    ]}
known_enz_names = [ known_enzymes[e][0] for e in sorted(known_enzymes) ]
known_enz_set = set([ e.lower() for e in known_enz_names ])

#
# set the restriction enzyme class and related variables
class RestrictionEnzyme:
    def __init__(self, enzyme_name):
        # Check if in available enzymes
        if enzyme_name.lower() not in known_enz_set:
            sys.exit('ERROR: \'{}\' is not an available enzyme. Enzymes include: {}'.format(enzyme_name, ' '.join(known_enz_names)))
        e = known_enzymes[enzyme_name.lower()]
        self.name = e[0]
        self.cut_pattern = e[1]
        self.cutsite = e[1].replace('/', '')
        remainder_length = max([ len(part) for part in e[1].split('/') ])
        self.remainder = self.cutsite[len(self.cutsite)-remainder_length:]
    def olap_len(self):
        return 2 * len(self.remainder) - len(self.cutsite)
    def __str__(self):
        return '{} ({})'.format(self.name, self.cut_pattern)

class LibraryOptions:
    def __init__(self,
                 library_type='sdRAD',
                 renz_1='SbfI',
                 renz_2='MspI',
                 insert_mu=350,
                 insert_sigma=37,
                 insert_min=None,
                 insert_max=None,
                 coverage=20,
                 read_len=150,
                 barcode_len=5,
                 barcode2_len=0,
                 ierr=0.001,
                 ferr=0.01,
                 min_distance=1000,
                 base_locus_length=1000,
                 max_n_prop=0.10,
                 output_format='fasta'):
        # Check inputs
        assert (library_type.lower() in ['sdrad', 'ddrad']), "Library types must be: sdRAD and ddRAD."
        assert (insert_mu < base_locus_length), f"Insert size mean ({insert_mu}) must be smaller than base locus length ({base_locus_length:,})."
        assert (insert_mu > read_len), f"Insert size mean ({insert_mu}) must be greater than read length ({read_len})."
        if insert_max is not None:
            assert (insert_max < base_locus_length), f"Insert size max ({insert_max}) must be smaller than base locus length ({base_locus_length:,})."
            assert insert_min is not None, "Error: must specify both min-insert and max-insert options."
        if insert_min is not None:
            assert insert_max is not None, "Error: must specify both min-insert and max-insert options."
        assert 0 <= max_n_prop < 1.0, f"Max proportion of Ns in reference sequence must be >= 0 and < 1."
        assert min_distance >= base_locus_length, f"Min inter-locus ({min_distance}) distance must be >= than base locus length ({base_locus_length:,})."
        # General library options
        self.type = library_type.lower()                    # library type (ddRAD, sdRAD (aka baird))
        self.renz_1 = RestrictionEnzyme(renz_1)             # name of first restriction enzyme
        self.min_dist = min_distance                        # mininum inter-locus distance
        self.cov = coverage                                 # per-locus sequencing coverage
        self.rlen = read_len                                # read length in bp
        self.base_len = base_locus_length                   # base length of a locus
        self.max_n_prop = max_n_prop                        # Maximum proportion of Ns in the refernece locus sequence
        # sdRAD options
        self.ins_mu = insert_mu                             # insert size mean
        self.ins_sig = insert_sigma                         # insert size standard deviation
        self.ins_len = lambda: int(np.random.normal(self.ins_mu, self.ins_sig))
        # ddRAD options
        self.renz_2 = RestrictionEnzyme(renz_2)             # name of second restriction enzyme (for ddRAD)
        self.ins_min = None                                 # insert size min for ddRAD
        if insert_min is None:
            # Calculate based on the size distributon, min = mean - (2x st.dev)
            self.ins_min = int(insert_mu - (insert_sigma * 2))
        else:
            # Provide absolute min value.
            self.ins_min = insert_min
        assert (self.ins_min > self.rlen), f"Minimum insert size ({self.ins_min}) must be greater than read length ({self.rlen})."
        self.ins_max = None                                 # insert size max for ddRAD
        if insert_max is None:
            # Calculate based on the size distributon, max = mean + (2x st.dev)
            self.ins_max = int(insert_mu + (insert_sigma * 2))
        else:
            # Provide absolute max value
            self.ins_max = insert_max
        assert self.ins_max < self.base_len, f"Maximum insert size ({self.ins_max}) must be smaller than base locus length ({self.base_len})."
        assert self.ins_min < self.ins_max
        # Override insert mean and stdev
        if insert_min is not None and insert_max is not None:
            self.ins_mu  = int((self.ins_min+self.ins_max)/2)
            self.ins_sig = int((self.ins_max-self.ins_mu)/2)
        # Barcodes
        assert barcode_len < self.rlen, f"Barcode 1 length ({barcode_len}) must be smaller than read length ({self.rlen})"
        assert barcode2_len < self.rlen, f"Barcode 2 length ({barcode_len}) must be smaller than read length ({self.rlen})"
        self.bar_len = barcode_len                          # length of the sample barcode in forward read
        self.bar2_len = barcode2_len                        # length of the sample barcode in reverse read
        # Sequencing error parameters
        assert 0.0 <= ierr < 1.0, f"Probability of error at the 5' end ({ierr}) must be between 0 and 1"
        assert 0.0 <= ferr < 1.0, f"Probability of error at the 3' end ({ferr}) must be between 0 and 1"
        assert ferr >= ierr, f"3'-end error ({ferr}) but be higher than 5'-end error."
        self.ierr = ierr                                    # 5' error
        self.ferr = ferr                                    # 3' error
        big_int = 1e6
        self.err_probs = (big_int,
            np.array([
                int( (self.ierr + (self.ferr - self.ierr) / (self.rlen - 1) * i) * big_int) for i in range(self.rlen)
                ], dtype=np.int64) )
        # Format for the output reads
        output_format = output_format.lower()
        assert output_format in ['fasta', 'fastq']
        self.out_fmt = output_format
    def __str__(self):
        if self.type == 'sdrad':
            return f'''RAD Library Options:
    library type:            sdRAD
    restriction enzyme:      {self.renz_1.name} ({self.renz_1.cut_pattern})
    insert size mean:        {self.ins_mu} bp
    insert size std dev:     {self.ins_sig} bp
    read length:             {self.rlen} bp
    sequencing coverage:     {self.cov} x
    read1 barcode length:    {self.bar_len} bp
    read2 barcode length:    {self.bar2_len} bp
    5' sequencing error:     {self.ierr:.6g}
    3' sequencing error:     {self.ferr:.6g}
    base locus length:       {self.base_len:,} bp
    min locus distance:      {self.min_dist:,} bp
    max proportion Ns:       {self.max_n_prop:.6g}'''

        elif self.type == 'ddrad':
            return f'''RAD Library Options:
    library type:            ddRAD
    restriction enzyme 1:    {self.renz_1.name} ({self.renz_1.cut_pattern})
    restriction enzyme 2:    {self.renz_2.name} ({self.renz_2.cut_pattern})
    insert size mean:        {self.ins_mu} bp
    insert size min:         {self.ins_min} bp
    insert size max:         {self.ins_max} bp
    read length:             {self.rlen} bp
    sequencing coverage:     {self.cov} x
    read1 barcode length:    {self.bar_len} bp
    read2 barcode length:    {self.bar2_len} bp
    5' sequencing error:     {self.ierr:.6g}
    3' sequencing error:     {self.ferr:.6g}
    base locus length:       {self.base_len:,} bp
    min locus distance:      {self.min_dist:,} bp
    max proportion Ns:       {self.max_n_prop:.6g}'''

#
# Base RADtag Class
# Class is just for quick tally of loci number
class RADTag:
    def __init__(self, chrom_id, cut_position, start_bp, end_bp, direction, lib_type, no_cuts=False):
        assert direction in ['positive', 'negative']
        assert lib_type in ['sdrad', 'ddrad']
        assert type(no_cuts) is bool
        self.id = id
        self.chrom = chrom_id
        self.cut = cut_position
        self.sta = start_bp
        self.end = end_bp
        self.dir = direction
        self.type = lib_type
        self.nocuts = no_cuts
    def __str__(self):
        return f'{self.chrom}\t{self.cut}\t{self.dir}\t{self.sta}\t{self.end}'

#
# Function to do second digest of the base locus
def double_digest(sequence, enzyme, library_opts=LibraryOptions()):
    '''
    Find the second restriction digest site for a sequence that has the main (5\') cutter.

    Args:
        sequence : (str) Sequence of the locus
        enzyme : (RestrictionEnzyme) common cutter enzyme
        library_opts : (LibraryOptions) configuration and options for the library

    Returns:
        kept_cutsites : (list) list of the indexes of the second cutsites in the sequence. Length 0 when none are found in range, (None) when none are found AT ALL.
'''
    # Check inputs
    assert isinstance(enzyme, RestrictionEnzyme)
    assert isinstance(library_opts, LibraryOptions)
    # Find all cutsites in base sequence
    raw_cuts = [ match.start() for match in re.finditer(enzyme.cutsite, sequence) ]
    # Return None when no cutsites are found AT ALL
    if len(raw_cuts) == 0:
        return None
    # Filter cutsites
    kept_cutsites = list()
    for cut in raw_cuts:
        if library_opts.ins_min <= cut <= library_opts.ins_max:
            kept_cutsites.append(cut)
    # Return the list of kept cutsites (empty when none in range)
    return kept_cutsites

# Function to find a base RADtag based on a sequence and a cut
def def_rad_tag(chrom_sequence, chrom_id, cut_position, direction, library_opts=LibraryOptions()):
    '''
    Find a base RAD-tag based on a sequence and enzyme cutsites

    Args:
        chrom_sequence : (str) reference sequence of a chromosome/scaffold
        chrom_id : (str) ID of the reference sequence
        cut_position : (int) position (index) of the main cutter in the sequence
        direction : (str) DNA strand orientation [positive, negative]
        library_opts : (LibraryOptions)

    Returns:
        rad_rag : RADTag object or None'''
    # Check class and types
    assert isinstance(library_opts, LibraryOptions)
    assert cut_position in range(0, len(chrom_sequence))
    assert direction in ['positive', 'negative']
    rad_tag = None
    start_bp = None
    end_bp = None
    # Process sdRAD tags
    if library_opts.type == 'sdrad':
        # Define cutsite boundaries
        enz = library_opts.renz_1
        cutsite_first = cut_position
        cutsite_last  = cutsite_first + len(enz.cutsite) - 1
        # process depending on direction
        if direction == 'positive':
            # Define boundaries for positive tag
            start_bp = cutsite_first + (len(enz.cutsite) - len(enz.remainder))
            end_bp = start_bp + library_opts.base_len - 1
            rad_tag = RADTag(chrom_id, cut_position, start_bp, end_bp, direction, library_opts.type)
        else:
            # Define boundaries for negative tag
            end_bp = cutsite_first + len(enz.remainder) - 1
            start_bp = end_bp - library_opts.base_len + 1
            rad_tag = RADTag(chrom_id, cut_position, start_bp, end_bp, direction, library_opts.type)
    # Process ddRAD tags
    elif library_opts.type == 'ddrad':
        # Define first cutsite boundaries
        enz = library_opts.renz_1
        cutsite_first = cut_position
        cutsite_last  = cutsite_first + len(enz.cutsite) - 1
        # ddRAD parameters
        enz_2 = library_opts.renz_2
        # process depending on direction
        if direction == 'positive':
            # Define boundaries for positive tag
            start_bp = cutsite_first + (len(enz.cutsite) - len(enz.remainder)) # for first
            end_bp = start_bp + library_opts.base_len - 1 # for last
            # get base sequence
            seq = chrom_sequence[start_bp:end_bp+1]
            # double digest
            dd_cuts = double_digest(seq, enz_2, library_opts)
            if dd_cuts is None:
                rag_tag = None
            elif len(dd_cuts) == 0:
                end_bp = start_bp + library_opts.ins_max-1
                rad_tag = RADTag(chrom_id, cut_position, start_bp, end_bp, direction, library_opts.type, no_cuts=True)
            else:
                # create new tag
                end_bp = start_bp + max(dd_cuts) + len(enz_2.cutsite) - 1
                rad_tag = RADTag(chrom_id, cut_position, start_bp, end_bp, direction, library_opts.type)
        # For negative loci
        else:
            # Define boundaries for negative tag
            end_bp = cutsite_first + len(enz.remainder) - 1 # rev last
            start_bp = end_bp - library_opts.base_len + 1   # rev fist
            # get base sequence
            seq = rev_comp(chrom_sequence[start_bp:end_bp+1])
            # double digest
            dd_cuts = double_digest(seq, enz_2, library_opts)
            if dd_cuts is None:
                rag_tag = None
            elif len(dd_cuts) == 0:
                start_bp = start_bp - library_opts.ins_max-1
                rad_tag = RADTag(chrom_id, cut_position, start_bp, end_bp, direction, library_opts.type, no_cuts=True)
            else:
                # create new tag
                start_bp = end_bp - max(dd_cuts) - len(enz_2.cutsite) + 1
                rad_tag = RADTag(chrom_id, cut_position, start_bp, end_bp, direction, library_opts.type)
    # return rad_tag
    return rad_tag

#
# Reference Locus Class
class ReferenceRADLocus:
    def __init__(self, locus_id, chromosome, cutsite_bp, start_bp, end_bp, sequence, loc_type='sdrad'):
        self.id = locus_id
        self.chrom = chromosome
        self.cut = cutsite_bp
        self.sta = start_bp
        self.end = end_bp
        self.seq = sequence
        self.type = loc_type
        self.dir = None
        if locus_id[-1] == 'p':
            self.dir = 'positive'
        elif locus_id[-1] == 'n':
            self.dir = 'negative'
    def __str__(self):
        return '{}\t{}\t{}\t{}\t{}'.format(self.id, self.chrom, self.cut, self.sta, self.end)

#
# Function to find RAD loci in a chromosome sequence.
# Returns a list containing all the tag coordinates for a given sequence
def find_loci(chrom_name, chrom_sequence, locus_stat_dict, library_opts=LibraryOptions(), log_f=None):
    '''
    Find RAD loci for a single chromosome/scaffold sequence

    Args:
        chrom_name : (str) chromosome/scaffold ID
        chrom_sequence : (str) chromosome/scaffold sequence
        locus_stat_dict : (dict) dictonary tallying the status of each locus
        library_opts : (LibraryOptions) library configuration and options

    Returns:
        kept_tags : (list) kept tags (in RADTag format)
        locus_stat_dict : (dict) updated tally dictionary
        '''
    # Check variables and classes
    assert isinstance(library_opts, LibraryOptions)
    enz = library_opts.renz_1
    raw_cuts = [ match.start() for match in re.finditer(enz.cutsite, chrom_sequence) ]
    # Filter cutsites - generate two tags per cutsite
    kept_tags = list()
    # Iterate over all the found cuts
    for i, cut in enumerate(raw_cuts):
        tag_dir = None
        rad_tag = None
        # For each cut, process both directions
        for direction in ['negative', 'positive']:
            # Cutsite status
            status = 'kept'
            tag_dir = direction
            # Get corresponding tag
            rad_tag = def_rad_tag(chrom_sequence, chrom_name, cut, tag_dir, library_opts)
            if rad_tag is None:
                # Skip None from the get go
                status = None
                continue
            else:
                assert isinstance(rad_tag, RADTag)

            # Process sdRAD loci
            if library_opts.type == 'sdrad':
                # Define cut boundaries
                cutsite_first = rad_tag.cut
                cutsite_last  = cutsite_first + len(enz.cutsite) - 1
                # First check if they are close to the chromosome ends
                if tag_dir == 'negative' and rad_tag.end < library_opts.base_len:
                    # Cutsite is close to the beginning, negative tag will start before 0
                    status = 'rm_chrom_end'
                elif tag_dir == 'positive' and rad_tag.end+1 >= len(chrom_sequence):
                    # Cutsite is close to the end, positive tag will go past the end of the sequence
                    status = 'rm_chrom_end'
                # Check if they are too close to nearest site
                # Positive tags can "hit" the next tag
                elif tag_dir == 'positive' and i < len(raw_cuts)-1:
                    next_cut = raw_cuts[i+1]
                    next_end = next_cut + len(enz.remainder)
                    assert next_end > rad_tag.sta
                    if (next_end-rad_tag.sta) < library_opts.min_dist:
                        status = 'rm_too_close'
                # The negative tags can "hit" the previous tag
                elif tag_dir == 'negative' and i > 0:
                    prev_cut = raw_cuts[i-1]
                    prev_sta = prev_cut+(len(enz.cutsite)-len(enz.remainder))
                    assert rad_tag.end > prev_sta
                    if (rad_tag.end-prev_sta) < library_opts.min_dist:
                        status = 'rm_too_close'
                # Check if they have too many Ns
                tag_seq = chrom_sequence[ rad_tag.sta : rad_tag.end + 1 ]
                tag_ns = tag_seq.upper().count('N')
                if tag_ns > (library_opts.base_len * library_opts.max_n_prop):
                    status = 'rm_excess_Ns'

            # Process ddRAD loci
            elif library_opts.type == 'ddrad':
                # Define cut boundaries
                cutsite_first = rad_tag.cut
                cutsite_last  = cutsite_first + len(enz.cutsite) - 1
                # First check if they are close to the chromosome ends
                if tag_dir == 'negative' and rad_tag.end < library_opts.base_len:
                    # Cutsite is close to the beginning, negative tag will start before 0
                    status = 'rm_chrom_end'
                elif tag_dir == 'positive' and rad_tag.end+1 >= len(chrom_sequence):
                    # Cutsite is close to the end, positive tag will go past the end of the sequence
                    status = 'rm_chrom_end'
                # Check if the locus has dd-cuts, but they're outside the range
                elif rad_tag.nocuts:
                    status = 'rm_no_dd_cuts'
                # Check if they are too close to nearest site
                # Positive tags can "hit" the next tag
                elif tag_dir == 'positive' and i < len(raw_cuts)-1:
                    # Define next cut
                    next_cut = raw_cuts[i+1]
                    next_neg_tag = def_rad_tag(chrom_sequence, chrom_name, next_cut, 'negative', library_opts)
                    # If None, previous tag is not a cutsite, so ignore
                    if next_neg_tag is not None:
                        assert next_neg_tag.end > rad_tag.sta, f'{next_neg_tag} - {rad_tag}'
                        if (next_neg_tag.end-rad_tag.sta) < library_opts.min_dist:
                            status = 'rm_too_close'
                # The negative tags can "hit" the previous tag
                elif tag_dir == 'negative' and i > 0:
                    # Re-define previous cut
                    prev_cut = raw_cuts[i-1]
                    next_pos_tag = def_rad_tag(chrom_sequence, chrom_name, prev_cut, 'positive', library_opts)
                    # If None, previous tag is not a cutsite, so ignore
                    if next_pos_tag is not None:
                        assert rad_tag.end > next_pos_tag.sta
                        if (rad_tag.end-next_pos_tag.sta) < library_opts.min_dist:
                            status = 'rm_too_close'
                # Check if they have too many Ns
                tag_seq = chrom_sequence[ rad_tag.sta : rad_tag.end + 1 ]
                tag_ns = tag_seq.upper().count('N')
                if tag_ns > (len(tag_seq) * library_opts.max_n_prop):
                    status = 'rm_excess_Ns'

            # Save the Tag if kept
            if status == 'kept':
                kept_tags.append(rad_tag)
            # Write into log file
            if log_f is not None and status is not None:
                # chrom_id cut_pos tag_dir status
                log_f.write(f'{chrom_name}\t{cut}\t{tag_dir[0:3]}\t{status}\n')
            # Increment tally
            locus_stat_dict.setdefault(status, 0)
            locus_stat_dict[status] += 1
            # print(rad_tag, status)
    # Return the good tags only and the current tally
    return kept_tags, locus_stat_dict

# Print the locus statistics distribution to the log
def report_locus_stats(locus_stat_dict, out_dir='.', library_opts=LibraryOptions):
    '''
    Print the tally of locus statistics to the raditinio.log
    Args:
        locus_stat_dict : (dict) Locus stats dictionary
        out_dir : (str) Path to output directory
        library_opts : (LibraryOptions) Library configuration
    Returns:
        None'''
    total = sum(locus_stat_dict.values())
    # Process as single or double digest
    if library_opts.type == 'sdrad':
        print(f'    Found a total of {total:,} {library_opts.renz_1.name} loci in the genome (use this number for coverage calculations).', flush=True)
    elif library_opts.type == 'ddrad':
        no_dd_cut = locus_stat_dict.get('rm_no_dd_cuts', 0)
        total = total - no_dd_cut
        print(f'    Found a total of {total:,} {library_opts.renz_1.name}-{library_opts.renz_2.name} loci (insert size range: {library_opts.ins_min}-{library_opts.ins_max}bp) in the genome (use this number for coverage calculations).', flush=True)
        # No dd cut
        if no_dd_cut > 0:
            print(f'    Note: an additional {no_dd_cut:,} loci were found outside the target insert size range.', flush=True)
    # Too close to the ends
    rm_chrom_end = locus_stat_dict.get('rm_chrom_end', 0)
    if rm_chrom_end> 0:
        print(f'    Removed {rm_chrom_end:,} loci ({rm_chrom_end/total:.1%}) too close to the ends of the reference sequences.', flush=True)
    # Excess Ns in sequence
    rm_excess_ns = locus_stat_dict.get('rm_excess_Ns', 0)
    if rm_excess_ns > 0:
        print(f'    Removed {rm_excess_ns:,} loci ({rm_excess_ns/total:.1%}) containing excess (>{library_opts.max_n_prop:.1%}) of Ns in sequence.')
    # Too close
    rm_too_close = locus_stat_dict.get('rm_too_close', 0)
    if rm_too_close > 0:
        print(f'    Removed {rm_too_close:,} loci ({rm_too_close/total:.1%}) in close proximity (<{library_opts.min_dist}bp) to another locus.', flush=True)
    # Kept
    kept = locus_stat_dict.get('kept', 0)
    p_kept = kept/total
    print(f'    Retained {kept:,} loci ({p_kept:.1%}) for downstream analysis.', flush=True)
    # Summary
    print(f'\n    See `{out_dir}/reference_rad_loci.stats.gz` for a detailed description of the per-cutsite position and status.', flush=True)
    return


#
# Extract reference RAD loci from reference genome
# Returns dictionary of all loci ID and positions
# Also writes reference RAD loci fasta and statistics file
def extract_reference_rad_loci(genome_dict, out_dir, library_opts=LibraryOptions()):
    '''
    Tally and process the reference RAD loci in a reference FASTA
    
    Args:
        genome_dict : (dict) Dictionary of the reference sequences
        out_dir : (str) path to output directory
        library_opts : (LibraryOptions) library configuration and options

    Returns:
        loci_dict : (dict) Dictionary of the reference RAD loci (as ReferenceRADLocus objects)
    '''
    print('\nExtracting RAD loci...', flush=True)
    # Check for class types and directories.
    assert type(genome_dict) == dict
    assert isinstance(library_opts, LibraryOptions)
    out_dir = out_dir.rstrip('/')
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    elif not os.path.isdir(out_dir):
        sys.exit('oops')
    # Open output FASTA and stats file.
    enz = library_opts.renz_1
    fa_f = gzip.open(f'{out_dir}/reference_rad_loci.fa.gz', 'wt')
    stats_log = gzip.open(f'{out_dir}/reference_rad_loci.stats.gz', 'wt')
    stats_log.write('#chrom_id\tcut_pos\ttag_dir\tstatus\n')
    # Make the locus status dictionary
    locus_stat_dict = dict()
    # Tag ID information
    tag_dict = dict()
    loc_num = -1
    # Loop throught chromosomes
    for chrom in sorted(genome_dict):
        chromosome = genome_dict[chrom]
        assert isinstance(chromosome, Chromosome)
        # Find tags in that chromosome and increment tally
        chrom_tags, locus_stat_dict = find_loci(chrom, chromosome.seq, locus_stat_dict, library_opts, log_f=stats_log)
        tag_dict[chrom] = chrom_tags
    # Determine total number of kept tags.
    total_tags = locus_stat_dict['kept']
    # Create dictionary of all reference RAD loci
    loci_dict = dict()
    # Each locus is a ReferenceRADLocus() class object
    # loci_dict = { chrom1 : { loc1 : RefLoc1, loc2 : RefLoc2 },
    #               chrom2 : { loc3 : RefLoc3, loc4 : RefLoc4 } }
    # Loop throught chromosomes again, extract tags, and convert to Loci objects
    for chrom in sorted(genome_dict):
        chromosome = genome_dict[chrom]
        assert isinstance(chromosome, Chromosome)
        chrom_loci = dict()   # Loci in this chromosome.
        # Loop through tags and process
        for tag in tag_dict[chrom]:
            assert isinstance(tag, RADTag)
            loc_num += 1
            # Process positive tags
            if tag.dir == 'positive':
                seq = chromosome.seq[ tag.sta : tag.end + 1 ]
                l_id = 't{{:0{}d}}p'.format(len(str(total_tags))).format(loc_num)
                if 'N' not in seq:
                    # Save as a ReferenceLocus object in loci dictionary
                    this_locus = ReferenceRADLocus(l_id, chrom, tag.cut, tag.sta, tag.end, seq, loc_type=library_opts.type)
                    chrom_loci[l_id] = this_locus
                    # Save as an entry in FASTA file
                    fa_f.write(f'>{this_locus.id} ref_pos={this_locus.chrom}:{(this_locus.sta+1)}-{(this_locus.end+1)}\n{this_locus.seq}\n')
            # Process negative tags
            else:
                seq = rev_comp(chromosome.seq[ tag.sta : tag.end + 1 ])
                l_id = 't{{:0{}d}}n'.format(len(str(total_tags))).format(loc_num)
                if 'N' not in seq:
                    # Save as a ReferenceLocus object in loci dictionary
                    this_locus = ReferenceRADLocus(l_id, chrom, tag.cut, tag.sta, tag.end, seq, loc_type=library_opts.type)
                    chrom_loci[l_id] = this_locus
                    # Save as an entry in FASTA file
                    fa_f.write(f'>{this_locus.id} ref_pos={this_locus.chrom}:{(this_locus.sta+1)}-{(this_locus.end+1)}\n{this_locus.seq}\n')
        loci_dict[chrom] = chrom_loci
    # Pretty print the tally dictionary
    report_locus_stats(locus_stat_dict, out_dir, library_opts)
    return loci_dict

# Substitution matrices
substitution_matrices = {
               # A    C    G    T
    # Equal probability across all states
    'equal' : [[0.0, 1/3, 1/3, 1/3],  # A
               [1/3, 0.0, 1/3, 1/3],  # C
               [1/3, 1/3, 0.0, 1/3],  # G
               [1/3, 1/3, 1/3, 0.0]], # T
    # Transitions are 2x more likely
    'ts'    : [[0.0, 1/4, 1/2, 1/4],  # A
               [1/4, 0.0, 1/2, 1/4],  # C
               [1/2, 1/4, 0.0, 1/4],  # G
               [1/4, 1/2, 1/4, 0.0]], # T
    # Transversions are 2x more likely
    'tv'    : [[0.0, 2/5, 1/5, 2/5],  # A
               [2/5, 0.0, 2/5, 1/5],  # C
               [1/5, 2/5, 0.0, 2/5],  # G
               [2/5, 1/5, 2/5, 0.0]]  # T
}

# Class defining substitution probabilities
class MutationModel:
    def __init__(
            self,
            substitution_matrix = 'equal',                 # Equal probability across all
            indel_prob = 0.01,                             # 1% indels
            ins_del_ratio = 1.0,                           # 1:1 insertions and deletions
            indel_model = lambda: np.random.poisson(lam=1) ):
        assert substitution_matrix in substitution_matrices.keys(), f"Subsitution matrices must be in ['equal', 'ts', 'tv']"
        assert 0.0 <= indel_prob <= 0.25, f"Probability of indels ({indel_prob}) must be between 0.0 and 0.25"
        assert 0.0 <= ins_del_ratio, f"Insertion/deletion ratio ({ins_del_ratio}) must be greater than 0."
        self.indel_p = indel_prob
        self.ins_del_ratio = ins_del_ratio
        sub_p = 1 - self.indel_p                           # prob of a substitution
        del_p = self.indel_p / (1 + self.ins_del_ratio)    # prob of a deletion
        ins_p = self.indel_p - del_p                       # prob of an insertion
        self.sub_mat = substitution_matrices[substitution_matrix]
        self.subs = substitution_matrix
        m = self.sub_mat
        a, c, g, t = m[0], m[1], m[2], m[3]                # per nucleotide probs
        self.mutation_matrix = [
            (['C', 'G', 'T', 'I', 'D'],                    # for ref = A
                [a[1]*sub_p, a[2]*sub_p, a[3]*sub_p, ins_p, del_p]),
            (['A', 'G', 'T', 'I', 'D'],                    # for ref = C
                [c[0]*sub_p, c[2]*sub_p, c[3]*sub_p, ins_p, del_p]),
            (['A', 'C', 'T', 'I', 'D'],                    # for ref = G
                [g[0]*sub_p, g[1]*sub_p, g[3]*sub_p, ins_p, del_p]),
            (['A', 'C', 'G', 'I', 'D'],                    # for ref = T
                [t[0]*sub_p, t[1]*sub_p, t[2]*sub_p, ins_p, del_p]) ]
        self.indel_s = indel_model
    # Function to generate random mutations, like in PCR or sequencing error
    def random_mutation(self, ref):
        mutations_comb = {
            'A' : ['C','G','T'],
            'C' : ['A','G','T'],
            'G' : ['A','C','T'],
            'T' : ['A','C','G']}
        if ref in mutations_comb:
            return mutations_comb[ref][np.random.randint(3)]
        elif ref == 'N':
            return 'N'
        else:
            print('Mutating a non \'ACGT\', non-N nucleotide!', file=sys.stderr)  # FIXME: @Angel 20190510: Should this be the right way of handing this?
            return 'N'
    # Function to mutate reference allele for simulated variants
    def mutate(self, variant_position, chrom_sequence):
        nucleotides = ['A', 'C', 'G', 'T']
        ref = chrom_sequence[variant_position]
        alt = None
        if ref == nucleotides[0]:                     # for ref = A
            mut_pattern = self.mutation_matrix[0]
            alt = np.random.choice(mut_pattern[0], p = mut_pattern[1])
        elif ref == nucleotides[1]:                   # for ref = C
            mut_pattern = self.mutation_matrix[1]
            alt = np.random.choice(mut_pattern[0], p = mut_pattern[1])
        elif ref == nucleotides[2]:                   # for ref = G
            mut_pattern = self.mutation_matrix[2]
            alt = np.random.choice(mut_pattern[0], p = mut_pattern[1])
        elif ref == nucleotides[3]:                   # for ref = T
            mut_pattern = self.mutation_matrix[3]
            alt = np.random.choice(mut_pattern[0], p = mut_pattern[1])
        # else:
        #     assert False
        elif ref not in nucleotides:                  # for ref = N
            alt = 'N'
            return 'N','N'
        # Return values for substitutions
        if alt in nucleotides:
            assert ref != None or alt != None
            return ref, alt
        # Check for indels in alternative alleles
        elif alt in ['I', 'D']:
            # If Insertion
            if alt == 'I':
                size = 0
                # Determine size of insertion
                while size == 0:
                    size = self.indel_s()
                insert = [ref]
                for i in range(size):
                    insert.append(random.choice('ACGT'))
                # Return return ref and insertion
                assert ''.join(insert) != None or len(''.join(insert)) >= 1
                return ref, ''.join(insert)
            # If Deletion
            elif alt == 'D':
                deletion = None
                # Determine size of deletion
                size = 0
                while size == 0:
                    size = self.indel_s()
                # Determine position where deletion ends in sequence
                del_end = variant_position + size + 1
                # What if the mutation is on the last bp? Change to random substitution. This is unlikely, but its an important fix to have.
                if variant_position == len(chrom_sequence) - 1:
                    deletion = ref
                    ref = self.random_mutation(deletion)
                # For all other "normal" cases...
                if del_end <= len(chrom_sequence):
                    deletion = chrom_sequence[variant_position:del_end]
                else:
                    deletion = chrom_sequence[variant_position:len(chrom_sequence)]
                # Return deletion and ref
                return deletion, ref
    # Function to print output to log
    def __str__(self):
        return f'''Mutation options:
    substution model:        {self.subs}
    indel probability:       {self.indel_p:.6g}
    insert/deletion ratio:   {self.ins_del_ratio:.6g}'''

#
# Function to merge msprime VCFs into master VCF
#
def merge_vcf(genome_dict : dict,
              msp_vcf_dir : str,
              out_dir : str,
              mutation_opts : MutationModel=MutationModel() ) -> None:
    '''
    Merge simulated VCFs and adjust alleles based on reference.

    Args:
        genome_dict:   dictionary containing the genome sequence objects
        msp_vcf_dir:   path to the simulated VCFs directory
        out_dir:       path to output directory
        mutation_opts: a MutationModel class object

    Returns:
        None
    '''
    # Check variables and classes
    assert type(genome_dict) == dict
    assert isinstance(mutation_opts, MutationModel)
    msp_vcf_dir = msp_vcf_dir.rstrip('/')
    out_dir = out_dir.rstrip('/')
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    elif not os.path.isdir(out_dir):
        sys.exit('oops')
    # open output file
    out_f = gzip.open('{}/ri_master.vcf.gz'.format(out_dir), 'wt')
    # work on the vcf header
    out_f.write(f'##fileformat=VCFv4.2\n##fileDate={date()}\n##source=RADinitio version {__version__} - radinitio.merge_vcf()\n##FILTER=<ID=PASS,Description="All filters passed">\n')
    for chrom in sorted(genome_dict):
        out_f.write(f'##contig=<ID={chrom},length={genome_dict[chrom].len}>\n')
    out_f.write('##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n')
    # Keep tally of sites seen and kept
    sites_seen = 0
    sites_kept = 0
    n_sim_vcfs = 0
    # Loop throught chromosomes
    for chr_i, chrom in enumerate(sorted(genome_dict)):
        assert isinstance(genome_dict[chrom], Chromosome)
        # Extract working sequence
        seq = genome_dict[chrom].seq
        prev_pos = 0
        # Open msprime VCF
        for line in gzip.open(f'{msp_vcf_dir}/{chrom}.vcf.gz', 'rt'):
            n_sim_vcfs += 1
            # Extract vcf header
            msp = []
            iden = []
            # Process sample IDs
            if line.startswith('#'):
                if line.startswith('#CHROM') and chr_i == 0:
                    fields = line.strip('\n').split('\t')
                    for f in fields:
                        if f[0:3] in ('msp', 'tsk'):
                            msp.append(f)
                        else:
                            iden.append(f)
                    # Determine pad size based on the length of largest sample number
                    pad = '0{}d'.format(len(msp[-1][4:]))
                    for m in range(len(msp)):
                        iden.append('msp_' + str(format(m, pad)))
                    out_f.write('\t'.join(iden)+'\n')
                continue
            # Process Genotype lines
            sites_seen += 1
            fields = line.strip('\n').split('\t')
            pos = int(fields[1]) - 1 # 0-based position of the SNP in the reference sequence
            # In case any simulated positions are larger than the reference chromosome...
            if pos >= len(seq):
                break
            fields[0] = chrom # chromosome ID
            # Remove variants if they are overlapping with indel sizes
            if pos <= prev_pos:
                continue
            # determine the new sequences of the reference and alternative alleles
            fields[3], fields[4] = mutation_opts.mutate(pos, seq)
            # If we are dealing with an indel, increase the prev_pos value.
            if len(fields[3]) > 1 or len(fields[4]) > 1:
                prev_pos = pos + len(fields[3])
            # Remove Ns
            if fields[3] == 'N':
                continue
            # Write new VCF line
            sites_kept += 1
            out_f.write('\t'.join(fields)+'\n')
    out_f.close()
    # Report to logs
    print(f'    Read {sites_seen:,} total variants across {n_sim_vcfs:,} simulated VCFs.', flush=True)
    print(f'    Kept {sites_kept:,} total variants in the merged VCF.', flush=True)

#
# Function to create a RAD position set dictionary for variant filtering
# Input is the 'loci_dict' from 'extract_reference_rad_loci()'
def create_rad_pos_set_dict(loci_dict):
    # Create empty output dictionary
    pos_set_dict = dict()
    # iterate over chroms in loci_dict
    for chrom in sorted(loci_dict):
        curr_chrom_dict = dict()
        # Iterate over the chromosome's loci
        for locus in sorted(loci_dict[chrom]):
            curr_locus = loci_dict[chrom][locus]
            assert isinstance(curr_locus, ReferenceRADLocus)
            # Select data current locus
            l_sta = curr_locus.cut        # keep information of the WHOLE cutsite so you can filter cut variants properly
            l_end = curr_locus.end + 1    # end of locus
            # iterate over range in locus
            for bp in range(l_sta, l_end):
                curr_chrom_dict.setdefault(bp, []).append(locus)
        pos_set_dict[chrom] = curr_chrom_dict
    return pos_set_dict

#
# Set the RAD Variant class and related variables
# Structure: (locus_id, bp, A, T, 1101100010)
class RADVariant:
    def __init__(self, locus_id, position_bp, ref_allele, alt_allele, genotypes, cut_var=False):
        self.loc = locus_id
        self.pos  = position_bp # AKA column
        self.ref  = ref_allele
        self.alt  = alt_allele
        self.geno = genotypes
        # Set the different types of variants
        self.type = None
        if len(self.ref) == len(self.alt):
            self.type = 'substitution'
        elif len(self.ref) > 1:
            self.type = 'deletion'
        elif len(self.alt) > 1:
            self.type = 'insertion'
        # Check if variant cutsite; True or False
        self.cut_variant = cut_var
    # Function to extract specific genotype from 'geno' string
    def get_genotype(self, sample_i, allele_n):
        assert allele_n in [0, 1]
        genotype = int(self.geno[ (sample_i * 2) + allele_n ])
        assert genotype in [0, 1]
        return genotype
    def __str__(self):
        return '{}\t{}\t{}\t{}\t{}\t{}'.format(self.loc, self.pos, self.ref, self.alt, self.geno, self.cut_variant)

#
# Function to convert RAD variants from VCF line
def variant_vcf_to_rad(rad_locus, vcf_pos, vcf_ref, vcf_alt, vcf_genotype_str, library_opts=LibraryOptions()):
    # Check types and classes
    assert isinstance(rad_locus, ReferenceRADLocus)
    assert type(vcf_pos) == int
    column = None
    ref_al = vcf_ref
    alt_al = vcf_alt
    cutvar = False
    # Process negative (3' -> 5') locus
    if rad_locus.dir == 'negative':
        ref_al = rev_comp(vcf_ref)[::-1]
        alt_al = rev_comp(vcf_alt)[::-1]
        # convert bp to reverse col 5'->3'
        column = rad_locus.end - vcf_pos
    # Process positive loci
    elif rad_locus.dir == 'positive':
        # readjust from bp to col
        column = vcf_pos - rad_locus.sta
    # Process any variants in forward cutsite (for both sd and ddRAD)
    enz = library_opts.renz_1
    # For CC/TGCAGG
    #     |  |    |
    #   sta  0    end
    cut_sta = 0 - (len(enz.cutsite) - len(enz.remainder))
    cut_end = cut_sta + len(enz.cutsite) - 1
    if column in range(cut_sta, cut_end):
        cutvar = True
    # (locus_id, column, A, T, 01101001, False/True)
    variant = RADVariant(rad_locus.id, column, ref_al, alt_al, vcf_genotype_str, cut_var=cutvar)
    return variant

#
# Function to find and filter the RAD variants based on cutsite information
# TODO: Update logs.
def filter_rad_variants(loci_dict, pos_set_dict, m_vcf_dir, library_opts=LibraryOptions()):
    # Check variables and classes
    assert type(loci_dict) == dict
    assert type(pos_set_dict) == dict
    assert isinstance(library_opts, LibraryOptions)
    m_vcf_pdir = m_vcf_dir.rstrip('/')
    # create empty rad variant_dictonary
    # rad_variants_dict = { loc1 : [var1, var2, ...] , loc2 : [var1], loc3 : [] }
    rad_variants_dict = dict()
    # Open master VCF
    for line in gzip.open('{}/ri_master.vcf.gz'.format(m_vcf_dir), 'rt'):
        if line[0] == '#':
            # Skip comment and metadata lines
            continue
        else:
            fields = line.strip('\n').split('\t')
            chrom = fields[0]
            pos = int(fields[1]) - 1
            # Verify is variant is in RAD loci
            if chrom not in pos_set_dict:
                # Chrom in VCF not among the loci
                continue
            if pos not in pos_set_dict[chrom]:
                # Not a RAD position
                continue
            # If position among RAD loci
            variant = None
            # Loop over all loci that have that position
            loci = pos_set_dict[chrom][pos]
            for locus in loci:
                curr_locus = loci_dict[chrom][locus]
                # Parse other VCF elements
                ref_a = fields[3]
                alt_a = fields[4]
                genotypes = []
                for i in range(9, len(fields)):
                    genotypes.append(fields[i][0])
                    genotypes.append(fields[i][2])
                genotypes = ''.join(genotypes)
                # Define variant from VCF line
                variant = variant_vcf_to_rad(curr_locus, pos, ref_a, alt_a, genotypes, library_opts)
            # add to variant dictionary
            rad_variants_dict.setdefault(curr_locus.id, []).append(variant)
            # TODO: produce RAD VCF including dropped alleles
            # TODO: parallelize per chromosome?
    return rad_variants_dict

#
# Function to create allele from template sequence
def create_allele(ref_locus_sequence, locus_variants, allele_i, sample_i, library_opts=LibraryOptions()):
    # Check classes
    assert isinstance(library_opts, LibraryOptions)
    # Convert reference sequence into list for indexing
    seq_list = list(ref_locus_sequence)
    # Create base CIGAR
    cigar = f'{library_opts.base_len}M'
    # Keep cutsite?
    discard = False
    # Iterate over the variants
    for variant in locus_variants:
        assert isinstance(variant, RADVariant)
        # TODO: set the CIGARs
        # Check the genotype
        genotype = variant.get_genotype(sample_i, allele_i)
        if genotype == 1:
            # Process variant cutsites
            if variant.cut_variant == True:
                discard = True
                # IMMEDIATELY drop allele if cutsite is mutated
                break
            # In instance variant is not within locus
            if variant.pos not in range(0, len(seq_list)):
                continue
            # Process all other variants
            # For substitutions
            if variant.type == 'substitution':
                seq_list[variant.pos] = variant.alt
            # For insertions
            elif variant.type == 'insertion':
                seq_list[variant.pos] = variant.alt
            # For deletions
            elif variant.type == 'deletion':
                for bp in range(len(variant.ref) - 1):
                    # in deletions, you delete the nucleotides AFTER the variant position
                    del_i = variant.pos + bp + 1
                    try:
                        seq_list[del_i] = ''
                    # Stop if the deletion goes beyond the base sequence
                    except IndexError:
                        # print(variant)
                        continue
    allele_seq = ''.join(seq_list)
    # Check forward cutsite
    enzyme = library_opts.renz_1
    if not discard:
        cut_1 = allele_seq[:len(enzyme.remainder)]
        if cut_1 != enzyme.remainder:
            discard = True
    # Check reverse cutsite if ddRAD
    elif library_opts.type == 'ddrad':
        # Find all 'good' dd cutsites
        dd_cuts = double_digest(allele_seq, library_opts.renz_2, library_opts)
        if dd_cuts is None or len(dd_cuts) == 0:
            # Discard if no goood dd cutsites are found
            discard = True
    # Return new sequence string, new CIGAR (TODO), and status of allele
    return allele_seq, cigar, discard

#
# Function to extract alleles
# TODO: Update logs.
def extract_rad_alleles(loci_dict, rad_variants_dict, popmap_file, out_dir, library_opts=LibraryOptions(), ploidy = 2, log_f=None):
    # Check variables and classes
    assert type(loci_dict) == dict
    assert type(rad_variants_dict) == dict
    assert isinstance(library_opts, LibraryOptions)
    # Check output directory
    out_dir = out_dir.rstrip('/')
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    elif not os.path.isdir(out_dir):
        sys.exit('oops')
    # generate a sample list from popmap
    samples = list()
    for sample in open(popmap_file, 'r'):
        samples.append(sample.strip('\n').split('\t')[0])

    # Structure to keep track of dropped alleles
    #   locus_id             allele_1                    allele_2
    # { locus_1 : ( [sample_1, ..., sample_n ], [sample_1, ..., sample_n ] ),
    #  ...
    #   locus_n : ( [sample_1, ..., sample_n ], [sample_1, ..., sample_n ] ) }
    allele_stat_dict = dict()
    # Only do this if log is wanted
    if log_f is not None:
        for chrom in sorted(loci_dict):
            for loc_id in sorted(loci_dict[chrom]):
                alleles = [ [] for _ in range(ploidy) ]
                for i in range(ploidy):
                    samples_allele = [ '0' for _ in range(len(samples)) ]
                    alleles[i] = samples_allele
                allele_stat_dict[loc_id] = alleles

    # Iterate over the samples
    # TODO: split this into smaller function for parallelization
    for sam_i, sample in enumerate(samples):
        # create an output file for the sample
        al_fasta = gzip.open(f'{out_dir}/{sample}.alleles.fa.gz', 'wt')
        # iterate over the loci dictionary
        for chrom in sorted(loci_dict):
            for loc_id in sorted(loci_dict[chrom]):
                # Set sequence and variant info for the current locus
                curr_locus = loci_dict[chrom][loc_id]
                locus_vars = rad_variants_dict.get(curr_locus.id, []) # In case there are loci with no variants
                # Iterate over the number of alleles
                for allele in range(ploidy):
                    # Check if cutsite needs to be discarded
                    discard = False
                    # Generate allele sequence
                    allele_seq, allele_cig, discard = create_allele(curr_locus.seq, locus_vars, allele, sam_i, library_opts)
                    # Remove allele if needed
                    if discard == True:
                        # Store discarded status in dictionary
                        if log_f is not None:
                            allele_stat_dict[loc_id][allele][sam_i] = '1'
                        continue
                    # Save sequences into output file
                    al_fasta.write(f'>{curr_locus.id}:{sample}:a{allele+1:d} cig={allele_cig}\n{allele_seq}\n')

    # Report dropped alleles
    if log_f is not None:
        log_f.write('locus\tallele\t{}\n'.format('\t'.join(samples)))
        for loc_id in sorted(allele_stat_dict):
            for a_i, allele in enumerate(allele_stat_dict[loc_id]):
                log_f.write('{}\ta{}\t{}\n'.format(loc_id, a_i+1, '\t'.join(allele)))
    log_f.close()
    al_fasta.close()


#
# Function to load the alleles of a single sample
def load_sample_alleles(sample_name, alleles_dir, library_opts=LibraryOptions()):
    # Check variables and classes
    assert isinstance(library_opts, LibraryOptions)
    # Check input directory
    alleles_dir = alleles_dir.rstrip('/')
    if not os.path.isdir(alleles_dir):
        sys.exit('oops')
    # Set library parameters
    #enz = library_opts.renz_1
    # Create allele list
    alleles_list = []
    header = None
    # Open file and read
    alleles_fa = f'{alleles_dir}/{sample_name}.alleles.fa.gz'
    for line in gzip.open(alleles_fa, 'rt'):
        if line.startswith('>'):
            header = line[1:-1]
        else:
            alleles_list.append( (header, line[:-1]) )
    return alleles_list

#
# Determine number of desired reads to obtain a coverage
def target_reads(n_alleles, coverage):
    n_reads = (n_alleles // 2) * coverage
    return int(n_reads)

# sample and process a template molecule from all available alleles
def sample_a_template(alleles_list, library_opts=LibraryOptions()):
    # Check variables and classes
    assert type(alleles_list) == list
    assert isinstance(library_opts, LibraryOptions)
    allele = None
    insert_len = None
    # process templates for sdRAD
    if library_opts.type == 'sdrad':
        # Pick alleles
        allele = random.choice(alleles_list)
        insert_len = 0
        while not library_opts.rlen <= insert_len <= len(allele[1]):
            # sample insert length from insert distribution
            insert_len = library_opts.ins_len()
    # process template for ddRAD
    elif library_opts.type == 'ddrad':
        dd_cuts = None
        while dd_cuts is None:
            # Pick alleles
            allele = random.choice(alleles_list)
            # find all 'good' dd cutsites
            temp_dd_cuts = double_digest(allele[1], library_opts.renz_2, library_opts)
            # If no cuts are found at all, just sample new allele
            if temp_dd_cuts is None:
                dd_cuts = None
            elif len(temp_dd_cuts) > 0:
                dd_cuts = temp_dd_cuts
        # Once you find a "good" allele return one insert length
        insert_len = random.choice(dd_cuts) + len(library_opts.renz_2.remainder)
    # return: allele=(id, seq) , insert_len bp
    return allele, insert_len

# Split CIGAR string into CIGAR list
def split_cigar_str(cigar):
    splitcig = []
    prev = 0
    for i, c in enumerate(cigar):
        if c in ('M', 'I', 'D'):
            splitcig.append(cigar[prev:i+1])
            prev=i+1
    return splitcig

#
# Extracts a read CIGAR from its locus CIGAR.
def extract_read_cigar(cigar, start, read_len, allele_seq):
    # Convert CIGAR from CIGAR string to CIGAR list
    cig_l = split_cigar_str(cigar)
    cig_n = []
    ref_consumed = 0
    ref_len = len(allele_seq)
    read_consumed = 0
    # Check CIGAR operations
    for op in cig_l:
        type = op[-1]
        if not type in ('M','D','I'):
            raise Exception('MDI')
        size = int(op[:-1])
        # Fast forward to the read region.
        if len(cig_n) == 0:
            # For Matches
            if type == 'M':
                if ref_consumed + size <= start:
                    ref_consumed += size
                    continue
                elif ref_consumed < start:
                    consume = start - ref_consumed
                    ref_consumed += consume
                    size -= consume
            # For Deletions
            if type == 'D':
                start += size
                ref_consumed += size
                continue
            # For Insertions
            elif type == 'I':
                start -= size
                if ref_consumed <= start:
                    continue
                else:
                    size = ref_consumed - start
            # For Clipped regions at the end
            if ref_consumed > 0:
                cig_n.append('{}H'.format(ref_consumed))
        # Write the cigar operations within the reads.
        if type == 'M': # For Match
            consume = min(size, read_len - read_consumed)
            cig_n.append('{}M'.format(consume))
            read_consumed += consume
            ref_consumed += consume
        elif type == 'D': # For Dels
            cig_n.append(op)
            ref_consumed += size
        elif type == 'I': # For Ins
            consume = min(size, read_len - read_consumed)
            cig_n.append('{}I'.format(consume))
            read_consumed += consume
        # Break after the read.
        if read_consumed == read_len:
            if ref_consumed < ref_len:
                cig_n.append('{}H'.format(ref_len - ref_consumed))
            break
        else:
            assert read_consumed < read_len
    # Return new CIGAR string for the read
    return cig_n

# generate new name for a sampled template
def build_base_template_name(allele, insert_len, clone_i, library_opts=LibraryOptions()):
    # Check variables and classes
    assert isinstance(library_opts, LibraryOptions)
    # produce read name
    fields = allele[0].split(' ')
    # TODO: Process CIGAR
    assert fields[1].startswith('cig=')
    # cigar = fields[1][len('cig='):]
    # fw_read_cig = ''.join( extract_read_cigar(cigar, 0, (library_opts.rlen - library_opts.bar_len), allele[1]) )
    # rev_read_cig = ''.join( extract_read_cigar(cigar, (insert_len - (library_opts.rlen - library_opts.bar2_len) ), (library_opts.rlen - library_opts.bar2_len), allele[1])[::-1] )
    name = '{}:{}'.format(fields[0], clone_i + 1)
    return name

#
# Generate new sequence with a PCR mutation
def introduce_pcr_mutation(seq, insert_len, library_opts=LibraryOptions(), mutation_opts=MutationModel()):
    # Check variables and classes
    assert isinstance(library_opts, LibraryOptions)
    assert isinstance(mutation_opts, MutationModel)
    # Define forward and reverse read intervals within the sequence
    read_regions = list(range(0, library_opts.rlen)) + list(range((insert_len - library_opts.rlen), insert_len))
    # Choose a random position in sequence within the read regions
    pos = random.choice(read_regions)
    # Find alternative nucleotide for that position
    nuc = mutation_opts.random_mutation(seq[pos])
    return seq[:pos] + nuc + seq[pos+1:]

#
# Function to add sequencing errors to a sequence.
# `err_probs` as defined by LibraryOptions classs
def seq_error(seq, err_probs, mutation_opts=MutationModel()):
    # Check variables and classes
    assert isinstance(mutation_opts, MutationModel)
    # Make sure size of errors is the same as the read length
    assert len(err_probs[1]) == len(seq)
    lseq = list(seq)
    # Generate random integer list and compare agains err_probs
    rdm = np.random.randint(err_probs[0], size=len(seq))
    for i in range(len(seq)):
        if rdm[i] < err_probs[1][i]:
            lseq[i] = mutation_opts.random_mutation(lseq[i])
    return ''.join(lseq)

# function to generate template molecule (sheared allele sequence)
# Simulate sequencing process for a given read pair
def sequence_read_pair(allele, insert_len, library_opts=LibraryOptions()):
    # Check variables and classes
    assert isinstance(library_opts, LibraryOptions)
    fw_read = seq_error(allele[1][:library_opts.rlen], library_opts.err_probs)[:(library_opts.rlen - library_opts.bar_len)]
    rv_read = rev_comp(seq_error(allele[1][(insert_len - library_opts.rlen):insert_len], library_opts.err_probs))[:(library_opts.rlen - library_opts.bar2_len)]
    return fw_read, rv_read

#
# Determine number of average reads from
# the number of loci and coverage
def avg_num_reads(genome_dict, library_opts=LibraryOptions(), ploidy=2):
    # Check variables and classes
    assert type(genome_dict) == dict
    assert isinstance(library_opts, LibraryOptions)
    assert library_opts.cov != None
    # Define enzyme
    enz = library_opts.renz_1
    # Number of Tags
    tag_n = 0
    # Iterate over genome dict
    for chrom in sorted(genome_dict):
        chromosome = genome_dict[chrom]
        assert isinstance(chromosome, Chromosome)
        # Find the kept tags in each chromosome
        chrom_tags = find_loci(chrom, chromosome.seq, library_opts)
        tag_n += len(chrom_tags)
    assert tag_n != None
    # Calculate number of reads, tags x coverage
    n_reads = tag_n * library_opts.cov
    return n_reads

#
# PCR Model
#

# Determine number of per-clone PCR duplicates (size of clone)
# DEPRECATED IN RADINITIO v 1.2.0
def simulate_pcr_inherited_efficiency(mu, sigma, n_cycles):
    duplicates = 1
    # Probability of duplicating a read
    p = 0.0
    while not 0.0 < p <= 1.0:
        p = np.random.normal(mu, sigma)
    for i in range(n_cycles):
        duplicates += np.random.binomial(duplicates, p)
    return duplicates

# Overall distribution of PCR duplicates
#  This will determine clone size and frequency (probability)
#  Structure: Cpn, where p is the frequency of a clone of size n
#     [ Cp0, Cp1, Cp2, Cp3, Cp4, ... ]
# DEPRECATED IN RADINITIO v 1.2.0
def get_library_clone_size_distribution(pcr_model, n_sims=1e5):
    clone_histogram = {}
    for i in range(int(n_sims)):
        clone_size = pcr_model()
        clone_histogram.setdefault(clone_size, 0)
        clone_histogram[clone_size] += 1
    max_size = max(clone_histogram.keys())
    for i in range(max_size+1):
        clone_histogram.setdefault(i, 0)
    clone_histogram = [ clone_histogram[i] / n_sims for i in range(max_size+1) ]
    return clone_histogram

#
# Function to log convert the size clases of the amplified clone size distribution
# Converting the distribution will collapse size classes, decreasing the size of the distribution and improving efficiency
# DEPRECATED IN RADINITIO v 1.2.0
def log_convert_ampl_clone_dist(ampl_clone_size_distrib, base):
    # generate empy distribution of size x, where x is the log of the biggest clone in the original distribution
    a_max = len(ampl_clone_size_distrib) - 1
    log_ampl_clone_size_distrib = [ 0.0 for log_a in range(math.floor(math.log(a_max, base)) + 1) ]
    for a, prob in enumerate(ampl_clone_size_distrib):
        if a == 0:
            continue
        log_a = math.floor(math.log(a, base))
        log_ampl_clone_size_distrib[log_a] += prob
    assert 1.0-1e-9 < sum(log_ampl_clone_size_distrib) < 1.0+1e-9
    return log_ampl_clone_size_distrib

#
# Function to determine the clone sizes within a clone class
# log_a = is the log-transform of a clone size
def get_sizes_in_clone_class(log_a, base):
    assert log_a >= 0
    clone_class = range(
        math.ceil(base ** log_a),
        math.ceil(base ** (log_a + 1)) )
    if not clone_class:
        return None
    return clone_class
def get_clone_class_representative_value(log_a, base):
    if get_sizes_in_clone_class(log_a, base) is None:
        return None
    return round(base ** (log_a + 0.5))

#
# Calculate number of starting templates
# def total_molecules_per_sample(insert_bp, dna_ng, n_samples, frac_rad_molecules=0.01):
#     # The fraction of "good" RAD molecules when amplifying library.
#     # Takes into account frequency of cuts, size selection, adapters, etc.
#     avog = 6.022e23
#     nuc_w = 660
#     total_molecules = (( dna_ng * avog ) / ( insert_bp * 1e9 * nuc_w)) * frac_rad_molecules
#     return int(total_molecules//n_samples)

#
# Calculate number of mutated nodes in PCR clone tree
def mutated_node_freq(n_nodes):
    # 0 and 1 can never have mutations
    assert n_nodes >= 2
    # edges are the number of sucessful amplification reactions
    n_edges = n_nodes - 1
    # Mutations appear on a random edge
    edge_with_mut = np.random.randint(n_edges)
    # List storing the nodes count
    #   [no_mutations, mutations]
    nodes_cnt = [1 + edge_with_mut, 1]
    # Determine if later reactions stem from mutated node
    while (nodes_cnt[1] + nodes_cnt[0]) < n_nodes:
        # Prob of new mutated node
        p = nodes_cnt[1] / (nodes_cnt[1] + nodes_cnt[0])
        # Prob of new non-mutated node
        q = 1 - p
        # Select if new node is mutated (1) or not (0)
        i = np.random.choice([1, 0], p=[p, q])
        nodes_cnt[i] += 1
    # Return number of mutated nodes in the tree
    return nodes_cnt[1]

#
# Calculate the probability of obtaining no mutations in a given clone size
def prob_pcr_no_error(ampl_clone_size, read_len, pol_error):
    if ampl_clone_size <= 1:
        return 1.0
    else:
        p_no_err_read = (1 - pol_error) ** ((ampl_clone_size - 1) * (read_len * 2))
        return p_no_err_read

#
# Generate distribution of per clone probabilities of no error
#   Structure:  [ error_prob0, error_prob1, ... ]
def per_clone_no_error_prob_log_dist(read_len, log_ampl_clone_size_distrib, base, pol_error=4.4e-7):
    # pol_error default is the fidelity of Phusion HF Pol (per bp, per CPR cycle)
    per_clone_no_error = [ None for log_a in range(len(log_ampl_clone_size_distrib)) ]
    for log_a in range(len(log_ampl_clone_size_distrib)):
        a = get_clone_class_representative_value(log_a, base)
        if a is None:
            continue
        per_clone_no_error[log_a] = prob_pcr_no_error(a, read_len, pol_error)
    # Return list of error probabilities for the corresponding clone sizes classes
    return per_clone_no_error

#
# Per clone size, generate a distribution of the frequency of nodes with mutation
#   Structure: [ [ p0, p1, p2 ]
#                [ p0, p1, p2, p3 ],
#                ...,
#                [ p0, p1, p2, ..., pn ] ]
# First dimension of the list is the clone size classes, starting at class size 2 (0 & 1 have no error)
# Second dimension is distribution of errors in that clone
def generate_mut_node_log_distrib(log_ampl_clone_size_distrib, base, max_iter):
    # Empty list to hold the error distributions for all clone size classes
    mut_node_dist = [ None for log_a in range(len(log_ampl_clone_size_distrib)) ]
    # Iterate over the size classes
    for log_a in range(len(log_ampl_clone_size_distrib)):
        a = get_clone_class_representative_value(log_a, base)
        if a is None:
            continue
        if a < 2:
            continue
        # Iterate and keep tally of the mutated nodes generated
        clone_error_dist = [ 0 for n_mut in range(a + 1) ]
        for _ in range(max_iter):
            n_mut = mutated_node_freq(a)
            clone_error_dist[n_mut] += 1
        # Convert tally to frequency list
        mut_freq = [ clone_error_dist[n_mut]/max_iter for n_mut in range(a + 1) ]
        # Store in mut_node_dist list
        mut_node_dist[log_a] = mut_freq
    return mut_node_dist

#
# New distribution containing the adjusted mutated molecule distribution
# Merges `per_clone_no_error_prob_dist` and `generate_mut_node_distrib`
#   Structure: [ [ p0 ],
#                [ p0, p1 ], ...,
#                [ p0, p1, p2, ..., pn ] ]
# First dimension of the list is the clone size classes,
# Second dimension is distribution of errors in that clone
def adjust_dist_of_ampl_errors(log_ampl_clone_size_distrib, read_len,
        base, max_iter=100, pol_error=4.4e-7):
    # Generate two base distributions
    clone_no_error_prob = per_clone_no_error_prob_log_dist(read_len, log_ampl_clone_size_distrib, base, pol_error)
    mut_node_dist = generate_mut_node_log_distrib(log_ampl_clone_size_distrib, base, max_iter)
    assert len(clone_no_error_prob) == len(mut_node_dist)
    adj_error_dist = [ None for log_a in range(len(clone_no_error_prob)) ]
    for log_a, prob_no_mut in enumerate(clone_no_error_prob):
        if prob_no_mut is None:
            continue
        if log_a == 0:
            # a==1; no mutations.
            adj_error_dist[0] = [1.0, 0.0]
            continue
        assert mut_node_dist[log_a][0] == 0.0
        assert 1.0-1e-9 < sum(mut_node_dist[log_a]) < 1.0+1e-9
        adj_error_dist[log_a] = [ p_n_mut * (1 - prob_no_mut) for p_n_mut in mut_node_dist[log_a] ]
        adj_error_dist[log_a][0] = prob_no_mut
    return adj_error_dist

def get_amplification_factor(ampl_clone_size_distrib, base):
    mean_ampl_factor = 0.0
    for log_a, prob in enumerate(ampl_clone_size_distrib):
        a = get_clone_class_representative_value(log_a, base)
        if a is None:
            assert prob == 0.0 or prob is None
            continue
        mean_ampl_factor += a * prob
    return mean_ampl_factor

#
# Generate a single distribution containing both PCR error and duplicates by
# applying the following formula:
# p(S=s^ES=r) = sum_a{ p(A=a) p(S=s|A=a) sum_e{ p(EA=e|A=a) p(ES=r|S=s^A=a^EA=e) }}
def generate_pcr_dups_error_log_distrib(
        log_ampl_clone_size_distrib,
        reads_to_templates_ratio,
        base,
        single_adj_error_distrib=None):
    max_s = 1000    # Max size of sequenced clones
    p_lim = 1e-6    # Truncate distribution for values smaller than this
    seq_pcr_error_distrib = []
    #   Structure: [ [ p0 ],
    #                [ p0, p1 ], ...,
    #                [ p0, p1, p2, ..., pn ] ]
    # Half matrix containing probabilities of clone sizes and error
    # First dimension clone sizes
    # Second dimension errors in that clone size

    ampl_fac = get_amplification_factor(log_ampl_clone_size_distrib, base)
    reads_to_ampl_mols_ratio = reads_to_templates_ratio / ampl_fac

    # Define the amplifed clone size classes
    a_classes = range(len(log_ampl_clone_size_distrib))
    # precompute the p(S=s|A=a)
    p_s_a = [None for log_a in a_classes]
    for log_a in a_classes:
        a = get_clone_class_representative_value(log_a, base)
        if a is None:
            continue
        p_s_a[log_a] = poisson.pmf(range(max_s), (reads_to_ampl_mols_ratio * a))
    p_s0 = None
    for s in range(max_s):
        seq_pcr_error_distrib.append([ None for r in range(s+1) ])
        # precompute the p(ES=r|S=s^A=a^EA=e)
        if single_adj_error_distrib is not None:
            p_r_sae = []
            for log_a in a_classes:
                p_r_sae.append(None)
                a = get_clone_class_representative_value(log_a, base)
                if a is None:
                    continue
                p_r_sae[-1] = [ binom.pmf(range(s+1), s, e/a) for e in range(a+1) ]
        for r in range(s+1):
            p_sr = 0.0
            for log_a in a_classes:
                a = get_clone_class_representative_value(log_a, base)
                if a is None:
                    continue
                if single_adj_error_distrib is None:
                    sum_e = 1.0 if r == 0 else 0.0
                else:
                    sum_e = 0.0
                    for e in range(a):
                        # sum_e{ p(EA=e|A=a) p(ES=r|S=s^A=a^EA=e)
                        p_e_a = single_adj_error_distrib[log_a][e]
                        sum_e += p_e_a * p_r_sae[log_a][e][r]
                # sum_a{ p(A=a) p(S=s|A=a) sum_e{ p(EA=e|A=a) p(ES=r|S=s^A=a^EA=e) }} for a given `a`
                p_sr += log_ampl_clone_size_distrib[log_a] * p_s_a[log_a][s] * sum_e
            if s == 0 :
                assert r == 0
                p_s0 = p_sr
                seq_pcr_error_distrib[0][0] = 0.0
            else:
                seq_pcr_error_distrib[s][r] = p_sr / (1 - p_s0)
        if s > 0 and sum(seq_pcr_error_distrib[s]) < p_lim:
            # break when values are getting too small
            break
    assert len(seq_pcr_error_distrib) > 1
    # Return double matrix
    return seq_pcr_error_distrib

#
# Convert the sequenced clone/error matrix into two lists (one of values and one of probabilities)
# Values are (x, y), where x is a sequenced clone size, y is number of molecules with error in that sequenced clone
def get_seq_pcr_error_lists(seq_pcr_error_distrib):
    seq_clone_errors_freq = []
    seq_clone_errors_vals = []
    for s, probs in enumerate(seq_pcr_error_distrib):
        for r, p in enumerate(probs):
            seq_clone_errors_freq.append(p)
            seq_clone_errors_vals.append((s, r))
    # Adjust values so sum of probabilities equals 1
    #   This is product of truncating the distribution for really small values
    sum_p = np.sum(seq_clone_errors_freq)
    if sum_p < 1:
        seq_clone_errors_freq = [ seq_clone_errors_freq[i]/sum_p for i in range(len(seq_clone_errors_freq)) ]
    # Return lists of clone values and adjusted frecuency
    return seq_clone_errors_freq, seq_clone_errors_vals

#
# Convert distribution of clone sizes AND errors into clone sizes only
def get_duplicate_only_distrib(seq_clone_errors_freq, seq_clone_errors_vals):
    dup_distrib = {}
    # Iterate over the clone+error distribution and sum all frequencies for a given clone size
    for i in range(len(seq_clone_errors_freq)):
        clone_size = seq_clone_errors_vals[i][0]
        dup_distrib.setdefault(clone_size, 0)
        dup_distrib[clone_size] += seq_clone_errors_freq[i]
    dup_distrib = [ dup_distrib[clone_size] for clone_size in sorted(dup_distrib) ]
    # Return a list containing the per-sequenced clone size frequencies
    return dup_distrib

#
# From the distribution of sequenced clones, calculate the percentage of PCR duplicates
def calculate_perc_duplicates(dup_distrib):
    # duplicates = to 1 - (1 / sum_reads)
    # sum_reads = 1*p(S=1) + 2*p(S=2) + 3*p(S=3) + ...
    # 1 - sum_reads is the portion of reads that are kept
    sum_reads = 0.0
    for clone_size, prob in enumerate(dup_distrib):
        if clone_size == 0:
            continue
        # Do n*p(S=n), where n is the clone size
        sum_reads += (clone_size * prob)
    # Return 1 - kept_reads
    return 1 - (1 / sum_reads)

#
# Sample from the merged sequencing clone size/error distribution and
# determine the properties of the sequenced clone
def determine_seq_clone_size_error(seq_clone_errors_freq, seq_clone_errors_vals):
    value_index = list(range(len(seq_clone_errors_vals)))
    seq_clone_index = np.random.choice(value_index, p=seq_clone_errors_freq)
    # First value is size of the clone
    clone_size = seq_clone_errors_vals[seq_clone_index][0]
    # Second value is number of mutated molecules in clone
    clone_error = seq_clone_errors_vals[seq_clone_index][1]
    return clone_size, clone_error

#
# Check the input parameters for the Decoratio PCR model
#
def check_input_pcrmodel_parameters(pcr_main_model=None, pcr_cycles=None,
                                    log_normal_sd=None,  log_normal_skew=None, 
                                    inheff_mean=None,    inheff_sd=None):
    '''
    Checks the input parameters for the PCR amplification to guarantee it is a valid decoratio amplification model

    Args:
        pcr_main_model : (str) Main decoratio amplification model, among lognormal, logskewnormal, inheff, inheffbeta
        pcr_cycles : (int) Number of PCR cycles
        log_normal_sd : (float) Stdev for lognormal and logknewnormal models
        log_normal_skew : (int, float) Skew value for logskewnormal model
        inheff_mean : (float) Mean amplification for inheff and inheffbeta
        inheff_sd : (float) Stdev amplification for inheff and inheffbeta

    Returns:
        model : (str) decoratio amplification model string or None
    '''
    model = None
    # Check the main model string
    if pcr_main_model is not None:
        pcr_main_model = pcr_main_model.lower()
        assert pcr_main_model in {'lognormal', 'logskewnormal', 'inheff', 'inheffbeta'}, f"Error: {pcr_main_model} is an invalid PCR model. Allowed models are: lognormal, logskewnormal, inheff, inheffbeta."
        model_str = pcr_main_model
        # Check parameters for the lognormal and logskewnormal
        if pcr_main_model in {'lognormal', 'logskewnormal'}:
            # Add the lognormal standard dev
            if log_normal_sd is not None:
                assert type(log_normal_sd) is float, f"Error: {log_normal_sd} is invalid lognormal stdev. Must be a float."
                assert log_normal_sd > 0.0, f"Error: {log_normal_sd} is invalid lognormal stdev. Must be > 0.0."
                model_str += f':{log_normal_sd}'
            # Add the skew
            if pcr_main_model == 'logskewnormal':
                if log_normal_skew is not None:
                    assert type(log_normal_skew) in {int, float}, f"Error: {log_normal_skew} is invalid lognormal skew. Value must be an int or float."
                    assert log_normal_sd is not None, f"Error: If providing a lognormal skew, lognormal stdev must also be specified."
                    model_str += f':{log_normal_skew}'
        # Check parameters for the inheff models
        elif pcr_main_model in {'inheff', 'inheffbeta'}:
            # Check PCR cycles
            if pcr_cycles is not None:
                assert type(pcr_cycles) is int, f"Error: {pcr_cycles} is invalid PCR cycle number. Value must be an integer."
                assert 1 <= pcr_cycles <= 50, f"Error: {pcr_cycles} is invalid number of PCR cycles. Value must be between 1-50."
                model_str += f':{pcr_cycles}'
            else:
                sys.exit("Error: If using inheff and inheffbeta models, PCR cycles must not be None")
            # Add the inheff mean
            if inheff_mean is not None:
                assert inheff_sd is not None, 'Error: If providing InhEff mean, InEff stdev must also be specified.'
                assert type(inheff_mean) is float, f"Error: {inheff_mean} is invalid InhEff mean. Value must be a float."
                assert 0.0 < inheff_mean < 1.0, f"Error: {inheff_mean} is invalid InhEff mean. Value must be greater than 0, smaller than 1."
                model_str += f':{inheff_mean}'
            # Add the inheff stdev
            if inheff_sd is not None:
                assert inheff_mean is not None, 'Error: If providing InhEff stdev, InEff mean must also be specified.'
                assert type(inheff_sd) is float, f"Error: {inheff_sd} is invalid InhEff stdev. Value must be a float."
                assert 0.0 < inheff_sd < 1.0, f"Error: {inheff_sd} is invalid InhEff stdev. Value must be greater than 0, smaller than 1."
                model_str += f':{inheff_sd}'
        model = model_str
    return model

#
# PCR duplicates class
class PCRDups:
    def __init__(self,
                 pcr_main_model=None,
                 pcr_cycles=None,
                 log_normal_sd=None,
                 log_normal_skew=None,
                 inheff_mean=None,
                 inheff_sd=None,
                 deco_ratio=0.1, # Depth-Complexity ratio, 1:10 reads to template (aka, good ratio)
                 base=(2**0.1),
                 max_iter=100,
                 pol_error=4.4e-7,
                 library_opts=LibraryOptions()):
        # Check classes
        assert isinstance(library_opts, LibraryOptions)
        # Check the DeCo Ratio
        assert type(deco_ratio) is float
        assert 1e-4 <= deco_ratio <= 1e4, f"Error: {deco_ratio} is an invalid Depth/Complexity ratio. Value must be between 1e-4 to 1e4 (for stability reasons)."
        # Check other paramters
        assert type(base) is float
        assert type(pol_error) is float
        assert 0 <= pol_error < 1, f"Error: {pol_error} is invalid value for PCR error rate. Must be: 0 <= value < 1."
        assert type(max_iter) is int
        assert 0 < max_iter <= 1e6
        # Check PCR model (will be checked again by decoratio)
        self.ampl_model = check_input_pcrmodel_parameters(pcr_main_model, pcr_cycles, log_normal_sd, log_normal_skew, inheff_mean, inheff_sd)
        self.pcr_cyc    = pcr_cycles
        self.ratio      = deco_ratio
        self.base       = base
        self.max_it     = max_iter
        self.pol_er     = pol_error
        # If no PCR cycles, return empty PCR clone distribution, otherwise generate distribution
        self.seq_clone_errors_freq = None
        self.seq_clone_errors_vals = None
        if self.ampl_model is None:
            # If PCR model is None, only the (1, 0) clone is possible
            self.seq_clone_errors_vals = [(0, 0), (1, 0)]
            self.seq_clone_errors_freq = [ 0.00,   1.00 ]
        else:
            # Amplified PCR duplicate distribution:
            # Added for version 1.2.0 using the decoration amplification models
            try:
                ampl_model = decoratio.AmplModel.factory(self.ampl_model)
            except ValueError:
                sys.exit(f'ERROR: failed to parse model \'{ampl_model}\'')
            log_ampl_clone_size_distrib = ampl_model.get_ampl_cz_d(self.base)
            # Adjusted amplified PCR error distribution
            single_adj_error_distrib = adjust_dist_of_ampl_errors(log_ampl_clone_size_distrib, library_opts.rlen, self.base, self.max_it, self.pol_er)
            # Generate a single distribution that convined probabilities of duplicates and error for PCR clones
            seq_pcr_error_distrib = generate_pcr_dups_error_log_distrib(
                log_ampl_clone_size_distrib,
                self.ratio,
                self.base,
                single_adj_error_distrib)
            # Convert the matrix into two lists (one of values and one of probabilities)
            self.seq_clone_errors_freq, self.seq_clone_errors_vals = get_seq_pcr_error_lists(seq_pcr_error_distrib)
        # Convert into single list of clone sizes and calculate PCR duplicates
        dup_distrib = get_duplicate_only_distrib(self.seq_clone_errors_freq, self.seq_clone_errors_vals)
        self.perc_duplicates = calculate_perc_duplicates(dup_distrib)
    # Function to print PCR sequenced clone distribution
    def print_seq_clone_dist(self, out_dir):
        clone_dist = open('{}/sequenced_clone_distrib.tsv'.format(out_dir), 'w')
        clone_dist.write('clone_size\tn_errors\tclone_prob\n')
        for i in range(len(self.seq_clone_errors_vals)):
            clone_dist.write('{}\t{}\t{:.6g}\n'.format(self.seq_clone_errors_vals[i][0],
                self.seq_clone_errors_vals[i][1],
                self.seq_clone_errors_freq[i]))
    # Sample from the merged sequencing clone size/error distribution and
    # determine the properties of the sequenced clone
    def determine_seq_clone_size_error(self):
        value_index = list(range(len(self.seq_clone_errors_vals)))
        seq_clone_index = np.random.choice(value_index, p=self.seq_clone_errors_freq)
        # First value is size of the clone
        clone_size = self.seq_clone_errors_vals[seq_clone_index][0]
        # Second value is number of mutated molecules in clone
        clone_error = self.seq_clone_errors_vals[seq_clone_index][1]
        return clone_size, clone_error
    # Print class properties
    def __str__(self):
        if self.ampl_model is None:
            return f'''PCR model options:
    PCR amplification model: {self.ampl_model} (No PCR)
    PCR cycles:              {self.pcr_cyc}
    PCR duplicate rate:      {self.perc_duplicates:.2%}'''
        else:
            return f'''PCR model options:
    PCR amplification model: {self.ampl_model}
    PCR cycles:              {self.pcr_cyc}
    depth/complexity ratio:  {(self.ratio):0.6g}
    PCR duplicates rate:     {self.perc_duplicates:.3%}'''

#
# Extract reads from a sample
def sequence_sample(sample_n, out_dir, alleles_list, library_opts=LibraryOptions(), mutation_opts=MutationModel(), pcr_opts=PCRDups(), def_score=37, phred_offet=33):
    # Check classes
    assert isinstance(library_opts, LibraryOptions)
    assert isinstance(mutation_opts, MutationModel)
    assert isinstance(pcr_opts, PCRDups)
    # Determine the number of reads to generate
    n_sequenced_reads = target_reads(len(alleles_list), library_opts.cov)
    # Loop over target reads and sequence each iteration
    remaining_reads = n_sequenced_reads
    clone_i = 0
    # Process as FASTA
    if library_opts.out_fmt == 'fasta':
        # Open output files
        reads1_fa = gzip.open(f'{out_dir}/{sample_n}.1.fa.gz', 'wt')
        reads2_fa = gzip.open(f'{out_dir}/{sample_n}.2.fa.gz', 'wt')
        while remaining_reads > 0:
            # Sample random template to start a clone
            allele, insert_len = sample_a_template(alleles_list, library_opts)
            base_name = build_base_template_name(allele, insert_len, clone_i, library_opts)
            # Determine size of clone and number of reads with mutations
            clone_size, n_mut_reads = pcr_opts.determine_seq_clone_size_error()
            # iterate over clone size and process sequence into reads
            duplicate_i = 0
            # write sequences without error
            for i in range(clone_size - n_mut_reads):
                fw_read, rv_read = sequence_read_pair(allele, insert_len, library_opts)
                reads1_fa.write(f'>{base_name}:{duplicate_i+1}/1\n{fw_read}\n')
                reads2_fa.write(f'>{base_name}:{duplicate_i+1}/2\n{rv_read}\n')
                duplicate_i += 1
            # write sequences with PCR error
            if n_mut_reads > 0:
                mut_allele = (allele[0], introduce_pcr_mutation(allele[1], insert_len, library_opts, mutation_opts))
                for i in range(n_mut_reads):
                    fw_read, rv_read = sequence_read_pair(mut_allele, insert_len, library_opts)
                    reads1_fa.write(f'>{base_name}:{duplicate_i+1}/1\n{fw_read}\n')
                    reads2_fa.write(f'>{base_name}:{duplicate_i+1}/2\n{rv_read}\n')
                    duplicate_i += 1
            # Increate count of used clones
            clone_i += 1
            # Consume remaining reads
            remaining_reads -= clone_size
        reads1_fa.close()
        reads2_fa.close()
    elif library_opts.out_fmt == 'fastq':
        # Open output files
        reads1_fq = gzip.open(f'{out_dir}/{sample_n}.1.fq.gz', 'wt')
        reads2_fq = gzip.open(f'{out_dir}/{sample_n}.2.fq.gz', 'wt')
        # Determine fixed PHRED scores (same for all reads) based on a representative read pair
        score = chr(def_score+phred_offet)
        allele, insert_len = sample_a_template(alleles_list, library_opts)
        fw_read, rv_read = sequence_read_pair(allele, insert_len, library_opts)
        fw_phred = ''.join([ score for _ in range(len(fw_read))])
        rv_phred = ''.join([ score for _ in range(len(rv_read))])
        while remaining_reads > 0:
            # Sample random template to start a clone
            allele, insert_len = sample_a_template(alleles_list, library_opts)
            base_name = build_base_template_name(allele, insert_len, clone_i, library_opts)
            # Determine size of clone and number of reads with mutations
            clone_size, n_mut_reads = pcr_opts.determine_seq_clone_size_error()
            # iterate over clone size and process sequence into reads
            duplicate_i = 0
            # write sequences without error
            for i in range(clone_size - n_mut_reads):
                fw_read, rv_read = sequence_read_pair(allele, insert_len, library_opts)
                reads1_fq.write(f'@{base_name}:{duplicate_i+1}/1\n{fw_read}\n+\n{fw_phred}\n')
                reads2_fq.write(f'@{base_name}:{duplicate_i+1}/2\n{rv_read}\n+\n{rv_phred}\n')
                duplicate_i += 1
            # write sequences with PCR error
            if n_mut_reads > 0:
                mut_allele = (allele[0], introduce_pcr_mutation(allele[1], insert_len, library_opts, mutation_opts))
                for i in range(n_mut_reads):
                    fw_read, rv_read = sequence_read_pair(mut_allele, insert_len, library_opts)
                    reads1_fq.write(f'@{base_name}:{duplicate_i+1}/1\n{fw_read}\n+\n{fw_phred}\n')
                    reads2_fq.write(f'@{base_name}:{duplicate_i+1}/2\n{rv_read}\n+\n{rv_phred}\n')
                    duplicate_i += 1
            # Increate count of used clones
            clone_i += 1
            # Consume remaining reads
            remaining_reads -= clone_size
        reads1_fq.close()
        reads2_fq.close()


# Sequence library
# TODO: Update logs.
def sequence_library(out_dir, popmap_file, alleles_dir, library_opts=LibraryOptions(), mutation_opts=MutationModel(), pcr_opts=PCRDups()):
    # Check variables and classes
    assert isinstance(library_opts, LibraryOptions)
    assert isinstance(mutation_opts, MutationModel)
    assert isinstance(pcr_opts, PCRDups)
    # Check output directory
    out_dir = out_dir.rstrip('/')
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    elif not os.path.isdir(out_dir):
        sys.exit('oops')
    # Check alleles directory
    alleles_dir = alleles_dir.rstrip('/')
    if not os.path.isdir(alleles_dir):
        sys.exit('oops')
    # generate a sample list from popmap
    samples = []
    for sample in open(popmap_file, 'r'):
        samples.append(sample.strip('\n').split('\t')[0])
    # Iterate over samples
    for sample in samples:
        # Extract sample alleles
        alleles_list = load_sample_alleles(sample, alleles_dir, library_opts)
        # Sequence sample
        sequence_sample(sample, out_dir, alleles_list, library_opts, mutation_opts, pcr_opts)
    # TODO parallelize

#
# MAIN WRAPPER OPTIONS
# They run all or several parts of the pipeline.
# Are called by `__main__` and `radinitio` wrapper
#

# Main simulation wrapper - default in `__main__`
def simulate(
        out_dir,
        genome_fa,
        chromosomes,
        chrom_recomb_rates,
        msprime_simulate_args,
        library_opts = LibraryOptions(),
        mutation_opts = MutationModel(),
        pcr_opts = PCRDups(),
        min_seq_len = 0):

    # Check variables and classes
    assert type(msprime_simulate_args) == dict
    assert isinstance(library_opts, LibraryOptions)
    assert isinstance(mutation_opts, MutationModel)
    assert isinstance(pcr_opts, PCRDups)

    # Create the output directory.
    assert os.path.exists(genome_fa)
    assert os.path.exists(out_dir)
    msprime_vcf_dir = '{}/msprime_vcfs'.format(out_dir)
    master_vcf_dir  = '{}/ref_loci_vars'.format(out_dir)
    rad_alleles_dir = '{}/rad_alleles'.format(out_dir)
    rad_reads_dir   = '{}/rad_reads'.format(out_dir)
    for d in [msprime_vcf_dir, master_vcf_dir, rad_alleles_dir, rad_reads_dir]:
        os.mkdir(d)

    if chromosomes is None:
        print('Target sequences not specified. Simulating over all sequences in the reference genome.', flush=True)
        if min_seq_len > 0:
            print(f'    Keeping sequences larger than {min_seq_len:,} bp.', flush=True)
    else:
        print(f'Simulating for {len(chromosomes):,} target sequences.', flush=True)
        check_brackets_in_chr_ids(chromosomes)
    print_msp_params(msprime_simulate_args, sys.stdout)
    print(f'\n{mutation_opts}', flush=True)
    print(f'\n{library_opts}', flush=True)
    print(f'\n{pcr_opts}', flush=True)

    # Load the genome.
    genome_dict = load_genome(genome_fa, chromosomes, min_seq_len)
    if not len(genome_dict) > 0:
        print('No chromosomes/scaffolds loaded.')
        return

    # Assign the chromosome recombination rates.
    assert type(chrom_recomb_rates) in [dict, float]
    for c in genome_dict:
        if type(chrom_recomb_rates) == dict:
            assert c in chrom_recomb_rates
            genome_dict[c].rec = chrom_recomb_rates[c]
        else:
            genome_dict[c].rec = chrom_recomb_rates

    # Run msprime
    print('\nSimulating chromosomes with msprime...', flush=True)
    sim_all_chromosomes(msprime_simulate_args, genome_dict, msprime_vcf_dir)
    # Write the population map.
    print('\nWriting the popmap.tsv...', flush=True)
    popmap_file = '{}/popmap.tsv'.format(out_dir)
    write_popmap(popmap_file, msprime_simulate_args['population_configurations'])
    # Merge and process variants.
    print('\nMerging msprime VCFs and generating variants...', flush=True)
    merge_vcf(genome_dict, msprime_vcf_dir, master_vcf_dir, mutation_opts)

    # Extract reference RAD loci and generate loci dictionary.
    ref_loci_dict = extract_reference_rad_loci(genome_dict, master_vcf_dir, library_opts)
    if not len(ref_loci_dict) > 0:
        print('No RAD loci retained.')
        return

    # Filter RAD variants
    # 1. Generate loci position set for filtering
    loci_pos_set = create_rad_pos_set_dict(ref_loci_dict)
    # 2. Filter
    print('\nFiltering RAD variants...', flush=True)
    rad_variants = filter_rad_variants(ref_loci_dict, loci_pos_set, master_vcf_dir)
    # Extract RAD alleles
    print('\nExtracting RAD alleles...', flush=True)
    # Create log for dropped alleles
    allele_log = gzip.open('{}/dropped_alleles.tsv.gz'.format(rad_alleles_dir), 'wt')
    extract_rad_alleles(ref_loci_dict, rad_variants, popmap_file, rad_alleles_dir, library_opts, log_f=allele_log)
    # Print the distribution of PCR clone sizes.
    pcr_opts.print_seq_clone_dist(out_dir)
    # Sequence samples
    print('\nSequencing library...', flush=True)
    sequence_library(rad_reads_dir, popmap_file, rad_alleles_dir, library_opts, mutation_opts, pcr_opts)


# Function to run RADinito variant generation and processing
# Starts with reference genome, msprime model params, and mutation options
# Produces msprime VCF, popmap, and processed genomic VCF
def make_population(
        out_dir,
        genome_fa,
        chromosomes,
        chrom_recomb_rates,
        msprime_simulate_args,
        mutation_opts = MutationModel(),
        min_seq_len = 0):

    # Check variables and classes
    assert type(msprime_simulate_args) == dict
    assert isinstance(mutation_opts, MutationModel)

    # Create the output directory.
    assert os.path.exists(genome_fa)
    assert os.path.exists(out_dir)
    out_dir = out_dir.rstrip('/')
    msprime_vcf_dir = f'{out_dir}/msprime_vcfs'
    master_vcf_dir  = f'{out_dir}/ref_loci_vars'
    for d in [msprime_vcf_dir, master_vcf_dir]:
        os.mkdir(d)


    if chromosomes is None:
        print('Target sequences not specified. Simulating over all sequences in the reference genome.', flush=True)
        if min_seq_len > 0:
            print(f'    Keeping sequences larger than {min_seq_len:,} bp.', flush=True)
    else:
        print(f'Simulating for {len(chromosomes):,} target sequences.', flush=True)
        check_brackets_in_chr_ids(chromosomes)
    print_msp_params(msprime_simulate_args, sys.stdout)
    print('\n{}'.format(mutation_opts), flush=True)

    # Load and check the genome
    genome_dict = load_genome(genome_fa, chromosomes, min_seq_len)
    if len(genome_dict) < 1:
        print('No chromosomes/scaffolds loaded.', flush=True)
        return

    # Assign the chromosome recombination rates.
    assert type(chrom_recomb_rates) in [dict, float]
    for c in genome_dict:
        if type(chrom_recomb_rates) == dict:
            assert c in chrom_recomb_rates
            genome_dict[c].rec = chrom_recomb_rates[c]
        else:
            genome_dict[c].rec = chrom_recomb_rates

    # Run msprime
    print('\nSimulating chromosomes with msprime...', flush=True)
    sim_all_chromosomes(msprime_simulate_args, genome_dict, msprime_vcf_dir)
    # Write the population map.
    print('\nWriting the popmap.tsv...', flush=True)
    popmap_file = f'{out_dir}/popmap.tsv'
    write_popmap(popmap_file, msprime_simulate_args['population_configurations'])
    # Merge and process variants.
    print('\nMerging msprime VCFs and generating variants...', flush=True)
    merge_vcf(genome_dict, msprime_vcf_dir, master_vcf_dir, mutation_opts)


# Provide a breakdown of the number of RAD loci in the genome following library parameters
# Starts with a reference genome and library parameters
# Returns reference loci fasta and loci status breakdown
def tally_rad_loci(
        out_dir,
        genome_fa,
        chromosomes = None,
        library_opts = LibraryOptions(),
        min_seq_len = 0):

    # Check variables and classes
    assert isinstance(library_opts, LibraryOptions)

    # Create the output directory.
    assert os.path.exists(genome_fa)
    assert os.path.exists(out_dir)
    reference_dir  = f'{out_dir}/ref_loci_vars'
    if not os.path.exists(reference_dir):
        os.mkdir(reference_dir)

    # Open the log and report parameters.
    sys.stdout = open(f'{out_dir}/radinitio.log', "w")
    print(f'RADinitio version {__version__}', flush=True)
    print(f'radinitio.tally_rad_loci started on {now()}.\n', flush=True)
    print_dependencies()
    if chromosomes is None:
        print('Target sequences not specified. Simulating over all sequences in the reference genome.', flush=True)
        if min_seq_len > 0:
            print(f'    Keeping sequences larger than {min_seq_len:,} bp.', flush=True)
    else:
        print(f'Simulating for {len(chromosomes):,} target sequences.', flush=True)
        check_brackets_in_chr_ids(chromosomes)
    print(f'\n{library_opts}', flush=True)

    # Load and check the genome
    genome_dict = load_genome(genome_fa, chromosomes, min_seq_len)
    if len(genome_dict) > 0:
        # Extract reference RAD loci and generate loci dictionary.
        ref_loci_dict = extract_reference_rad_loci(genome_dict, reference_dir, library_opts)
    else:
        print('No chromosomes/scaffolds loaded.', flush=True)
    return

#
# Simulate library generation and sequencing
# Starts with the genome-wide VCF from msprime/merge_vcf and/or `make_population()`
# Returns reference loci, allele fasta, reads fasta
def make_library_seq(
        out_dir,
        genome_fa,
        chromosomes,
        make_pop_sim_dir,
        library_opts = LibraryOptions(),
        mutation_opts = MutationModel(),
        pcr_opts = PCRDups(),
        min_seq_len = 0):

    # Check variables and classes
    assert isinstance(library_opts, LibraryOptions)
    assert isinstance(mutation_opts, MutationModel)
    assert isinstance(pcr_opts, PCRDups)
    make_pop_sim_dir = make_pop_sim_dir.rstrip('/')
    assert out_dir != make_pop_sim_dir

    # Check needed input/outputs
    assert os.path.exists(genome_fa)
    assert os.path.exists(out_dir)
    #   Check the `make_population` directory
    assert os.path.exists(make_pop_sim_dir)
    #   Check the genome-wide VCF
    genome_vcf_dir = f'{make_pop_sim_dir}/ref_loci_vars'
    assert os.path.exists(f'{genome_vcf_dir}/ri_master.vcf.gz')
    #   Check popmap
    popmap_file = f'{make_pop_sim_dir}/popmap.tsv'
    assert os.path.exists(popmap_file)

    # Create the output directory.
    ref_loci_dir = f'{out_dir}/ref_loci_vars'
    rad_alleles_dir = f'{out_dir}/rad_alleles'
    rad_reads_dir   = f'{out_dir}/rad_reads'
    for d in [ref_loci_dir, rad_alleles_dir, rad_reads_dir]:
        os.mkdir(d)

    if chromosomes is None:
        print('Target sequences not specified. Simulating over all sequences in the reference genome.', flush=True)
        if min_seq_len > 0:
            print(f'    Keeping sequences larger than {min_seq_len:,} bp.', flush=True)
    else:
        print(f'Simulating for {len(chromosomes):,} target sequences.', flush=True)
        check_brackets_in_chr_ids(chromosomes)
    print(f'\n{library_opts}', flush=True)
    print(f'\n{pcr_opts}', flush=True)

    # Load and check the genome
    genome_dict = load_genome(genome_fa, chromosomes, min_seq_len)
    if len(genome_dict) < 1:
        print('No chromosomes/scaffolds loaded.', flush=True)
        return

    # Extract reference RAD loci and generate loci dictionary.
    ref_loci_dict = extract_reference_rad_loci(genome_dict, ref_loci_dir, library_opts)
    if not len(ref_loci_dict) > 0:
        print('No RAD loci retained.')
        return

    # Filter RAD variants
    # 1. Generate loci position set for filtering
    loci_pos_set = create_rad_pos_set_dict(ref_loci_dict)
    # 2. Filter
    print('\nFiltering RAD variants...', flush=True)
    rad_variants = filter_rad_variants(ref_loci_dict, loci_pos_set, genome_vcf_dir)
    # Extract RAD alleles
    print('\nExtracting RAD alleles...', flush=True)
    # Create log for dropped alleles
    allele_log = gzip.open('{}/dropped_alleles.tsv.gz'.format(rad_alleles_dir), 'wt')
    extract_rad_alleles(ref_loci_dict, rad_variants, popmap_file, rad_alleles_dir, library_opts, log_f=allele_log)
    # Print the distribution of PCR clone sizes.
    pcr_opts.print_seq_clone_dist(out_dir)
    # Sequence samples
    print('\nSequencing library...', flush=True)
    sequence_library(rad_reads_dir, popmap_file, rad_alleles_dir, library_opts, mutation_opts, pcr_opts)





#
# Other utility functions
#

# Function to fix bases in reference genome
def fix_genome_bases(genome_dict, output_fa_path, line_width=60):
    # Check input classes
    assert type(genome_dict) == dict
    assert not os.path.exists(output_fa_path)
    # Set output genome fasta path
    if output_fa_path.endswith('.gz'):
        output_fa_path = output_fa_path.strip('.gz')
    out_fa = gzip.open(f'{output_fa_path}.gz', 'wt')
    # Allowed nucleotides
    allowed_nucleotides = {'A', 'C', 'G', 'T', 'N'}
    # Define dictionary of ambiguous nucleotides
    ambiguous_nucleotides = {
        'B' : ['C', 'G', 'T'],
        'D' : ['A', 'G', 'T'],
        'H' : ['A', 'C', 'T'],
        'K' : ['G', 'T'],
        'M' : ['A', 'C'],
        'R' : ['A', 'G'],
        'S' : ['G', 'C'],
        'U' : ['T'],
        'V' : ['A', 'C', 'G'],
        'W' : ['A', 'T'],
        'Y' : ['C', 'T'] }
    # Loop through genome dictionary
    for chrom in sorted(genome_dict):
        chromosome = genome_dict[chrom]
        # assert isinstance(chromosome, Chromosome)
        assert isinstance(chromosome, Chromosome)
        sequence_list = list(chromosome.seq)
        for i, nuc in enumerate(sequence_list):
            # Check the nucleotide
            if nuc in allowed_nucleotides:
                continue
            # If an ambiguous nucleotide
            elif nuc in ambiguous_nucleotides:
                sequence_list[i] = random.choice(ambiguous_nucleotides[nuc])
            # If any other thing
            else:
                sequence_list[i] = 'N'
        # Write output
        out_fa.write(f'>{chromosome.id}\n')
        # Wrap the sequence lines up to `line_width` characters
        seq_str = ''.join(sequence_list)
        start = None
        for start in range(0, len(seq_str), line_width):
            seq_line = seq_str[start:(start+line_width)]
            out_fa.write(f'{seq_line}\n')


#
# Function to calculate allele dropout at a read level
#
# Class to store the per-read information
class ri_read:
    def __init__(self, locus_id, sample_id, allele_i, clone_id):
        self.name   = locus_id
        self.loc    = 't{}{}'.format(int(locus_id[1:-1]), locus_id[-1])
        self.sam    = sample_id
        self.allele = int(allele_i) - 1
        self.clone  = int(clone_id)
    def __str__(self):
        return('{}\t{}\t{}\t{}'.format(self.loc, self.sam, self.allele, self.clone))

# Read fasta and extract values for a single sample
def extract_sample_reads(sample, reads_dir):
    # Output: sample read list
    sample_reads = list()
    # Open fasta
    sample_fa = '{}/{}.1.fa.gz'.format(reads_dir, sample)
    for line in gzip.open(sample_fa, 'rt'):
        if line[0] != '>':
            # Only process fasta headers
            continue
        # Remove unwanted characters from header (newline, `>`, read-pair id, etc)
        # >t098n:msp_0:a2:4:1/1
        # Structure of a radinitio read fasta header
        fields = line.strip('\n')[1:].split('/')[0]
        # Split into read elements
        fields = fields.split(':')
        if int(fields[4]) != 1:
            # Keep only the first read of each clone; aka remove PCR duplicates
            continue
        # store as ri_read class
        read = ri_read(fields[0], fields[1], fields[2][1], fields[3])
        sample_reads.append(read)
    return sample_reads

# Loop through samples and extract info for all reads
def extract_reads_all_samples(samples, reads_dir, ploidy=2):
    assert type(samples) == list
    assert os.path.exists(reads_dir)
    # Allele coverage dictionary
    allele_cov_dict = dict()
    # Parse all samples
    for sam_i, sample in enumerate(samples):
        # Extract sample reads
        sample_reads = extract_sample_reads(sample, reads_dir)
        # Loop over reads and add to dictionary
        for read in sample_reads:
            # Set default to allele coverage dictionary
            alleles_val = [ None for _ in range(ploidy) ]
            for i in range(ploidy):
                samples_allele = [ 0 for _ in range(len(samples)) ]
                alleles_val[i] = samples_allele
            allele_cov_dict.setdefault(read.loc, alleles_val)
            allele_cov_dict[read.loc][read.allele][sam_i] += 1
    # Return dictionary of per-sample allele coverage
    return allele_cov_dict

# After creating coverage dictionary, write into log
def write_read_dropout_log(samples, reads_dir, out_dir, min_cov=3):
    assert type(samples) == list
    assert os.path.exists(reads_dir)
    assert os.path.exists(out_dir)
    assert type(min_cov) == int
    # Generate the allele coverage dictionary
    allele_cov_dict = extract_reads_all_samples(samples, reads_dir)
    # Create output tsv file
    out_f = open('{}/dropped_alleles_reads.tsv'.format(out_dir), 'w')
    out_f.write('allele_id\t{}\n'.format('\t'.join(samples)))
    # Loop through dictionary and save output
    for locus in sorted(allele_cov_dict):
        this_loc = allele_cov_dict[locus]
        for a_i, allele in enumerate(this_loc):
            # Create new list to determine kept or loss alleles
            allele_tally = [ '0' for _ in range(len(allele)) ]
            for i, cov in enumerate(allele):
                if cov < min_cov:
                    allele_tally[i] = '1' # Means allele was dropped
            out_f.write('{}_a{}\t{}\n'.format(locus, a_i+1, '\t'.join(allele_tally)))
