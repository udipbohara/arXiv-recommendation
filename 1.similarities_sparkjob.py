#!/usr/bin/env python
# coding: utf-8

import pyspark
import pyspark.sql.functions as F
from pyspark.sql.types import *
from pyspark.sql.functions import *
import json 
from pyspark.ml.feature import RegexTokenizer, NGram, HashingTF, MinHashLSH,StopWordsRemover, Normalizer,Tokenizer,IDF
import regex as re 
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.sql.types import DoubleType
from pyspark.ml import Pipeline


sc = pyspark.SparkContext.getOrCreate()

metadata = sc.textFile('gs://input_spark/metadata.json')
records=metadata.map(lambda x:json.loads(x))

category_map = {'astro-ph': 'Astrophysics',
                'astro-ph.CO': 'Cosmology and Nongalactic Astrophysics',
                'astro-ph.EP': 'Earth and Planetary Astrophysics',
                'astro-ph.GA': 'Astrophysics of Galaxies',
                'astro-ph.HE': 'High Energy Astrophysical Phenomena',
                'astro-ph.IM': 'Instrumentation and Methods for Astrophysics',
                'astro-ph.SR': 'Solar and Stellar Astrophysics',
                'cond-mat.dis-nn': 'Disordered Systems and Neural Networks',
                'cond-mat.mes-hall': 'Mesoscale and Nanoscale Physics',
                'cond-mat.mtrl-sci': 'Materials Science',
                'cond-mat.other': 'Other Condensed Matter',
                'cond-mat.quant-gas': 'Quantum Gases',
                'cond-mat.soft': 'Soft Condensed Matter',
                'cond-mat.stat-mech': 'Statistical Mechanics',
                'cond-mat.str-el': 'Strongly Correlated Electrons',
                'cond-mat.supr-con': 'Superconductivity',
                'cs.AI': 'Artificial Intelligence',
                'cs.AR': 'Hardware Architecture',
                'cs.CC': 'Computational Complexity',
                'cs.CE': 'Computational Engineering, Finance, and Science',
                'cs.CG': 'Computational Geometry',
                'cs.CL': 'Computation and Language',
                'cs.CR': 'Cryptography and Security',
                'cs.CV': 'Computer Vision and Pattern Recognition',
                'cs.CY': 'Computers and Society',
                'cs.DB': 'Databases',
                'cs.DC': 'Distributed, Parallel, and Cluster Computing',
                'cs.DL': 'Digital Libraries',
                'cs.DM': 'Discrete Mathematics',
                'cs.DS': 'Data Structures and Algorithms',
                'cs.ET': 'Emerging Technologies',
                'cs.FL': 'Formal Languages and Automata Theory',
                'cs.GL': 'General Literature',
                'cs.GR': 'Graphics',
                'cs.GT': 'Computer Science and Game Theory',
                'cs.HC': 'Human-Computer Interaction',
                'cs.IR': 'Information Retrieval',
                'cs.IT': 'Information Theory',
                'cs.LG': 'Machine Learning',
                'cs.LO': 'Logic in Computer Science',
                'cs.MA': 'Multiagent Systems',
                'cs.MM': 'Multimedia',
                'cs.MS': 'Mathematical Software',
                'cs.NA': 'Numerical Analysis',
                'cs.NE': 'Neural and Evolutionary Computing',
                'cs.NI': 'Networking and Internet Architecture',
                'cs.OH': 'Other Computer Science',
                'cs.OS': 'Operating Systems',
                'cs.PF': 'Performance',
                'cs.PL': 'Programming Languages',
                'cs.RO': 'Robotics',
                'cs.SC': 'Symbolic Computation',
                'cs.SD': 'Sound',
                'cs.SE': 'Software Engineering',
                'cs.SI': 'Social and Information Networks',
                'cs.SY': 'Systems and Control',
                'econ.EM': 'Econometrics',
                'eess.AS': 'Audio and Speech Processing',
                'eess.IV': 'Image and Video Processing',
                'eess.SP': 'Signal Processing',
                'gr-qc': 'General Relativity and Quantum Cosmology',
                'hep-ex': 'High Energy Physics - Experiment',
                'hep-lat': 'High Energy Physics - Lattice',
                'hep-ph': 'High Energy Physics - Phenomenology',
                'hep-th': 'High Energy Physics - Theory',
                'math.AC': 'Commutative Algebra',
                'math.AG': 'Algebraic Geometry',
                'math.AP': 'Analysis of PDEs',
                'math.AT': 'Algebraic Topology',
                'math.CA': 'Classical Analysis and ODEs',
                'math.CO': 'Combinatorics',
                'math.CT': 'Category Theory',
                'math.CV': 'Complex Variables',
                'math.DG': 'Differential Geometry',
                'math.DS': 'Dynamical Systems',
                'math.FA': 'Functional Analysis',
                'math.GM': 'General Mathematics',
                'math.GN': 'General Topology',
                'math.GR': 'Group Theory',
                'math.GT': 'Geometric Topology',
                'math.HO': 'History and Overview',
                'math.IT': 'Information Theory',
                'math.KT': 'K-Theory and Homology',
                'math.LO': 'Logic',
                'math.MG': 'Metric Geometry',
                'math.MP': 'Mathematical Physics',
                'math.NA': 'Numerical Analysis',
                'math.NT': 'Number Theory',
                'math.OA': 'Operator Algebras',
                'math.OC': 'Optimization and Control',
                'math.PR': 'Probability',
                'math.QA': 'Quantum Algebra',
                'math.RA': 'Rings and Algebras',
                'math.RT': 'Representation Theory',
                'math.SG': 'Symplectic Geometry',
                'math.SP': 'Spectral Theory',
                'math.ST': 'Statistics Theory',
                'math-ph': 'Mathematical Physics',
                'nlin.AO': 'Adaptation and Self-Organizing Systems',
                'nlin.CD': 'Chaotic Dynamics',
                'nlin.CG': 'Cellular Automata and Lattice Gases',
                'nlin.PS': 'Pattern Formation and Solitons',
                'nlin.SI': 'Exactly Solvable and Integrable Systems',
                'nucl-ex': 'Nuclear Experiment',
                'nucl-th': 'Nuclear Theory',
                'physics.acc-ph': 'Accelerator Physics',
                'physics.ao-ph': 'Atmospheric and Oceanic Physics',
                'physics.app-ph': 'Applied Physics',
                'physics.atm-clus': 'Atomic and Molecular Clusters',
                'physics.atom-ph': 'Atomic Physics',
                'physics.bio-ph': 'Biological Physics',
                'physics.chem-ph': 'Chemical Physics',
                'physics.class-ph': 'Classical Physics',
                'physics.comp-ph': 'Computational Physics',
                'physics.data-an': 'Data Analysis, Statistics and Probability',
                'physics.ed-ph': 'Physics Education',
                'physics.flu-dyn': 'Fluid Dynamics',
                'physics.gen-ph': 'General Physics',
                'physics.geo-ph': 'Geophysics',
                'physics.hist-ph': 'History and Philosophy of Physics',
                'physics.ins-det': 'Instrumentation and Detectors',
                'physics.med-ph': 'Medical Physics',
                'physics.optics': 'Optics',
                'physics.plasm-ph': 'Plasma Physics',
                'physics.pop-ph': 'Popular Physics',
                'physics.soc-ph': 'Physics and Society',
                'physics.space-ph': 'Space Physics',
                'q-bio.BM': 'Biomolecules',
                'q-bio.CB': 'Cell Behavior',
                'q-bio.GN': 'Genomics',
                'q-bio.MN': 'Molecular Networks',
                'q-bio.NC': 'Neurons and Cognition',
                'q-bio.OT': 'Other Quantitative Biology',
                'q-bio.PE': 'Populations and Evolution',
                'q-bio.QM': 'Quantitative Methods',
                'q-bio.SC': 'Subcellular Processes',
                'q-bio.TO': 'Tissues and Organs',
                'q-fin.CP': 'Computational Finance',
                'q-fin.EC': 'Economics',
                'q-fin.GN': 'General Finance',
                'q-fin.MF': 'Mathematical Finance',
                'q-fin.PM': 'Portfolio Management',
                'q-fin.PR': 'Pricing of Securities',
                'q-fin.RM': 'Risk Management',
                'q-fin.ST': 'Statistical Finance',
                'q-fin.TR': 'Trading and Market Microstructure',
                'quant-ph': 'Quantum Physics',
                'stat.AP': 'Applications',
                'stat.CO': 'Computation',
                'stat.ME': 'Methodology',
                'stat.ML': 'Machine Learning',
                'stat.OT': 'Other Statistics',
                'stat.TH': 'Statistics Theory'}

