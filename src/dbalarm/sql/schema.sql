-- This is the database counterpart of a configuration file
-- All configurations are stored here

CREATE TABLE IF NOT EXISTS config_t
(
    section        TEXT NOT NULL,  -- Configuration section
    property       TEXT NOT NULL,  -- Property name
    value          TEXT NOT NULL,  -- Property value

    PRIMARY KEY(section, property)
);

-- alarms detection table
CREATE TABLE IF NOT EXISTS alarms_t
(
    detected_at TIMESTAMP NOT NULL, -- timpestamp from log file
    notified_at TIMESTAMP,  		-- not null if succesfully emailed

    PRIMARY KEY(detected_at)
);