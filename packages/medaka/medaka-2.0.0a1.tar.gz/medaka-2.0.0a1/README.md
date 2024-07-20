
![Oxford Nanopore Technologies logo](https://github.com/nanoporetech/medaka/raw/master/images/ONT_logo_590x106.png)


Medaka
======

[![](https://img.shields.io/pypi/v/medaka.svg)](https://pypi.org/project/medaka/)
[![](https://img.shields.io/pypi/wheel/medaka.svg)](https://pypi.org/project/medaka/)
[![install with bioconda](https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg?style=flat)](https://anaconda.org/bioconda/medaka)
[![](https://img.shields.io/conda/pn/bioconda/medaka.svg)](https://anaconda.org/bioconda/medaka)


`medaka` is a tool to create consensus sequences and variant calls from
nanopore sequencing data. This task is performed using neural networks applied
a pileup of individual sequencing reads against a draft assembly. It provides
state-of-the-art results outperforming sequence-graph based methods and
signal-based methods, whilst also being faster.

© 2018- Oxford Nanopore Technologies Ltd.

Features
--------

  * Requires only basecalled data. (`.fasta` or `.fastq`)
  * Improved accuracy over graph-based methods (e.g. Racon).
  * 50X faster than Nanopolish (and can run on GPUs).
  * Includes extras for implementing and training bespoke correction
    networks.
  * Works on Linux and MacOS.
  * Open source (Mozilla Public License 2.0).

For creating draft assemblies we recommend [Flye](https://github.com/fenderglass/Flye).

Installation
------------

Medaka can be installed in one of several ways.

**Installation with pip**

Official binary releases of medaka are available on
[PyPI](https://pypi.org/project/medaka/) and can be installed using pip:

    pip install medaka

On Linux platforms this will install a precompiled binary, on MacOS (and other)
platforms this will fetch and compile a source distribution.

We recommend using medaka within a virtual environment, viz.:

    virtualenv medaka --python=python3 --prompt "(medaka) "
    . medaka/bin/activate
    pip install --upgrade pip
    pip install medaka

Using this method requires the user to provide several binaries:

 * [samtools](https://github.com/samtools/samtools),
 * [minimap2](https://github.com/lh3/minimap2),
 * [tabix](https://github.com/samtools/htslib), and
 * [bgzip](https://github.com/samtools/htslib)

and place these within the `PATH`. `samtools/bgzip/tabix` version 1.14 and
`minimap2` version 2.17 are recommended as these are those used in development
of medaka. (Newer versions are almost certainly fine).

The default installation has the capacity to run on a GPU (see _Using a GPU_ below),
or on CPU. If you are using `medaka` exclusively on CPU, and don't need the ability
to run on GPU, you may wish to install the CPU-only version with:

    pip install medaka-cpu --extra-index-url https://download.pytorch.org/whl/cpu


**Installation with conda**

> The bioconda medaka packages are no longer supported by Oxford Nanopore Technologies.

For those who prefer the conda package manager, medaka is available via the
[bioconda](https://anaconda.org/bioconda/medaka) channel:

    conda create -n medaka -c conda-forge -c bioconda medaka

The bioconda releases lag behind the source code and [PyPI](https://pypi.org/project/medaka/)
releases.


**Installation from source**

> This method is useful for macOS M1 devices as it will assist in building
> dependencies which will fail with the other methods above.

Medaka can be installed from its source quite easily on most systems.

 Before installing medaka it may be required to install some
 prerequisite libraries, best installed by a package manager. On Ubuntu
 theses are:
 >     bzip2 g++ zlib1g-dev libbz2-dev liblzma-dev libffi-dev libncurses5-dev
 >     libcurl4-gnutls-dev libssl-dev curl make cmake wget python3-all-dev
 >     python-virtualenv
 In addition it is required to install and set up git LFS before cloning
 the repository.

A Makefile is provided to fetch, compile and install all direct dependencies
into a python virtual environment. To set-up the environment run:

    # Note: certain files are stored in git-lfs, https://git-lfs.github.com/,
    #       which must therefore be installed first.
    git clone https://github.com/nanoporetech/medaka.git
    cd medaka
    make install
    . ./venv/bin/activate

Using this method both `samtools` and `minimap2` are built from source and need
not be provided by the user.

When building from source, to install a CPU-only version without the capacity to
run on GPU, modify the above to:

    MEDAKA_CPU=1 make install


**Using a GPU**

Since version 2.0 `medaka` uses PyTorch. Prior versions (v1.x) used Tensorflow.

The default version of PyTorch that is installed when building from source or 
when installing through `pip` can make immediate use of GPUs via NVIDIA CUDA.
However, note that the `torch` package is compiled against specific versions of
the CUDA and cuDNN libraries; users are directed to the 
[torch installation](https://pytorch.org/get-started/locally/) pages for further
information. cuDNN can be obtained from the 
[cuDNN Archive](https://developer.nvidia.com/rdp/cudnn-archive), whilst CUDA from
the [CUDA Toolkit Archive](https://developer.nvidia.com/cuda-toolkit-archive).

As described above, if the capability to run on GPU is not required, `medaka-cpu`
can be installed with a CPU-only version of PyTorch that doesn't depend on the
CUDA libraries, as follows:

    pip install medaka-cpu --extra-index-url https://download.pytorch.org/whl/cpu

if using the prebuilt packages, or 

    MEDAKA_CPU=1 make install

if building from source.

*GPU Usage notes*

Depending on your GPU, `medaka` may show out of memory errors when running.
To avoid these the inference batch size can be reduced from the default
value by setting the `-b` option when running `medaka_consensus`. A value
`-b 100` is suitable for 11Gb GPUs.


**Using Docker**

The source code repository contains a `Dockerfile` which can be used to create
a GPU compatible Docker container image with the appropriate CUDA and cuDNN
library versions for running medaka. The image is built on top of images
[provided by NVIDIA](https://hub.docker.com/r/nvidia/cuda) designed to run with the [NVIDIA Container
Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).
With the toolkit setup on your host computer the following command can be used
to run the latest version of medaka:

    docker run --rm --gpus 0 ontresearch/medaka:latest medaka --help

(The `--gpus` option can be amended as appropriate for your environment). Versioned
tags are also available.


Usage
-----

`medaka` can be run using its default settings through the `medaka_consensus`
program. An assembly in `.fasta` format and basecalls in `.fasta` or `.fastq`
formats are required. The program uses both `samtools` and `minimap2`. If
medaka has been installed using the from-source method these will be present
within the medaka environment, otherwise they will need to be provided by
the user.

    source ${MEDAKA}  # i.e. medaka/venv/bin/activate
    NPROC=$(nproc)
    BASECALLS=basecalls.fa
    DRAFT=draft_assm/assm_final.fa
    OUTDIR=medaka_consensus
    medaka_consensus -i ${BASECALLS} -d ${DRAFT} -o ${OUTDIR} -t ${NPROC} -m r941_min_high_g303

The variables `BASECALLS`, `DRAFT`, and `OUTDIR` in the above should be set
appropriately. For the selection of the model (`-m r941_min_high_g303` in the
example above) see the Model section following.

When `medaka_consensus` has finished running, the consensus will be saved to
`${OUTDIR}/consensus.fasta`.


**Bacterial (ploidy-1) variant calling**

Variant calling for monoploid samples is enabled through the `medaka_haploid_variant`
workflow:

    medaka_haploid_variant -i <reads.fastq> -r <ref.fasta>
    
which requires the reads as a `.fasta` or `.fastq` and a reference sequence as a
`.fasta` file.


**Diploid variant calling**

The diploid variant calling workflow `medaka_variant` that was historically implemented
within the medaka package has been surpassed in accuracy and compute performance by
other methods, it has therefore been deprecated. Our current recommendation for
performing this task is to use [Clair3](https://github.com/HKU-BAL/Clair3) either directly
or through the Oxford Nanopore Technologies provided Nextflow implementation available
through [EPI2ME Labs](https://labs.epi2me.io/wfindex#variant-calling).


Models
------

For best results it is important to specify the correct model, `-m` in the
above, according to the basecaller used. Allowed values can be found by
running `medaka tools list\_models`.

**Recent basecallers**

Recent basecaller versions annotate their output with their model version.
In such cases medaka can inspect the files and attempt to select an appropriate
model for itself. This typically works best in the case of BAM output from
basecallers. It will work also for FASTQ input provided the FASTQ has been
created from basecaller output using:

```
samtools fastq -T '*' dorado.bam | gzip -c > dorado.fastq.gz
```

The command `medaka consensus` will attempt to automatically determine a
correct model by inspecting its BAM input file. The helper scripts
`medaka_consensus` and `medaka_haploid_variant` will make similar attempts
from their FASTQ input.

To inspect files for yourself, the command:

```
medaka tools resolve_model --auto_model <consensus/variant> <input.bam/input.fastq>
```

will print the model that automatic model selection will use.


**For older basecallers and when automatic selection is unsuccessful**

If the name of the basecaller model used is known, but has been lost from the input
files, the basecaller model can been provided to medaka directly. It must however
be appended with either `:consensus` or `:variant` according to whether the user
wishing to use the consensus or variant calling medaka model. For example:

```
medaka consensus input.bam output.hdf \
    --model dna_r10.4.1_e8.2_400bps_hac@v4.1.0:variant
```

will use the medaka variant calling model appropriate for use with the basecaller
model named `dna_r10.4.1_e8.2_400bps_hac@v4.1.0`.

Medaka models are named to indicate i) the pore type, ii) the sequencing
device (MinION or PromethION), iii) the basecaller variant, and iv) the
basecaller version, with the format:

    {pore}_{device}_{caller variant}_{caller version}

For example the model named `r941_min_fast_g303` should be used with data from
MinION (or GridION) R9.4.1 flowcells using the fast Guppy basecaller version
3.0.3. By contrast the model `r941_prom_hac_g303` should be used with PromethION
data and the high accuracy basecaller (termed "hac" in Guppy configuration
files). Where a version of Guppy has been used without an exactly corresponding
medaka model, the medaka model with the highest version equal to or less than
the guppy version should be selected.


Improving parallelism
---------------------

The `medaka_consensus` program is good for simple datasets but perhaps not
optimal for running large datasets at scale. A higher level of parallelism
can be achieved by running independently the component steps of
`medaka_consensus`. The program performs three tasks:

1. alignment of reads to input assembly (via `mini_align` which is a thin
   veil over `minimap2`)
2. running of consensus algorithm across assembly regions
   (`medaka consensus`, note no underscore!)
3. aggregation of the results of 2. to create consensus sequences
   (`medaka stitch`)

The three steps are discrete, and can be split apart and run independently. In
most cases, Step 2. is the bottleneck and can be trivially parallelized. The
`medaka consensus` program can be supplied a `--regions`
argument which will restrict its action to particular assembly sequences from
the `.bam` file output in Step 1. Therefore individual jobs can be run for batches
of assembly sequences simultaneously. In the final step, `medaka stitch`
can take as input one or more of the `.hdf` files output by Step 2.

So in summary something like this is possible:

```
# align reads to assembly
mini_align -i basecalls.fasta -r assembly.fasta -P -m \
    -p calls_to_draft.bam -t <threads>
# run lots of jobs like this, change model as appropriate
mkdir results
medaka consensus calls_to_draft.bam results/contigs1-4.hdf \
    --model r941_min_fast_g303 --batch 200 --threads 8 \
    --region contig1 contig2 contig3 contig4
...
# wait for jobs, then collate results
medaka stitch results/*.hdf polished.assembly.fasta
```

It is not recommended to specify a value of `--threads` greater than 2 for
`medaka consensus` since the compute scaling efficiency is poor beyond this.
Note also that `medaka consensus` may been seen to use resources equivalent to
`<threads> + 4` as an additional 4 threads are used for reading and preparing
input data.


Origin of the draft sequence
----------------------------

Medaka has been trained to correct draft sequences output from the
[Flye](https://github.com/fenderglass/Flye) assembler.

Processing a draft sequence from alternative sources (e.g. the output of
[canu](https://github.com/marbl/canu) or
[wtdbg2](https://github.com/ruanjue/wtdbg2)) may lead to different results.

> Historical correction
> models in medaka were trained to correct draft sequences output from the canu
> assembler with [racon](https://github.com/lbcb-sci/racon) applied either once,
> or four times iteratively. For contemporary models this is not the case and
> medaka should be used directly on the output of Flye.



Acknowledgements
----------------

We thank [Joanna Pineda](https://github.com/jopineda) and
[Jared Simpson](https://github.com/jts) for providing htslib code samples which aided
greatly development of the optimised feature generation code, and for testing the
version 0.4 release candidates.

We thank [Devin Drown](https://github.com/devindrown) for
[working through](https://github.com/nanoporetech/medaka/issues/70)
use of `medaka` with his RTX 2080 GPU.

Help
----

**Licence and Copyright**

© 2018- Oxford Nanopore Technologies Ltd.

`medaka` is distributed under the terms of the Mozilla Public License 2.0.

**Research Release**

Research releases are provided as technology demonstrators to provide early
access to features or stimulate Community development of tools. Support for
this software will be minimal and is only provided directly by the developers.
Feature requests, improvements, and discussions are welcome and can be
implemented by forking and pull requests. However much as we would
like to rectify every issue and piece of feedback users may have, the
developers may have limited resource for support of this software. Research
releases may be unstable and subject to rapid iteration by Oxford Nanopore
Technologies.
