
// 1. Load Dataset
//Load Dataset
CALL apoc.periodic.iterate(
"CALL apoc.load.json('https://raw.githubusercontent.com/udipbohara/arXiv-recommendation/master/data.json') YIELD value",

"MERGE (paper1:Paper{id:value.id})
ON CREATE SET paper1.title = value.title,
              paper1.date = date(value.date)

MERGE(topic:Topic{name:value.Dominant_Topic}) MERGE (paper1)-[:PART_OF]->(topic)
MERGE(submitted_by:Submitter{name:value.submitter}) MERGE (paper1)-[:SUBMITTED_BY]-(submitted_by)  

FOREACH (authorName IN value.authors | MERGE (author:Author{name:authorName}) MERGE (author)-[:WROTE]->(paper1))
FOREACH (categoryName IN value.category | MERGE (category:Category{name:categoryName}) MERGE (paper1)-[:BELONGS_TO]->(category))
FOREACH (similarPaper IN value.similar_to | MERGE (paper2:Paper{id:similarPaper}) MERGE (paper1)-[:SIMILAR_TO]-(paper2))
FOREACH (citedPaper IN value.cited_by | MERGE (paper2:Paper{id:citedPaper}) MERGE (paper1)-[:CITED_BY]->(paper2))",
{batchSize:1000, iterateList:true, parallel:true, retries:3})

// 2. Categories_Demo
//Categories_Demo
MATCH p=()-[r:BELONGS_TO]->() RETURN p LIMIT 100


//3. Topic Demo
MATCH p=()-[r:PART_OF]->() RETURN p LIMIT 200

//4.1 Author most submitted count with papers
//return author who has submitted the most number of papers.
MATCH (p)-[w:SUBMITTED_BY]->(submitter)
RETURN submitter.name, COLLECT(p.id) as Paper_id, count(DISTINCT w) AS num
ORDER BY num DESC 
LIMIT 10


// 4.2 Simple recommendation Query
//Query to get all papers that have a title that are similar to it 'Dynamic Sparse Graph for Efficient Deep Learning' and belong to the same topic.

MATCH path =(t1:Topic)<-[:PART_OF]-(p{title:'Dynamic Sparse Graph for Efficient Deep Learning'})-[:SIMILAR_TO]-(p2)-[:PART_OF]->(t2:Topic)
WHERE t1.name = t2.name  
RETURN path

//5. Simple Match Query (Graph)
MATCH path=(p:Paper)-[:SIMILAR_TO]-(p2)-[:BELONGS_TO]->(TOPIC)
WHERE p.title CONTAINS 'Object Detection'
RETURN path
LIMIT 70

// 7. A more complex Query (Graph)
// Where the similar paper was written after january, and show authors as well. 

MATCH path=(a:Author)-[:WROTE]->(p:Paper)-[:SIMILAR_TO]-(p2)-[:BELONGS_TO]->(Category)
MATCH path2=(p)-[:PART_OF]-()
WHERE p.title CONTAINS 'Object Detection' AND  p2.date > date({year:2019,month:1})
RETURN path,path2

// 8. A more complex Query (TABLE) / PRACTICAL 
// Returning All Papers that are similar to any paper that has 'Object Detection' in it sorted by Date (descending), with cited_by
MATCH path=(a:Author)-[:WROTE]->(p:Paper)-[:SIMILAR_TO]-(p2)-[:BELONGS_TO]->(Category)
MATCH path2=(p2)-[:PART_OF]-(Topic)
MATCH (p2)-[:CITED_BY]-(paper3)
WHERE p.title CONTAINS 'Object Detection' AND  p2.date > date({year:2019,month:1})
RETURN DISTINCT p2.title as Similar_Papers, collect(DISTINCT a.name) as Authors, count(DISTINCT paper3) as cited_by, p2.date as Published_Date, Topic.name as Topic, collect(DISTINCT Category.name) as Category
ORDER BY Published_Date DESC 