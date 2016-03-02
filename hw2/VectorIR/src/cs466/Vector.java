package cs466;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Scanner;
import java.util.Set;
import java.util.TreeMap;
import java.util.stream.IntStream;

public class Vector {
	
	private enum MODE {
	    ONE_A, ONE_B, ONE_C,
	    TWO_A, TWO_B,
	    THREE_A, THREE_B,
	    FOUR_A, FOUR_B,
	    FIVE_A, FIVE_B, FIVE_C,
	    DEFAULT
	}
	
	private static final String DIR = "C:\\Users\\Sanghyun\\Documents\\GitHub\\info-retrieval\\hw2";
	private static final String HOME = "C:\\Users\\Sanghyun\\Documents\\GitHub\\info-retrieval\\hw2";
	
	private static final String STEMMED = "stemmed";
	private static final String TOKENIZED = "tokenized";
	private static final String HISTOGRAM = "hist";

	private static final String TOKEN_DOCS = DIR + "\\cacm";
	private static final String CORPS_FREQ = DIR + "\\cacm";
	private static final String STOPLIST = DIR + "\\common_words";
	private static final String TITLES = DIR + "\\titles.short";
	private static final String TOKEN_QRYS = DIR + "\\query";
	private static final String QUERY_FREQ = DIR + "\\query";
	private static final String QUERY_RELV = DIR + "\\query.rels";

	private static final String TOKEN_INTR = HOME + "\\interactive";

	private static final ArrayList<HashMap<String, Double>> docVector = new ArrayList<HashMap<String, Double>>();
	private static final ArrayList<HashMap<String, Double>> qryVector = new ArrayList<HashMap<String, Double>>();
	private static final HashMap<String, Integer> docsFreqHash = new HashMap<String, Integer>();
	private static final HashMap<String, Integer> corpFreqHash = new HashMap<String, Integer>();
	private static final HashSet<String> stoplistHash = new HashSet<String>();
	private static final ArrayList<String> titlesVector = new ArrayList<String>();
	private static final HashMap<Integer, HashMap<Integer, Boolean>> relevanceHash = new HashMap<Integer, HashMap<Integer, Boolean>>();
	private static double[] docSimula;
	private static int[] resVector;

	private static void initCorpFreq(MODE mode) throws Exception {
		boolean isStemmed = mode != MODE.THREE_A;
		
		FileReader in = null;
		BufferedReader br = null;
		
		docsFreqHash.clear();
		corpFreqHash.clear();

		try {
			in = new FileReader(CORPS_FREQ + "." + (isStemmed ? STEMMED : TOKENIZED) + "." + HISTOGRAM);
			br = new BufferedReader(in);
			
			String line;
			while ((line = br.readLine()) != null) {
				String[] tokens = line.trim().split("\\s+");
				String word = tokens.length > 2 ? tokens[2] : "";
				docsFreqHash.put(word, Integer.parseInt(tokens[0]));
				corpFreqHash.put(word, Integer.parseInt(tokens[1]));
			}
		} finally {
			closeResouce(in, br);
		}
		
		try {
			in = new FileReader(QUERY_FREQ + "." + (isStemmed ? STEMMED : TOKENIZED) + "." + HISTOGRAM);
			br = new BufferedReader(in);
			
			String line;
			while ((line = br.readLine()) != null) {
				String[] tokens = line.trim().split("\\s+");
				String word = tokens.length > 2 ? tokens[2] : "";
				Integer docFreq = docsFreqHash.get(word);
				Integer corpFreq = corpFreqHash.get(word);
				docsFreqHash.put(word, (docFreq == null ? 0 : docFreq) + Integer.parseInt(tokens[0]));
				corpFreqHash.put(word, (corpFreq == null ? 0 : corpFreq) + Integer.parseInt(tokens[1]));
			}
		} finally {
			closeResouce(in, br);
		}
		
		stoplistHash.clear();
		
		try {
			in = new FileReader(STOPLIST + (isStemmed ? ("." + STEMMED) : ""));
			br = new BufferedReader(in);
			
			String line;
			while ((line = br.readLine()) != null) {
				stoplistHash.add(line.trim());
			}
		} finally {
			closeResouce(in, br);
		}
		
		titlesVector.clear();
		titlesVector.add("");
		
		try {
			in = new FileReader(TITLES);
			br = new BufferedReader(in);
			
			String line;
			while ((line = br.readLine()) != null) {
				titlesVector.add(line.trim());
			}
		} finally {
			closeResouce(in, br);
		}
		
		relevanceHash.clear();
		
		try {
			in = new FileReader(QUERY_RELV);
			br = new BufferedReader(in);
			
			String line;
			while ((line = br.readLine()) != null) {
				String[] tokens = line.split("\\s+");
				Integer qryNum = Integer.parseInt(tokens[0]);
				Integer relDoc = Integer.parseInt(tokens[1]);
				
				HashMap<Integer, Boolean> hashMap = relevanceHash.get(qryNum);
				if (hashMap == null) {
					hashMap = new HashMap<Integer, Boolean>();
					relevanceHash.put(qryNum, hashMap);
				}
				hashMap.put(relDoc, true);
			}
		} finally {
			closeResouce(in, br);
		}
	}
	
