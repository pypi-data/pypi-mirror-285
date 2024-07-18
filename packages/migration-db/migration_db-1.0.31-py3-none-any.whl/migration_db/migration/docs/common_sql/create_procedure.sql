/*
-- 根据_separator拆分字符串，返回pos处的值
DROP FUNCTION IF EXISTS SPLIT_STR;
CREATE FUNCTION SPLIT_STR(
  x VARCHAR(255),
  _separator VARCHAR(12),
  pos INT
)
RETURNS VARCHAR(255)
RETURN REPLACE(SUBSTRING(SUBSTRING_INDEX(x, _separator, pos), LENGTH(SUBSTRING_INDEX(x, _separator, pos - 1)) + 1), _separator, '');

DROP FUNCTION IF EXISTS COUNT_STR_SEPARATOR;
CREATE FUNCTION COUNT_STR_SEPARATOR(
  x VARCHAR(255),
  _separator VARCHAR(12)
)
RETURNS INT
RETURN LENGTH(x) - LENGTH(REPLACE(x, _separator, ""));
*/


DROP PROCEDURE IF EXISTS REPLACE_STR;
DELIMITER //
CREATE PROCEDURE REPLACE_STR(
		IN `table_name` VARCHAR(200),
		IN `field_name` VARCHAR(200),
		IN `pre_value` VARCHAR(20),
		IN `cur_value` VARCHAR(20),
		IN `_separator` VARCHAR(20),
		IN `pos` INT)
BEGIN
    DECLARE cnt INT DEFAULT 0;
    DECLARE i INT DEFAULT 0;
    DECLARE fieldValue VARCHAR(200);
    DECLARE splitFieldValue VARCHAR(200);
    DECLARE countFieldValueSeparator INT;
	SET @queryStmt = CONCAT("SELECT COUNT(1) INTO @cnt FROM ", table_name);
	PREPARE stmt FROM @queryStmt;
	EXECUTE stmt;
	DEALLOCATE PREPARE stmt;
	SET cnt = @cnt;
    WHILE i<= cnt DO
		SET @stmtStr = CONCAT("SELECT ", field_name, " INTO @fieldValue FROM ", table_name, " LIMIT ", i, ",1");
		PREPARE stmt FROM @stmtStr;
		EXECUTE stmt;
		DEALLOCATE PREPARE stmt;
		SET fieldValue = @fieldValue;
--        SET splitFieldValue = SPLIT_STR(fieldValue, _separator, pos);
--        SET countFieldValueSeparator = COUNT_STR_SEPARATOR(fieldValue, _separator);
        SET splitFieldValue = REPLACE(SUBSTRING(SUBSTRING_INDEX(fieldValue, _separator, pos), LENGTH(SUBSTRING_INDEX(fieldValue, _separator, pos - 1)) + 1), _separator, '');
        SET countFieldValueSeparator = LENGTH(fieldValue) - LENGTH(REPLACE(fieldValue, _separator, ""));
		IF splitFieldValue = pre_value THEN
			SET @newFieldValue = CONCAT(SUBSTRING_INDEX(fieldValue, _separator, pos - 1), "-", cur_value, "-", SUBSTRING_INDEX(fieldValue, _separator, -(countFieldValueSeparator + 1 -pos)));
			SET @stmtStr = CONCAT("UPDATE ", table_name, " SET ", field_name, "='", @newFieldValue, "' WHERE ", field_name, "='", fieldValue, "';");
			PREPARE stmt FROM @stmtStr;
			EXECUTE stmt;
			DEALLOCATE PREPARE stmt;
		END IF;
        SET i = i + 1;
    END WHILE;
END;
//
DELIMITER ;