-- SQLite
SELECT movieId, tag, COUNT(tag) as count 
FROM tags
GROUP BY movieId, tag 