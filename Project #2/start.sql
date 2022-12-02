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
    answer VARCHAR(4096) NOT NULL DEFAULT 'Нет текста',
    attachment VARCHAR(64) DEFAULT ''
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
    status VARCHAR(32) DEFAULT 'new',
    FOREIGN KEY (city_id) REFERENCES cities(id),
    FOREIGN KEY (direction_id) REFERENCES directions(id)
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

INSERT INTO buttons ( type,title, answer) VALUES
    ('start','Доброе пожаловать в Дом.РФ','Привет!
```ДОМ.РФ – это финансовый институт развития в жилищной сфере России. Вместе мы создаем условия для комфортной жизни россиян, увеличивая доступность жилья и создавая проекты городского развития.
Мы познакомим тебя с компанией ДОМ.РФ, расскажем о стажировках и поможем на них записаться, а также ответим на все интересующие вопросы. Жми скорее, чтобы стать частью нашей большой команды! Создадим комфортное будущее вместе!```'),
    ('contacts','Контакты!','`Получить больше информация о стажировках, познакомиться с сотрудниками и партнерами, а также узнать подробности жизни нашей команды — можно здесь:`
**Группа в ВК:** https://vk.com/domrf
**Канал на YouYube:** https://www.youtube.com/channel/UCgUs7ebuhG19V4yxDNe_2GQ
**Канал в Telegtam:** https://t.me/domrf_life
**Телефон**
`8 (495) 775-47-40`
**Консультационный центр**
`8 (800) 775-11-22`'),
    ('faq','Что такое ДОМ.РФ?','ДОМ.РФ — крупнейший финансовый институт, который 25 лет занимается развитием жилищной сферы в России.
Мы объединяем направления, которые способствуют прогрессу рынка недвижимости и поддерживают его участников — граждан, девелоперов, финансовые организации. С нашей помощью ипотека стала доступной, аренда — цивилизованной, а окружающая среда — благоустроенной.
'),('form','Стажировки','Подать заявку на стражировку'),('ticket','Связаться с нами','Тут будет текст...'),('faq_main','Список вопросов:','Много-много вопросов')
    ON CONFLICT DO NOTHING;

INSERT INTO users (id, username,first_name, last_name, hash, photo_code, role_id) VALUES
    (1469793383, 'halisl', 'Данила','Гинда', 'hash_to_update', 'P9vhtP8sHGpmM_TRgpQdYWYuQCv5ZUSN10s0EvMIkKY', 1),
    (5663523522, 'house_rf_bot', 'Технический','Аккаунт', '69676bc6c46eaec7d943482f77fa73e6fba22015a897192376c45f7e3fcec41f', '', 5)
    ON CONFLICT  DO NOTHING ;

CREATE TABLE IF NOT EXISTS bot_uses (
    user_id BIGINT PRIMARY KEY,
    date TIMESTAMP DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    user_name VARCHAR(256),
    user_img VARCHAR(256),
    status VARCHAR(32) DEFAULT 'new',
    admin_id BIGINT,
    admin_name VARCHAR(256),
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    answer_date TIMESTAMP DEFAULT NULL,
    close_date TIMESTAMP DEFAULT NULL
);

CREATE TABLE ticket_messages (
    id SERIAL PRIMARY KEY,
    author_id BIGINT,
    text VARCHAR(4096),
    ticket BIGINT,
    FOREIGN KEY (ticket) REFERENCES tickets(id)
)

