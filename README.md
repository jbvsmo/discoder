
Discoder
========

Distributed Transcoder Tools
----------------------------


This software was created to enable distribution of video transcoding
to multiple computing nodes in a network to scale the processing horizontally.
Many approaches are limited to very few processes (normally up to 10 or 16) with 
far from optimal results.

The reason this code is able to achieve almost linear speedups even with 32 CPUs
is because it uses a combination of FFmpeg provided multithread work with a
embarrassingly parallel load of processes. Besides, this system applies load
balancing techniques to minimize the amount of idle CPU time.

With some tests, we realized that not splitting the video data directly into GOPs result
in a much smaller preprocessing overhead, letting each video process do each own 
segmentation. Empirically we noted that letting each video segment be at least 2
or 3 times the average GOP size will yield much better results.


How To Use
----------

* Tested on Ubuntu 13.04. Any Linux box should be fine.
* Currently you need to have `FFmpeg 1.0` or later with `libx264` installed. Libav is not tested.
* Python 2.7 or 3.2+
* NFS for clusters (You can also run the software on a single machine)

All the the machines where there will be video transcoding are called "nodes". The machine spawning the
processes is called "master". The "master" may own the NFS (recommended) and may also be a transcoding
node (not recommended).

On the nodes you run:

    $ python3 /path_to/discoder/start.py node -d

The `-d` option will start the process as deamon.


On the master you will have to set all your nodes IP addresses on `discoder/discoder/nodes.txt` file (ne per line).
Then you can run one or more transcoding commands. E.g. for 4 node cluster with dual 4-core HT CPUs:

    $ python3 /path_to/discoder/start.py cluster -i some_video_file.mkv -n 4 -p 32 \
     --threads 8 --fancy-seek --balance --remove -l log.txt

* `-i ...`       Input file. Must be available for all nodes on NFS!
* `-n 4`         Use the first 4 nodes of `nodes.txt`.
* `-p 32`        Total of 32 simultaneous processes (i.e. 8 per node -- should be 1 per real core).
* `--threads 8`  Number of threads per process (Should be about 1 per real core).
* `--fancy-seek` Accurate seek without decoding (This option will become default). On FFmpeg 2.1+
this is the current behaviour, but this flag is still needed.
* `--balance`    Enable load balancing (This option will become default).
* `--remove`     Remove all intermediate files (This option will become default).
* `-l log.txt`   Log file (optional).


**NOTE:** Most video transcoding options are still missing and, by default, the system will transcode
the video using H.264 with CRF 23, maintaining the audio intact and storing it as a MP4 file.
Other transcoding options are to create other video files setting bitrate and resolution (optional)
*alongside* the 1st transcoding (named "original transcoding"). E.g. Three options:

    -f 2500K:1280x720 -f 800K:640x360 -f 6000K



About:
------

This code was part of my undergraduate research to obtain an Electronic Engineering
and Computer Science degree at the Federal University of Rio de Janeiro (UFRJ). The 
monograph with all experiments and results is available (Portuguese only) [here][1].
This research also won 1st prize at the [WebMedia 2013][2] Symposium
(Workshop on Ongoing Undergraduate Research) under the title
"Transcodificação Distribuída de Vídeo com Alto Desempenho".

The software was developed at "Laboratório de Computação Paralela e Sistemas Móveis" (Compasso)


Contact:
-------

* João Bernardo Vianna Oliveira - <jbvsmo@gmail.com>
* Lauro Whately - <whately@compasso.ufrj.br>
* Diego Dutra - <diegodutra@compasso.ufrj.br>
* Claudio Amorim - <amorim@compasso.ufrj.br>


[1]: http://monografias.poli.ufrj.br/monografias/monopoli10008915.pdf
[2]: http://webmedia2013.dcc.ufba.br/