list_of_interest = ('cs.LG','cs.AI','cs.CV')
keys = list(category_map.keys())
categories = [i for i in keys if i.startswith(list_of_interest)]

docs = (records.filter(lambda x:any(ele in x['categories'] for ele in categories)==True))
get_metadata = lambda x: {'id': x['id'].replace('\n',' '),
                  'title': x['title'].replace('\n',' '),
                  'authors': x['authors'].replace('\n',' '),
                  'authors_parsed' : x['authors_parsed'],
                  'category':x['categories'].replace('\n',' '),
                  'abstract':x['abstract'].replace('\n',' '),
                 'version':x['versions'][-1]['created'].replace('\n',' '),
                 'year':x['versions'][-1]["created"].split(" ")[3]}

spark = SparkSession(sc)
filterddocs = docs.map(get_metadata)
df = filterddocs.toDF()
df = df.filter(df.year>2018)

filter_columns= lambda x: {'id': x['id'].replace('\n',' '),
                  'abstract':x['abstract'].replace('\n',' ')}


rdd = df.rdd.map(filter_columns)

def clean_text(c):
  c = lower(c)
  c = regexp_replace(c, "^rt ", "")
  c = regexp_replace(c, "(https?\://)\S+", "")
  c = regexp_replace(c, "[^a-zA-Z0-9\\s]", "")
  return c

