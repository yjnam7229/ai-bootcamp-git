/* 예제2-1 */
SELECT * 
FROM 고객;

/* 예제2-2 */
SELECT 고객번호
	, 담당자명
	, 고객회사명
	, 마일리지 AS 포인트
	, 마일리지 * 1.1 '10% 인상된 마일리지'
FROM 고객;

/* 예제2-3 */
SELECT 고객번호
	, 담당자명
    , 마일리지
FROM 고객
WHERE 마일리지 >= 100000;


/* 예제2-4 */
SELECT 고객번호
	, 담당자명
    , 도시
    , 마일리지 AS 포인트
FROM 고객
WHERE 도시 = '서울특별시'
ORDER BY 마일리지 DESC; -- ASC

/* 예제2-5 */
SELECT *
FROM 고객
LIMIT 3;

/* 예제2-6 */
SELECT *
FROM 고객
ORDER BY 마일리지 DESC
LIMIT 3;

/* 예제2-7 */
SELECT DISTINCT 도시
FROM 고객;

/* 예제2-8 */
SELECT 23 + 5 AS 더하기
      ,23 - 5 AS 빼기
      ,23 * 5 AS 곱하기
      ,23 / 5 AS 실수나누기
      ,23 DIV 5 AS 정수나누기
      ,23 % 5 AS 나머지1
      ,23 MOD 5 AS 나머지2;

/* 예제2-9 */
SELECT 23 >= 5
      ,23 <= 5
      ,23 > 23 
      ,23 < 23
      ,23 = 23
      ,23 != 23
      ,23 <> 23;

/* 예제2-10 */
SELECT *
FROM 고객
WHERE 담당자직위 <> '대표 이사';

/* 예제2-11 */
SELECT *
FROM 고객
WHERE 도시 = '부산광역시'
AND 마일리지 < 1000;

/* 예제2-12 */
SELECT 고객번호
	, 담당자명
    , 마일리지
    , 도시
FROM 고객
WHERE 도시 = '부산광역시'
UNION
SELECT 고객번호
	, 담당자명
    , 마일리지
    , 도시
FROM 고객
WHERE 마일리지 < 1000
ORDER BY 고객번호;

-- OR 연산자 해결법
SELECT 고객번호
	, 담당자명
    , 마일리지
    , 도시
FROM 고객
WHERE 도시 = '부산광역시'
OR 마일리지 < 1000
ORDER BY 고객번호;

/* 예제2-13 */
SELECT *
FROM 고객
WHERE 지역 IS NULL;

SELECT *
FROM 고객
WHERE 지역 = '';

UPDATE 고객
SET 지역 = NULL
WHERE 지역 = ''; 
 
/* 예제2-14 */
SELECT 고객번호, 담당자명, 담당자직위
FROM 고객
WHERE 담당자직위 = '영업 과장' 
OR 담당자직위 = '마케팅 과장';

SELECT 고객번호, 담당자명, 담당자직위
FROM 고객
WHERE 담당자직위 IN ('영업 과장', '마케팅 과장');


/* 예제2-15 */
SELECT 담당자명, 마일리지
FROM 고객
WHERE 마일리지 BETWEEN 100000 AND 200000;
 
/* 예제2-16 */
SELECT * 
FROM 고객
WHERE 도시 LIKE '%광역시'
AND (고객번호 LIKE '_C%' OR 고객번호 LIKE '__C%');    /*이면서AND*/

