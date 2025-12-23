-- depends: 00002_tasks
CREATE TABLE `task_reviewers` (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id INT UNSIGNED NOT NULL,
    task_id INT UNSIGNED NOT NULL,
    CONSTRAINT `uc_taskreviewers_userid_taskid`
    UNIQUE (`user_id`, `task_id`),
    PRIMARY KEY (`id`)
);

CREATE INDEX `idx_taskreviewers_taskid`
ON `task_reviewers` (`task_id`);