	private static int initDocVectors(MODE mode) throws Exception {
		int titleBaseWeight = 3;
		int keywdBaseWeight = 4;
		int abstrBaseWeight = 1;
		int authrBaseWeight = 3;
		
		if (mode == MODE.FIVE_A) {
			titleBaseWeight = 1;
			keywdBaseWeight = 1;
			abstrBaseWeight = 1;
			authrBaseWeight = 1;
		} else {
			if (mode == MODE.FIVE_C) {
				titleBaseWeight = 1;
				keywdBaseWeight = 1;
				abstrBaseWeight = 4;
				authrBaseWeight = 1;
			}
		}
		
		FileReader in = null;
		BufferedReader br = null;
		
		boolean isStemmed = mode != MODE.THREE_A;
		
		docVector.clear();
		docVector.add(new HashMap<String, Double>());
		
		int docNum = 0;
		double tWeight = 0.0;
		
		try {
			in = new FileReader(TOKEN_DOCS + "." + (isStemmed ? STEMMED : TOKENIZED));
			br = new BufferedReader(in);
			
			String word;
			while ((word = br.readLine()) != null) {
				word = word.trim();
				
				if (".I 0".equals(word)) {
					break;
				} else {
					if (word.startsWith(".I")) {
						docVector.add(new HashMap<String, Double>());
						docNum++;
						
						continue;
					}
				}
				
				if (word.startsWith(".T")) {
					tWeight = titleBaseWeight;
					continue;
				} else if (word.startsWith(".K")) {
					tWeight = keywdBaseWeight;
					continue;
				} else if (word.startsWith(".W")) {
					tWeight = abstrBaseWeight;
					continue;
				} else {
					if (word.startsWith(".A")) {
						tWeight = authrBaseWeight;
						continue;
					}
				}
				
				if ((mode == MODE.FOUR_B && !word.isEmpty()) 
						|| (word.matches(".*[a-zA-Z]+.*") && !stoplistHash.contains(word))) {
					Integer freq = docsFreqHash.get(word);
					if (freq == null) {
						System.err.println("ERROR: Document frequency of zero: " + word);
					} else {
						if (mode == MODE.ONE_C) {
							docVector.get(docNum).put(word, 1.0);
						} else {
							Double weight = docVector.get(docNum).get(word);
							if (weight == null) {
								weight = 0.0;
							}
							docVector.get(docNum).put(word, weight + tWeight);
						}
					}
				}
			}
			
			if (mode != MODE.ONE_A && mode != MODE.ONE_C) {
				for (HashMap<String, Double> map : docVector) {
					Set<Entry<String, Double>> entrySet = map.entrySet();
					for (Entry<String, Double> entry : entrySet) {
						Integer freq = docsFreqHash.get(entry.getKey());
						map.put(entry.getKey(), entry.getValue() * Math.log((double) docNum / (double) freq));
					}
				}
			}
		} finally {
			closeResouce(in, br);
		}
		
		return docNum;
	}
	
