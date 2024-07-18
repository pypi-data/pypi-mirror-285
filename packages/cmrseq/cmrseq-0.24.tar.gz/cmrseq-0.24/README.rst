CMRseq
========


.. image:: https://people.ee.ethz.ch/~jweine/cmrseq/latest/_images/logo_cmrseq.svg
   :align: right
   :scale: 150 %

**Define your MRI sequences in pure python!**

The cmrseq frame-work is build to define MRI sequences consisting of radio-frequency pulses,
gradient waveforms and sampling events. All definitions follow the concept hierarchically assemble
experiments where the basic building blocks (Arbitrary Gradients, Trapezoidals, RF-pulses and
ADC-events) are forming the core functionality and are all instances of SequenceBaseBlock-instances.
On instantiation all base-blocks are validated against the System specifications. Composition of
base-blocks is done in a Sequence object. The Sequence object implements convenient definitions
for addition and composition of multiple Sequence objects as well as to perform a variety on common
operations on semantically grouped base-blocks.

Several semantically connected groups of building blocks (e.g. a slice selective excitation) are
allready functionally defined in the parametric_definitions module. For a complete list of available
definitions checkout the API-reference.

The original motivation for cmrseq was to create a foundation to define sequences for simulation
experiments. Therefore Sequences can be easily gridded onto a regular (or even unregular grids with
a maximum step width) grids. Furthermore, commonly useful functionalities as plotting, evaluation
of k-space-trajectories, calculation of moments, etc.

To close the gap to real-world measurements, cmrseq includes an IO module that allows loading
Phillips (GVE) sequence definitions as well as reading and writing Pulseq (>= 1.4) files, which
then can be used to export the sequence to multiple vendor platforms. For more information on this
file format please refer to the official `PulSeq web-page`_.

.. _PulSeq web-page: https://pulseq.github.io/

Installation
^^^^^^^^^^^^^

The registry contains the versioned package, which can be installed using:

.. code-block::

    pip install cmrseq

There are only few package dependencies, namely:
- numpy
- matplotlib to display the waveforms
- pint to assign `physical units`_ and assert correctness of calculations
- tqdm progressbar visualizations
- scipy selected functionalities

.. _physical units: https://github.com/hgrecco/pint

Documentation & Getting Started
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The API documentation for released versions can be found `here`_.

.. _here: https://people.ee.ethz.ch/~jweine/cmrseq/latest/index.html