-- create the tables here
-- enum
CREATE TYPE visibility_type AS ENUM ('Public', 'Private');

-- NANDANA
CREATE TABLE Student (
    student_id SERIAL PRIMARY KEY  ,
    full_name VARCHAR(100) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    profile_pic VARCHAR(255),
    bio TEXT,
    dob DATE,
    institution VARCHAR(150),
    location VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ANGEL
CREATE TABLE Project (
    project_id SERIAL PRIMARY KEY ,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    github_url VARCHAR(255),
    demo_url VARCHAR(255),
    visibility visibility_type DEFAULT 'Public',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Student(student_id)
    ON DELETE CASCADE
);

---SANA
CREATE TABLE Post (
    post_id SERIAL PRIMARY KEY ,
    user_id INT NOT NULL,
    caption TEXT,
    image_url VARCHAR(255),
    post_type VARCHAR(50),
    link_url VARCHAR(255),
    location VARCHAR(100),
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES Student(student_id)
        ON DELETE CASCADE
);

-- NAVNEETH
CREATE TABLE IF NOT EXISTS Skill (
    skill_id SERIAL PRIMARY KEY  ,
    skill_name VARCHAR(200) NOT NULL,
    skill_category VARCHAR(200),
    description VARCHAR(200)
);


-- ATHUL
CREATE TABLE IF NOT EXISTS UserSkill (
    user_id INT NOT NULL,
    skill_id INT NOT NULL,
    PRIMARY KEY (user_id, skill_id),
    FOREIGN KEY (user_id) REFERENCES Student(student_id)
        ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES Skill(skill_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS UserFollows (
    follower_id INT NOT NULL,
    following_id INT NOT NULL,
    PRIMARY KEY (follower_id, following_id),
    FOREIGN KEY (follower_id) REFERENCES Student(student_id)
        ON DELETE CASCADE,
    FOREIGN KEY (following_id) REFERENCES Student(student_id)
        ON DELETE CASCADE
);