	private static int initQryVectors(MODE mode) throws Exception {
		int queryBaseWeight = 2;
		int queryAuthWeight = 2;
		
		FileReader in = null;
		BufferedReader br = null;
		
		boolean isStemmed = mode != MODE.THREE_A;
		
		qryVector.clear();
		qryVector.add(new HashMap<String, Double>());
		
		int qryNum = 0;
		double tWeight = 0.0;
		
		try {
			in = new FileReader(TOKEN_QRYS + "." + (isStemmed ? STEMMED : TOKENIZED));
			br = new BufferedReader(in);
			
			String word;
			while ((word = br.readLine()) != null) {
				word = word.trim();
				
				if (word.startsWith(".I")) {
					qryVector.add(new HashMap<String, Double>());
					qryNum++;
					
					continue;
				}
				
				if (word.startsWith(".W")) {
					tWeight = queryBaseWeight;
					continue;
				} else {
					if (word.startsWith(".A")) {
						tWeight = queryAuthWeight;
						continue;
					}
				}
				
				if ((mode == MODE.FOUR_B && !word.isEmpty()) 
						|| (word.matches(".*[a-zA-Z]+.*") && !stoplistHash.contains(word))) {
					Integer freq = docsFreqHash.get(word);
					if (freq == null) {
						System.err.println("ERROR: Document frequency of zero: " + word);
					} else {
						if (mode == MODE.ONE_C) {
							qryVector.get(qryNum).put(word, 1.0);
						} else {
							Double weight = qryVector.get(qryNum).get(word);
							if (weight == null) {
								weight = 0.0;
							}
							qryVector.get(qryNum).put(word, weight + tWeight);
						}
					}
				}
			}
		} finally {
			closeResouce(in, br);
		}
		
		return qryNum;
	}

	private static void closeResouce(FileReader in, BufferedReader br) throws IOException {
		if (in != null) {
			in.close();
		}
		if (br != null) {
			br.close();
		}
	}

	public static void main(String[] args) {
		MODE mode = MODE.THREE_A;
		
		System.out.println("INITIALIZING VECTORS ...");
		
		Scanner reader = null;
		
		try {
			initCorpFreq(mode);
			
			int totalDocs = initDocVectors(mode);
			int totalQrys = initQryVectors(mode);
			
			while (true) {
				reader = new Scanner(System.in);
				
				System.out.printf("	============================================================\n" + 
						"	==     Welcome to the 600.466 Vector-based IR Engine\n" + 
						"	==                                                  \n" + 
						"        == Total Documents: %s                     \n" + 
						"	== Total Queries:   %s                     \n" + 
						"	============================================================\n" + 
						"\n" + 
						"	OPTIONS:\n" + 
						"	  1 = Find documents most similar to a given query or document\n" + 
						"	  2 = Compute precision/recall for the full query set\n" + 
						"	  3 = Compute cosine similarity between two queries/documents\n" + 
						"	  4 = Quit\n" + 
						"\n" + 
						"	============================================================\n", totalDocs, totalQrys);
				
				System.out.print("Enter Options: ");
				
				String optionStr = reader.next("[1-4]*");
				
				int option = optionStr.matches("[1-4]") ? Integer.parseInt(optionStr) : 1; 
				
				if (option == 4) {
					break;
				}
				
				if (option == 2) {
					fullPrecisionRecallTest();
					continue;
				}
				
				if (option == 3) {
					doFullCosineSimilarity(reader);
					continue;
				}
				
				getAndShowRetrievedSet(mode, reader);
			}
		} catch (Exception e) {
			e.printStackTrace();
		} finally {
			if (reader != null) {
				reader.close();
			}
		}
	}
	
	private static void getAndShowRetrievedSet(MODE mode, Scanner reader) throws Exception {
		System.out.println("    Find documents similar to:\n" + 
				"        (1) a query from 'query.raw'\n" + 
				"	(2) an interactive query\n" + 
				"	(3) another document");
		
		System.out.print("Choice: ");
		
		String optionStr = reader.next().trim();
		
		int compType = optionStr.matches("[1-3]") ? Integer.parseInt(optionStr) : 1;
		
		System.out.print("\n");
		
		int vectNum = 1;
		
		if (compType != 2) {
			System.out.print("Target Document/Query number: ");
			
			optionStr = reader.next().trim();
			
			vectNum = optionStr.matches("[1-9][0-9]*") ? Integer.parseInt(optionStr) : 1;
			
			System.out.print("\n");
		}
		
		System.out.print("Show how many matching documents (20): ");
		
		int maxShow = 20;
		
		optionStr = reader.next().trim();
		
		maxShow = optionStr.matches("[0-9]+") ? Integer.parseInt(optionStr) : 20;
		
		System.out.print("\n");
		
		if (compType == 3) {
			System.out.println("Document to Document comparison");
			
			getRetrievedSet(docVector.get(vectNum), mode);
			shwRetrievedSet(maxShow, vectNum, docVector.get(vectNum), "Document", reader);
		} else if (compType == 2) {
			System.out.println("Interactive Query to Document comparison");
			
			HashMap<String, Double> intVector = setInteractVec(mode);
			
			getRetrievedSet(intVector, mode);
			shwRetrievedSet(maxShow, 0, intVector, "Document", reader);
		} else {
			System.out.println("Query to Document comparison");
			
			getRetrievedSet(qryVector.get(vectNum), mode);
			shwRetrievedSet(maxShow, vectNum, qryVector.get(vectNum), "Query", reader);
			compRecall(relevanceHash.get(vectNum), vectNum);
			showRelvnt(relevanceHash.get(vectNum), vectNum, qryVector.get(vectNum));
		}
	}
	
