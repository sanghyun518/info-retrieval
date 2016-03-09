Part 1 and 2.

Implemented using 'vector1.prl'.
The permutation mode can be set by changing 'my $mode' inside the main loop (line 467).
The final results are given in 'Part2Results.txt'.

Part 3.

Chose option 10 and implemented the program in Java 1.8.

The parameters {DIR} and {HOME} are equivalent to $DIR and $HOME in the Perl program.
Given the structure of my deliverable, you can set {DIR} = ../../ and {HOME} = ../../ 

How to run:
1. Move to directory: VectorIR/src/cs466/
2. Compile: javac Vector.java
3. Move to directory: VectorIR/src/
3. Do 'Option A' or 'Option B'

Option A (Run compiled source directly)
1. Run: java cs466.Vector {DIR} {HOME}

Option B (Run from executable)
1. Create executable: jar cvfm VectorIR.jar META-INF/MANIFEST.MF cs466/*.class
2. Run executable: java -jar VectorIR.jar {DIR} {HOME}