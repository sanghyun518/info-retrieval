STEP A.
1. Move to directory: VectorIR/src/cs466/
2. Compile: javac Vector.java
3. Do STEP B or STEP C

STEP B (Run compiled source directly)
1. Move to directory: VectorIR/src/
2. Run: java cs466.Vector {DIR} {HOME}

STEP C (Run from executable)
1. Move to directory: VectorIR/src/
2. Create executable: jar cvfm VectorIR.jar META-INF/MANIFEST.MF cs466/*.class
3. Run executable: java -jar VectorIR.jar {DIR} {HOME}