df = rdd.toDF(["abstract", "ID"])
clean_text_df = df.select('ID',clean_text(col("abstract")).alias("abstract"))
clean_text_df = clean_text_df.withColumn('abstract', trim(clean_text_df.abstract))orm(tf)
#tokenize words
tokenizer = Tokenizer(inputCol="abstract", outputCol="words")
stage_1 = StringIndexer(inputCol= 'category_1', outputCol= 'category_1_index')
# remove stop words
remover = StopWordsRemover(inputCol="words", outputCol="filtered")
# define stage 3 :tf and idf
hashingTF = HashingTF(inputCol="words", outputCol="tf")
idf = IDF(inputCol="tf", outputCol="feature").fit(tf)
#compute L2 norm
normalizer = Normalizer(inputCol="feature", outputCol="norm")
pipeline = Pipeline(stages=[tokenizer, remover, hashingTF,normalizer])
# fit the pipeline for the trainind data
model = pipeline.fit(clean_text_df)
# transform the data
data = model.transform(clean_text_df)
dot_udf = F.udf(lambda x,y: float(x.dot(y)) if float(x.dot(y)) > 0.5 else 0, DoubleType())

result2 = data.alias("i").join(data.alias("j"), F.col("i.ID") < F.col("j.ID")).select(
        F.col("i.ID").alias("i"), 
        F.col("j.ID").alias("j"), 
        dot_udf("i.norm", "j.norm").alias("dot"))\
    .sort("i", "j")\
    .na.drop(subset=["dot"])

result2.write.parquet('gs://output_spark/calculated_similarities.parquet')



