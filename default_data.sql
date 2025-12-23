INSERT INTO users (id, public_id, user_name)
VALUES
      (1, '2f6a4b2a-6e3a-4c2f-9d2e-7a4c6f3d1e8b', 'Bob'),
      (2, '9b1f0c5e-8a3d-4e7a-b2c4-1f6e9d3a7c0b', 'Vanessa'),
      (3, '4c8e2f1d-7a6b-4b0c-9e3f-5d1a2c6b8e7f', 'Melon Pan');

INSERT INTO tasks (id, creator_id, review_priority, lines_of_code, state, created_at, approved_at, has_been_reviewed_once, pr_link)
VALUES
      (1, 1, 1, 2, 1, '2025-12-10 00:00:00', NULL, 0, 'https://github.com/fastapi/fastapi/pull/14589'),
      (2, 1, 2, 3, 1, '2025-12-11 00:00:00', NULL, 0, 'https://github.com/fastapi/fastapi/pull/14588'),
      (3, 2, 2, 1, 3, '2025-12-12 00:00:00', '2025-12-13 00:10:00', 1, 'https://github.com/fastapi/fastapi/pull/14587'),
      (4, 3, 3, 4, 1, '2025-12-12 00:00:00', NULL, 0, 'https://github.com/fastapi/fastapi/pull/14586');

INSERT INTO task_reviewers (user_id, task_id)
VALUES
      (2, 1),
      (3, 2),
      (1, 3),
      (3, 3),
      (1, 4),
      (2, 4);

INSERT INTO rewards (user_id, task_id, points, pr_link, was_quick_review, created_at, creator_public_id, creator_user_name, review_priority, lines_of_code)
VALUES
      (1, 3, 15, 'https://github.com/fastapi/fastapi/pull/14587', 0, '2025-12-13 00:00:00', '9b1f0c5e-8a3d-4e7a-b2c4-1f6e9d3a7c0b', 'Vanessa', 2, 1),
      (3, 3, 10, 'https://github.com/fastapi/fastapi/pull/14587', 1, '2025-12-13 00:10:00', '9b1f0c5e-8a3d-4e7a-b2c4-1f6e9d3a7c0b', 'Vanessa', 2, 1);
