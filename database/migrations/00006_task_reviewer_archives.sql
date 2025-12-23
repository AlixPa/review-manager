-- depends: 00003_task_reviewers
CREATE TABLE `task_reviewer_archives` (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    task_reviewers_id INT UNSIGNED NOT NULL,
    user_id INT UNSIGNED NOT NULL,
    task_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (`id`)
);