	private static HashMap<String, Double> setInteractVec(MODE mode) throws Exception {
		int queryBaseWeight = 2;
		int queryAuthWeight = 2;
		
		FileReader in = null;
		BufferedReader br = null;
		
		boolean isStemmed = mode != MODE.THREE_A;
		
		HashMap<String, Double> intVector = new HashMap<String, Double>();
		
		double tWeight = 0.0;
		
		try {
			in = new FileReader(TOKEN_INTR + "." + (isStemmed ? STEMMED : TOKENIZED));
			br = new BufferedReader(in);
			
			String line;
			while ((line = br.readLine()) != null) {
				line = line.trim();
				
				System.out.println(line);
				
				if (line.startsWith(".I")) {
					continue;
				}
				
				if (line.startsWith(".W")) {
					tWeight = queryBaseWeight;
					continue;
				} else {
					if (line.startsWith(".A")) {
						tWeight = queryAuthWeight;
						continue;
					}
				}
				
				if ((mode == MODE.FOUR_B && !line.isEmpty()) 
						|| (line.matches(".*[a-zA-Z]+.*") && !stoplistHash.contains(line))) {
					Integer freq = docsFreqHash.get(line);
					if (freq == null) {
						System.err.println("ERROR: Document frequency of zero: " + line);
					} else {
						if (mode == MODE.ONE_C) {
							intVector.put(line, 1.0);
						} else {
							Double weight = intVector.get(line);
							if (weight == null) {
								weight = 0.0;
							}
							intVector.put(line, weight + tWeight);
						}
					}
				}
			}
		} finally {
			closeResouce(in, br);
		}
		
		return intVector;
	}
	
	private static void getRetrievedSet(HashMap<String, Double> qryVector, MODE mode) {
		int totNumber = docVector.size() - 1;
		
		docSimula = new double[totNumber + 1];
		resVector = new int[totNumber];
		
		docSimula[0] = 0.0; // push one empty value so that indices correspond with document values
		
		final Map<Integer, Double> treeMap = new TreeMap<Integer, Double>(new Comparator<Integer>() {

			@Override
			public int compare(Integer o1, Integer o2) {
				if (docSimula[o1] >= docSimula[o2]) {
					return -1;
				} else {
					return 1;
				}
			}
		});
		
		for (int docNumber = 1; docNumber <= totNumber; docNumber++) {
			if (mode == MODE.TWO_B) {
				docSimula[docNumber] = jaccardSimA(qryVector, docVector.get(docNumber));
			} else {
				docSimula[docNumber] = cosineSimA(qryVector, docVector.get(docNumber));
			}
			
			treeMap.put(docNumber, docSimula[docNumber]);
		}
		
		Set<Integer> sortedIndices = treeMap.keySet();
		int index = 0;
		for (int sortedIndex : sortedIndices) {
			resVector[index++] = sortedIndex;
		}
	}
	
