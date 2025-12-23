-- depends: 00002_tasks

CREATE TABLE `rewards` (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id INT UNSIGNED NOT NULL,
    task_id INT UNSIGNED NOT NULL,
    pr_link VARCHAR(500) NOT NULL,
    creator_public_id CHAR(36) NOT NULL COMMENT 'public id is uuid for privacy',
    creator_user_name VARCHAR(255) NOT NULL,
    review_priority TINYINT UNSIGNED NOT NULL,
    lines_of_code TINYINT UNSIGNED COMMENT 'this is a status',
    was_quick_review TINYINT NOT NULL,
    points INT UNSIGNED NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
);

CREATE INDEX `idx_rewards_userid_taskid`
ON `rewards` (`user_id`, `task_id`);

CREATE INDEX `idx_rewards_createdat`
ON `rewards` (`created_at`);