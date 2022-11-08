CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(64),
    description VARCHAR(256)
);

CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,
    username VARCHAR(128),
    first_name VARCHAR(64),
    last_name VARCHAR(64) DEFAULT '',
    hash VARCHAR(64),
    photo_code VARCHAR(64),
    role_id INT DEFAULT 6,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

CREATE TABLE IF NOT EXISTS buttons (
    id SERIAL PRIMARY KEY,
    type VARCHAR(16) NOT NULL DEFAULT 'faq',
    title VARCHAR(256) NOT NULL DEFAULT 'Нет названия',
    answer VARCHAR(4096) NOT NULL DEFAULT 'Нет текста'
);
CREATE TABLE IF NOT EXISTS cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS directions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS forms (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    name VARCHAR(64),
    surname VARCHAR(64),
    father_name VARCHAR(64),
    city_id INT,
    direction_id INT,
    birthday_date date,
    email VARCHAR(256),
    cover_letter VARCHAR(2048),
    resume varchar(256),
    FOREIGN KEY (city_id) REFERENCES cities(id),
    FOREIGN KEY (direction_id) REFERENCES directions(id)
);
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    type varchar(32),
    title varchar(64),
    description varchar(2048)
);
INSERT INTO cities (title) VALUES ('Москва'),('Воронеж');
INSERT INTO directions (title) VALUES ('IT'),('Финансы'),('Анализ');

INSERT INTO roles ( title, description) VALUES
    ('Администратор','Тут будет описание этой роли'),
    ('BOT','Технический аккаунт!'),
    ('Саппорт','Тут будет описание этой роли'),
    ('Brand-Менеджер','Тут будет описание этой роли'),
    ('HR-Менеджер','Тут будет описание этой роли'),
    ('Пользователь','Тут будет описание этой роли')
    ON CONFLICT DO NOTHING;

INSERT INTO users (id, username,first_name, last_name, hash, photo_code, role_id) VALUES
    (1469793383, 'halisl', 'Данила','Гинда', 'hash_to_update', 'P9vhtP8sHGpmM_TRgpQdYWYuQCv5ZUSN10s0EvMIkKY', 1),
    (5663523522, 'house_rf_bot', 'Технический','Аккаунт', '69676bc6c46eaec7d943482f77fa73e6fba22015a897192376c45f7e3fcec41f', '', 5)
    ON CONFLICT  DO NOTHING ;