	private static void shwRetrievedSet(int maxShow, int qryNum, HashMap<String, Double> qryVect, String comparison, Scanner reader) {
		System.out.printf("************************************************************\n" + 
				"	Documents Most Similar To %s number %d\n" + 
				"    ************************************************************\n" + 
				"    Similarity   Doc#  Author      Title\n" + 
				"    ==========   ==== ========     =============================\n", comparison, qryNum);
		
		int relNum = qryNum;
		
		HashMap<Integer, Boolean> hashMap = relevanceHash.get(relNum);
		
		for (int i = 0; i < maxShow; i++) {
			int docNum = resVector[i];
			
			if ("Query".equalsIgnoreCase(comparison) && hashMap != null && hashMap.get(docNum) == Boolean.TRUE) {
				System.out.print("* ");
			} else {
				System.out.print("  ");
			}
			
			String similarity = String.format("%.8f", docSimula[docNum]);
			String title = titlesVector.get(docNum);
			
			if (title.length() > 47) {
				title = title.substring(0, 47);
			}
			
			System.out.println("  " + similarity + "   " + title);
		}
		
		System.out.print("\n");
		System.out.print("Show the terms that overlap between the query and retrieved docs (y/n): ");
		
		String showTerms = reader.next();
		
		if (!"n".equalsIgnoreCase(showTerms)) {
			for (int i = 0; i < maxShow; i++) {
				int docNum = resVector[i];
				
				showOverlap(qryVect, docVector.get(docNum), qryNum, docNum);
				
				if (i % 5 == 4) {
					System.out.print("\n");
					System.out.print("Continue (y/n)? ");
					
					String cont = reader.next();
					
					if ("n".equalsIgnoreCase(cont)) {
						break;
					}
				}
			}
		}
	}
	
	private static double[] compRecall(HashMap<Integer, Boolean> relHash, int qvn) {
		List<Integer> docRank = new ArrayList<Integer>();
		
		int totNumber = docVector.size() - 1;
		
		int index = 0;
		for (int docNum : resVector) {
			if (relHash != null && relHash.get(docNum) == Boolean.TRUE) {
				docRank.add(index + 1);
			}
			index++;
		}
		
		List<Integer> recallLevel = new ArrayList<Integer>();
		
		for (int i = 1; i <= 9; i++) {
			recallLevel.add(10 * i);
		}
		
		recallLevel.add(25);
		recallLevel.add(75);
		
		Collections.sort(recallLevel);
		
		Map<Integer, Double> precisions = new HashMap<Integer, Double>();
		
		int totRel = docRank.size();
		
		precisions.put(100, (double) totRel / (double) docRank.get(totRel - 1));
		
		for (int i = 0; i < totRel; i++) {
			double currRecallLevel = (double) i / (double) totRel;
			double nextRecallLevel = (double) (i + 1) / (double) totRel;
			double currPrecLevel = i == 0 ? 0.0 : ((double) i) / (double) docRank.get(i - 1);
			double nextPrecLevel = (double) (i + 1) / (double) docRank.get(i);
			
			int idx = 0;
			
			double recallLvl = (double) recallLevel.get(idx) / (double) 100;
			
			while (currRecallLevel <= recallLvl && recallLvl < nextRecallLevel) {
				double precision = (recallLvl - currRecallLevel) / (nextRecallLevel - currRecallLevel) 
						* (nextPrecLevel - currPrecLevel) + currPrecLevel;
				precisions.put(recallLevel.get(idx), precision);
				
				if (++idx == recallLevel.size()) {
					break;
				}
				
				recallLvl = (double) recallLevel.get(idx) / (double) 100;
			}
			
			while (idx > 0 && recallLevel.size() > 0) {
				recallLevel.remove(0);
				idx--;
			}
			
			if (recallLevel.size() == 0) {
				break;
			}
		}
		
		double precMean1 = (precisions.get(25) + precisions.get(50) + precisions.get(75)) / 3;
		double precMean2 = IntStream.rangeClosed(1, 10).mapToDouble(i -> precisions.get(10 * i)).sum() / 10;
		double precNorm = 1.0 - (docRank.stream().map(rank -> Math.log(rank)).reduce(0.0, Double::sum) 
				- IntStream.rangeClosed(1, totRel).mapToDouble(i -> Math.log(i)).reduce(0.0, Double::sum))
				/ (totNumber * Math.log(totNumber) - (totNumber - totRel) * Math.log(totNumber - totRel) - totRel * Math.log(totRel));
		double recallNorm = 1.0 - ((double) (docRank.stream().reduce(0, Integer::sum) - IntStream.rangeClosed(1, totRel).sum())) 
				/ ((double) totRel * (totNumber - totRel));
		
		
		return new double[] { precisions.get(25), precisions.get(50), precisions.get(75), precisions.get(100),
				precMean1, precMean2, precNorm, recallNorm };
	}
	
