SELECT messages.*, users.id, users.first_name, users.last_name, user2.id, user2.first_name, user2.last_name
FROM messages
JOIN users
ON users.id = messages.from_id
JOIN users AS user2
ON user2.id = messages.to_id;

SELECT messages.from_id, users.first_name, messages.to_id, user2.first_name, messages.message, messages.created_at 
FROM messages
JOIN users
ON users.id = messages.from_id
JOIN users AS user2
ON user2.id = messages.to_id
WHERE messages.to_id = 2;

SELECT COUNT(messages.to_id)
FROM messages
JOIN users
ON users.id = messages.from_id
JOIN users AS user2
ON user2.id = messages.to_id
WHERE messages.to_id = 2;


-- SELECT * FROM users;



