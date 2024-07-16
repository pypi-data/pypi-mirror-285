#!/bin/bash
# usage: sudo rag/start_all.sh

sudo docker run -d -p 6333:6333 -v $"`pwd`"/ztmp/.asearch/qdrant_storage:/qdrant/storage:z qdrant/qdrant
echo "started qdrant"
sudo /opt/neo4j/bin/neo4j restart
echo "started neo4j"