	private static void showRelvnt(HashMap<Integer, Boolean> relHash, int qvn, HashMap<String, Double> qvector) {
		System.out.printf("    ************************************************************\n" + 
				"	Documents relevant to query number %d\n" + 
				"    ************************************************************\n" + 
				"    Similarity   Doc#  Author      Title\n" + 
				"    ==========   ==== ========     =============================\n", qvn);
		
		for (int docNum : resVector) {
			if (relHash != null && relHash.get(docNum) == Boolean.TRUE) {
				String similarity = String.format("%.8f", docSimula[docNum]);
				String title = titlesVector.get(docNum);
				
				if (title.length() > 47) {
					title = title.substring(0, 47);
				}
				
				System.out.println("  " + similarity + "   " + title);
			}
		}
	}
	
	private static void showOverlap(HashMap<String, Double> qryVect, HashMap<String, Double> docVect, int qryNum, int docNum) {
		System.out.println("============================================================");
		System.out.printf("%-15s  %8d   %8d\t%s\n", "Vector Overlap", qryNum, docNum, "Docfreq");
		System.out.println("============================================================");
		
		qryVect.forEach((termOne, weightOne) -> {
			Double weightTwo = docVect.get(termOne);
			if (weightTwo != null) {
				System.out.printf("%-15s  %8d   %8d\t%d\n", termOne, weightOne.intValue(), weightTwo.intValue(), docsFreqHash.get(termOne));
			}
		});
	}
	
	private static void doFullCosineSimilarity(Scanner reader) {
		System.out.print("\n");
		System.out.print("1st Document/Query number: ");
		
		String numOneStr = reader.next().trim();
		
		int numOne = numOneStr.matches("[1-9][0-9]*") ? Integer.parseInt(numOneStr) : 1;
		
		System.out.print("2nd Document/Query number: ");
		
		String numTwoStr = reader.next().trim();
		
		int numTwo = numTwoStr.matches("[1-9][0-9]*") ? Integer.parseInt(numOneStr) : 1;
		
		fullCosineSimilarity(qryVector.get(numOne), docVector.get(numTwo), numOne, numTwo);
	}
	
	private static void fullCosineSimilarity(HashMap<String, Double> qryVect, HashMap<String, Double> docVect, int qryIndx, int docIndx) {
		System.out.println("============================================================");
		System.out.printf("%-15s  %8d   %8d\t%-15s\n", "Vector Overlap", qryIndx, docIndx, "Weight Product");
		System.out.println("============================================================");
		
		Set<Entry<String, Double>> entrySet = qryVect.entrySet();
		for (Entry<String, Double> entry : entrySet) {
			String termOne = entry.getKey();
			Double weightOne = entry.getValue();
			Double weightTwo = docVect.get(termOne);
			if (weightTwo != null) {
				System.out.printf("%-15s  %8d   %8d\t%.8f\n", termOne, weightOne.intValue(), weightTwo.intValue(), weightOne * weightTwo);
			}
		}
		
		double cosineSim = cosineSimA(qryVect, docVect);
		double diceSim = diceSimA(qryVect, docVect);
		double jaccardSim = jaccardSimA(qryVect, docVect);
		
		System.out.println("============================================================");
		System.out.printf("%-15s\t%-15s\t%-15s\n", "Cosine Sim.", "Dice Sim.", "Jaccard Sim.");
		System.out.printf("%.8f\t%.8f\t%.8f\n", cosineSim, diceSim, jaccardSim);
		System.out.println("============================================================");
	}
	
	private static void fullPrecisionRecallTest() throws Exception {
		System.out.println("======================================================================================");
		System.out.println("Permutation Name\tP_0.25\tP_0.50\tP_0.75\tP_1.00\tP_mean1\tP_mean2\tP_norm\tR_norm");
		System.out.println("======================================================================================");
		
		runExperiment("Raw TF Weight     ", MODE.ONE_A);
		runExperiment("Boolean Weight    ", MODE.ONE_C);
		runExperiment("Jaccard Similarity", MODE.TWO_B);
		runExperiment("Unstemmed Tokens  ", MODE.THREE_A);
		runExperiment("Include All Tokens", MODE.FOUR_B);
		runExperiment("Equal Weights     ", MODE.FIVE_A);
		runExperiment("Relative Weights  ", MODE.FIVE_C);
		runExperiment("Default Setting   ", MODE.DEFAULT);
	}
	
