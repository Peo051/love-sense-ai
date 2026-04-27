-- Map Firebase Authentication users to existing internal UUID-scoped user data.

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS firebase_uid VARCHAR(128) UNIQUE;

CREATE INDEX IF NOT EXISTS idx_users_firebase_uid ON users(firebase_uid);

COMMENT ON COLUMN users.firebase_uid IS 'Firebase Authentication uid mapped to the internal user id.';
