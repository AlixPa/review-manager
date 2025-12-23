-- depends:
CREATE TABLE `users` (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    public_id CHAR(36) NOT NULL COMMENT 'public id is uuid for privacy',
    email VARCHAR(255),
    google_sub VARCHAR(255),
    user_name VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
);

CREATE INDEX `idx_users_googlesub`
ON `users` (`google_sub`);

CREATE INDEX `idx_users_publicid`
ON `users` (`public_id`);