	private static void runExperiment(String name, MODE mode) throws Exception {
		// Re-initialize vectors
		
		initCorpFreq(mode);
		initDocVectors(mode);
		initQryVectors(mode);
		
		// Collect results
		
		List<Double> averagedResults = new ArrayList<Double>(8);
		for (int j = 0; j < 8; j++) {
			averagedResults.add(0.0);
		}
		
		int totQueries = qryVector.size() - 1;
		
		for (int i = 1; i <= totQueries; i++) {
			getRetrievedSet(qryVector.get(i), mode);
			double[] recall = compRecall(relevanceHash.get(i), i);
			for (int j = 0; j < averagedResults.size(); j++) {
				averagedResults.set(j, averagedResults.get(j) + recall[j]); 
			}
		}
		
		System.out.print(name + "\t");
		
		for (int j = 0; j < averagedResults.size(); j++) {
			System.out.printf("%.3f\t", averagedResults.get(j) / totQueries);
		}
		
		System.out.print("\n");
	}
	
	private static double cosineSimA(HashMap<String, Double> vec1 , HashMap<String, Double> vec2) {
		double num  = 0;
		double sumSq1 = 0;
		double sumSq2 = 0;
		
		if (vec1.size() > vec2.size()) {
			HashMap<String, Double> temp = vec1;
			vec1 = vec2;
			vec2 = temp;
		}
		
		Set<Entry<String, Double>> entrySet = vec1.entrySet();
		for (Entry<String, Double> entry : entrySet) {
			Double value = vec2.get(entry.getKey());
			num += entry.getValue() *(value == null ? 0 : value);
		}
		
		Collection<Double> values = vec1.values();
		for (Double value : values) {
			sumSq1 += value * value;
		}
		
		values = vec2.values();
		for (Double value : values) {
			sumSq2 += value * value;
		}
		
		return cosineSimB(num, sumSq1, sumSq2);
	}
	
	private static double cosineSimB(double num, double sumSq1, double sumSq2) {
		return num / Math.sqrt(sumSq1 + sumSq2);
	}
	
	private static double diceSimA(HashMap<String, Double> vec1 , HashMap<String, Double> vec2) {
		double num  = 0;
		double sum1 = 0;
		double sum2 = 0;
		
		if (vec1.size() > vec2.size()) {
			HashMap<String, Double> temp = vec1;
			vec1 = vec2;
			vec2 = temp;
		}
		
		Set<Entry<String, Double>> entrySet = vec1.entrySet();
		for (Entry<String, Double> entry : entrySet) {
			Double value = vec2.get(entry.getKey());
			num += entry.getValue() *(value == null ? 0 : value);
		}
		
		Collection<Double> values = vec1.values();
		for (Double value : values) {
			sum1 += value;
		}
		
		values = vec2.values();
		for (Double value : values) {
			sum2 += value;
		}
		
		return diceSimB(num, sum1, sum2);
	}
	
	private static double diceSimB(double num, double sum1, double sum2) {
		return 2 * num / (sum1 + sum2);
	}
	
	private static double jaccardSimA(HashMap<String, Double> vec1 , HashMap<String, Double> vec2) {
		double num  = 0;
		double sum1 = 0;
		double sum2 = 0;
		
		if (vec1.size() > vec2.size()) {
			HashMap<String, Double> temp = vec1;
			vec1 = vec2;
			vec2 = temp;
		}
		
		Set<Entry<String, Double>> entrySet = vec1.entrySet();
		for (Entry<String, Double> entry : entrySet) {
			Double value = vec2.get(entry.getKey());
			num += entry.getValue() *(value == null ? 0 : value);
		}
		
		Collection<Double> values = vec1.values();
		for (Double value : values) {
			sum1 += value;
		}
		
		values = vec2.values();
		for (Double value : values) {
			sum2 += value;
		}
		
		return jaccardSimB(num, sum1, sum2);
	}
	
	private static double jaccardSimB(double num, double sum1, double sum2) {
		return num / (sum1 + sum2 - num);
	}

}
