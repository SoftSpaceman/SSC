
--gpdata2. database

--gp_file. table 

--gp_file_historical. table 






-- Gives the entier table but without comment 
SELECT id, norad_cat_id, modification_timestamp, creation_date, epoch, originator, object_name, object_id, center_name, ref_frame, time_system, mean_element_theory, mean_motion, eccentricity, inclination, ra_of_asc_node, arg_of_pericenter, mean_anomaly, ephemeris_type, classification_type, element_set_no, rev_at_epoch, bstar, mean_motion_dot, mean_motion_ddot, semimajor_axis, "period", apoapsis, periapsis, object_type, rcs_size, country_code, launch_date, site, decay_date, file, gp_id, tle_line0, tle_line1, tle_line2
FROM public.gp_file;
	

--Gives all the rows count 
SELECT COUNT(*)
FROM gp_file;


-- gives all the rows with uniqe NORAD. 
SELECT
   COUNT(*) AS total_rows,
   COUNT(DISTINCT norad_cat_id) AS unique_rows
FROM
   public.gp_file;


-- This query will return all columns for the row(s) where the NORAD_CAT_ID matches the specified value.
SELECT *
FROM gp_file
WHERE NORAD_CAT_ID = your_desired_NORAD_CAT_ID;



-- This query shows how many rows have the same NORAD_CAT_ID.
SELECT NORAD_CAT_ID, COUNT(*)
FROM gp
GROUP BY NORAD_CAT_ID
HAVING COUNT(*) > 1;




-- This query will count the number of NORAD_CAT_ID for each modification_timestamp, grouping them by date. 
-- It orders the result by modification_date. 
-- Adjust the modification_timestamp::date according to your database's syntax for extracting the date part from a timestamp if needed.

SELECT modification_timestamp::date AS modification_date, COUNT(NORAD_CAT_ID) AS norad_count
FROM gp_file
GROUP BY modification_timestamp::date
ORDER BY modification_date;




-- This query uses the DATE_TRUNC function to truncate the modification_timestamp to the minute precision. 
-- It then counts the NORAD_CAT_ID for each truncated timestamp, effectively grouping by both date and time at minute granularity. 
-- Adjust the 'minute' parameter in DATE_TRUNC if you need a different level of granularity (e.g., 'second', 'hour', etc.).
SELECT 
    DATE_TRUNC('minute', modification_timestamp) AS modification_time,
    COUNT(NORAD_CAT_ID) AS norad_count
FROM gp_file
GROUP BY DATE_TRUNC('minute', modification_timestamp)
ORDER BY modification_time;






-- This query will return all columns for the row where the id matches the specified value.
SELECT NORAD_CAT_ID, modification_timestamp, COUNT(*)
FROM gp_file
GROUP BY NORAD_CAT_ID, modification_timestamp
HAVING COUNT(*) > 1;

-- This query will return the total count of rows that have duplicates across all columns in the gp_file table.
SELECT *
FROM gp_file
GROUP BY id, NORAD_CAT_ID, modification_timestamp, CCSDS_OMM_VERS, COMMENT, CREATION_DATE, EPOCH, ORIGINATOR, OBJECT_NAME, OBJECT_ID, CENTER_NAME, REF_FRAME, TIME_SYSTEM, MEAN_ELEMENT_THEORY, MEAN_MOTION, ECCENTRICITY, INCLINATION, RA_OF_ASC_NODE, ARG_OF_PERICENTER, MEAN_ANOMALY, EPHEMERIS_TYPE, CLASSIFICATION_TYPE, ELEMENT_SET_NO, REV_AT_EPOCH, BSTAR, MEAN_MOTION_DOT, MEAN_MOTION_DDOT, SEMIMAJOR_AXIS, PERIOD, APOAPSIS, PERIAPSIS, OBJECT_TYPE, RCS_SIZE, COUNTRY_CODE, LAUNCH_DATE, SITE, DECAY_DATE, FILE, GP_ID, TLE_LINE0, TLE_LINE1, TLE_LINE2
HAVING COUNT(*) > 1;
