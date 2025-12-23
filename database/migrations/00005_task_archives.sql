-- depends: 00002_tasks
CREATE TABLE `task_archives` (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    task_id INT UNSIGNED NOT NULL,
    creator_id INT UNSIGNED NOT NULL,
    review_priority TINYINT UNSIGNED NOT NULL,
    pr_link VARCHAR(500) NOT NULL,
    has_been_reviewed_once TINYINT UNSIGNED NOT NULL,
    lines_of_code TINYINT UNSIGNED COMMENT 'this is a status',
    state TINYINT UNSIGNED NOT NULL,
    task_created_at DATETIME NOT NULL,
    task_approved_at DATETIME,
    PRIMARY KEY (`id`)
);