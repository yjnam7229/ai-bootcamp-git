/* ch07 예제 */

/* 예제7-1 */
INSERT INTO 부서
VALUES('A5', '마케팅부');

/* 예제7-2 */
INSERT INTO 제품
VALUES(91, '연어피클소스', NULL, 5000, 40);

/* 예제7-3 */
INSERT INTO 제품
VALUES(90, '연어핫소스', NULL, 4000, 50);

/* 예제7-4 */
INSERT INTO 사원(사원번호, 이름, 직위, 성별, 입사일)
VALUES('E20', '김사과', '수습사원', '남', curdate()),
	  ('E21', '박바나나', '수습사원', '여', curdate()),
      ('E22', '정오렌지', '수습사원', '여', curdate());

/* 예제7-5 */
UPDATE 사원
SET 이름 = '김레몬'
WHERE 사원번호 = 'E20';

/* 예제7-6 */
UPDATE 제품
SET 포장단위 = '200ml bottles'
WHERE 제품번호 = 91;

/* 예제7-7 */
UPDATE 제품
SET 단가 = 단가 * 1.1,
	재고 = 재고 - 10
WHERE 제품번호 = 91;

-- CF)
UPDATE 부서
SET 부서명 = '마케팅부'
WHERE 부서번호 = 'A5';

/* 예제7-8 */
DELETE FROM 제품
WHERE 제품번호 = 91;

/* 예제7-9 */
DELETE FROM 사원
ORDER BY 입사일 DESC
LIMIT 3;

/* 예제7-10 */
INSERT	INTO 제품(제품번호, 제품명, 단가, 재고)
VALUES(91, '연어피클핫소스', 6000, 50)
ON DUPLICATE KEY UPDATE 제품명 = '연어피클핫소스', 단가=6000, 재고 = 50;


/* 예제7-11 */
CREATE TABLE 고객주문요약(
	고객번호 CHAR(5) PRIMARY KEY,
    고객회사명  VARCHAR(50),
    주문건수  INT,
    최종주문일 DATE
);

INSERT INTO 고객주문요약
	SELECT 고객.고객번호, 고객회사명, COUNT(*), MAX(주문일)
    FROM 고객, 주문
    WHERE 고객.고객번호 = 주문.고객번호
    GROUP BY 고객.고객번호, 고객회사명;
    
SELECT * FROM 고객주문요약;


/* 예제7-12 */
UPDATE 제품
SET 단가 = ( SELECT *
             FROM (SELECT AVG(단가)
				   FROM 제품
                   WHERE 제품명 LIKE '%소스%') AS t)
WHERE 제품번호 = 91;

/* 예제7-13 */
UPDATE 고객, (SELECT DISTINCT 고객번호 FROM 주문) AS 주문고객
SET 마일리지 = 마일리지 * 1.1
WHERE 고객.고객번호 IN (주문고객.고객번호);

-- 결과 확인
SELECT * FROM 고객
WHERE 고객번호 IN (SELECT DISTINCT 고객번호 FROM 주문);

/*예제7-14*/
/*ANSI SQL*/
UPDATE 고객
INNER JOIN 마일리지등급
ON 마일리지 BETWEEN 하한마일리지 AND 상한마일리지
SET 마일리지 = 마일리지 + 1000
WHERE 등급명 = 'S';

/*Non-ANSI SQL*/
UPDATE 고객
      ,마일리지등급
SET 마일리지 = 마일리지 + 1000
WHERE 마일리지 BETWEEN 하한마일리지 AND 상한마일리지
AND 등급명 = 'S';

-- 결과 확인
select 고객번호
      ,고객회사명
      ,마일리지
from 고객
INNER join  마일리지등급
on 마일리지 BETWEEN 하한마일리지 and 상한마일리지
where 등급명 = 'S';



/*예제7-15*/
DELETE FROM 주문
WHERE 주문번호 NOT IN (
                        SELECT DISTINCT 주문번호
                        FROM 주문세부
                      );

/*예제7-16*/
SELECT *
FROM 주문
WHERE 주문번호 = 'H0248';

SELECT *
FROM 주문세부
WHERE 주문번호 = 'H0248';

/*ANSI SQL*/
DELETE 주문
      ,주문세부
FROM 주문
INNER JOIN 주문세부
ON 주문.주문번호 = 주문세부.주문번호
WHERE 주문.주문번호 = 'H0248';

/*Non-ANSI SQL*/
DELETE 주문
      ,주문세부
FROM 주문
    ,주문세부
WHERE 주문.주문번호 = 주문세부.주문번호
AND 주문.주문번호 = 'H0248';

/*예제7-17*/
SELECT 고객.*
FROM 고객
LEFT OUTER JOIN 주문
ON 고객.고객번호 = 주문.고객번호
WHERE 주문.고객번호 IS NULL;

DELETE 고객
FROM 고객
LEFT JOIN 주문
ON 고객.고객번호 = 주문.고객번호
WHERE 주문.고객번호 IS NULL;

SELECT *
FROM 고객
WHERE 고객번호 IN ('BQQZA', 'RISPA', 'SSAFI', 'TTRAN');









