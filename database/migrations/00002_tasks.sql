-- depends: 00001_users
CREATE TABLE `tasks` (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    creator_id INT UNSIGNED NOT NULL,
    review_priority TINYINT UNSIGNED NOT NULL,
    pr_link VARCHAR(500) NOT NULL,
    has_been_reviewed_once TINYINT UNSIGNED NOT NULL DEFAULT 0,
    lines_of_code TINYINT UNSIGNED COMMENT 'this is a status',
    state TINYINT UNSIGNED NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    approved_at DATETIME,
    CONSTRAINT `uc_tasks_prlink`
    UNIQUE (`pr_link`),
    PRIMARY KEY (`id`)
);

CREATE INDEX `idx_tasks_id_state`
ON `tasks` (`id`, `state`);

CREATE INDEX `idx_tasks_creatorid_state`
ON `tasks` (`creator_id`, `state`);