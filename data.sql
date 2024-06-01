ALTER TABLE post
DROP CONSTRAINT post_topic_fk;

ALTER TABLE post
DROP CONSTRAINT post_user_fk;

ALTER TABLE comment
DROP CONSTRAINT comment_user_fk;

ALTER TABLE comment
DROP CONSTRAINT comment_post_fk;

ALTER TABLE comment
DROP CONSTRAINT comment_comment_fk;

ALTER TABLE liked
DROP CONSTRAINT liked_user_fk;

ALTER TABLE liked
DROP CONSTRAINT liked_post_fk;

ALTER TABLE liked
DROP CONSTRAINT liked_comment_fk;

ALTER TABLE saved
DROP CONSTRAINT saved_user_fk;

ALTER TABLE saved
DROP CONSTRAINT saved_post_fk;

DROP TABLE user;

DROP TABLE topic;

DROP TABLE post;

DROP TABLE comment;

DROP TABLE liked;

DROP TABLE saved;

CREATE TABlE user(
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255),
    phone_number VARCHAR(255),
    password VARCHAR(1000),
    username VARCHAR(100),
    bio VARCHAR(1000),
    pfp VARCHAR(1000),
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE topic(
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    description VARCHAR(1000),
    logo VARCHAR(1000),
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE post(
    id INT PRIMARY KEY AUTO_INCREMENT,
    topic_id INT,
    user_id INT,
    title VARCHAR(100),
    content VARCHAR(10000),
    image VARCHAR(1000),
    like_count INT,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comment(
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    post_id INT,
    parent_id INT,
    has_parent BOOLEAN,
    content VARCHAR(10000),
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE liked(
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    post_id INT,
    comment_id INT,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE saved(
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    post_id INT,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE post
ADD CONSTRAINT post_topic_fk
FOREIGN KEY(topic_id) REFERENCES topic(id)
 ON DELETE SET NULL;

ALTER TABLE post
ADD CONSTRAINT post_user_fk
FOREIGN KEY(user_id) REFERENCES user(id)
 ON DELETE SET NULL;

ALTER TABLE comment
ADD CONSTRAINT comment_user_fk
FOREIGN KEY(user_id) REFERENCES user(id)
 ON DELETE SET NULL;


ALTER TABLE comment
ADD CONSTRAINT comment_post_fk
FOREIGN KEY(post_id) REFERENCES post(id)
 ON DELETE SET NULL;

ALTER TABLE comment
ADD CONSTRAINT comment_comment_fk
FOREIGN KEY(parent_id) REFERENCES comment(id)
 ON DELETE SET NULL;

ALTER TABLE liked
ADD CONSTRAINT liked_user_fk
FOREIGN KEY(user_id) REFERENCES user(id)
 ON DELETE SET NULL;


ALTER TABLE liked
ADD CONSTRAINT liked_post_fk
FOREIGN KEY(post_id) REFERENCES post(id)
 ON DELETE SET NULL;

ALTER TABLE liked
ADD CONSTRAINT liked_comment_fk
FOREIGN KEY(comment_id) REFERENCES comment(id)
 ON DELETE SET NULL;

ALTER TABLE saved
ADD CONSTRAINT saved_user_fk
FOREIGN KEY(user_id) REFERENCES user(id)
 ON DELETE SET NULL;

ALTER TABLE saved
ADD CONSTRAINT saved_post_fk
FOREIGN KEY(post_id) REFERENCES post(id)
 ON DELETE SET NULL;