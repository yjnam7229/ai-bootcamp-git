-- DML 데이터 조작어
/*Ch07 예제*/

/*예제7-1  부서 테이블에 다음 레코드를 삽입하세요.*/
INSERT INTO 부서
VALUES ('A5', '마케팅부');

/*예제7-2  제품 테이블에 다음 레코드를 추가하세요. 제품번호: 91, 제품명: 연어피클소스, 단가: 5000, 재고: 40*/
INSERT INTO 제품
VALUES ('91', '연어피클소스'
	  , NULL
      , 5000
      , 40
     );

/*예제7-3  제품 테이블에 다음 레코드를 추가하세요. 제품번호: 90, 제품명: 연어핫소스, 단가: 4000, 재고: 50*/
INSERT INTO 제품
VALUES ('90', '연어피클소스'
	  , NULL
      , 4000
      , 50
     );

/*예제7-4  사원 테이블에 한 문장으로 세 명의 레코드를 추가하세요.*/
-- 사원번호: E20, 이름: 김사과, 직위: 수습사원, 성별: 남, 입사일: 현재 날짜
-- 사원번호: E21, 이름: 박바나나, 직위: 수습사원, 성별: 여, 입사일: 현재 날짜
-- 사원번호: E22, 이름: 정오렌지, 직위: 수습사원, 성별: 여, 입사일: 현재 날짜
INSERT INTO 사원 (사원번호, 이름, 직위, 성별, 입사일)
 VALUES ('E20', '김사과', '수습사원', '남', curdate()),
		('E21', '박바나나', '수습사원', '여', curdate()),
        ('E22', '정오렌지', '수습사원', '여', curdate());
        
/*예제7-5 사원번호가 ‘E20’인 사원의 데이터를 다음과 같이 수정하세요. (사원번호: E20, 이름: 김사과) → (사원번호: E20, 이름: 김레몬)*/
UPDATE 사원
  SET 이름 = '김레문'
 WHERE 사원번호 = 'E20';

/*예제7-6  제품번호가 91인 제품에 대하여 포장 단위를 추가하세요.*/
UPDATE 제품
  SET 단가 = 6000
 WHERE 제품번호 = 91;
 
 UPDATE 제품
  SET 포장단위 = '200 ml bottles'
 WHERE 제품번호 = 91;

/*예제7-7 제품번호가 91인 제품에 대하여 단가를 10% 인상하고, 재고에서 10을 뺀 값으로 변경하세요.*/
UPDATE 제품
  SET 단가 = 단가 * 1.1
     ,재고 = 재고 - 10
 WHERE 제품번호 = 91;
 
 SELECT 단가, 단가*1.1, 재고, 재고 - 10
 FROM 제품
 WHERE 제품번호 = 91;
 
/*예제7-8 제품 테이블에서 제품번호가 91인 레코드를 삭제하세요.*/
DELETE FROM 제품
 WHERE 제품번호 = 91;

/*예제7-9 사원 테이블에서 입사일이 가장 늦은 사원 3명의 레코드를 삭제하세요.*/
DELETE FROM 사원 
ORDER BY 입사일 DESC
LIMIT 3;

/*예제7-10 91번 제품이 없다면 레코드를 추가하고, 이미 존재한다면 값을 변경하세요*/ 
INSERT INTO 제품(제품번호, 제품명, 단가, 재고)
 VALUES (91, '연어피클핫소스', 6000, 50)
  ON DUPLICATE KEY UPDATE 제품번호 = 91
						, 제품명 = '연어피클핫소스'
                        , 단가 = 6000
                        , 재고 = 50;
 

/*예제7-11 고객주문요약 테이블을 만들고, 레코드를 추가하세요*/
CREATE TABLE 고객주문요약(
	고객번호 CHAR(5) PRIMARY KEY,
    고객회사명 VARCHAR(50),
    주문건수 INT,
    최종주문일 DATE
);

INSERT INTO 고객주문요약
      SELECT 고객.고객번호, 고객회사명, COUNT(*), MAX(주문일)
       FROM 고객, 주문
	  WHERE 고객.고객번호 = 주문.고객번호
      GROUP BY 고객.고객번호, 고객회사명;


/*예제7-12 제품번호가 91인 제품의 단가를 ‘소스’ 제품들의 평균 단가로 변경하세요.*/
UPDATE 제품
   SET 단가 = (SELECT *
                 FROM (SELECT AVG(단가) 
                         FROM 제품 
						WHERE 제품명 LIKE '%소스%') AS t) 
  WHERE 제품번호 = 91;
  
  SELECT AVG(단가) 
  FROM 제품 
 WHERE 제품명 LIKE '%소스%'; 
 
/*예제7-13 한 번이라도 주문한 적이 있는 고객의 마일리지를 10% 인상하세요*/
UPDATE 고객, (SELECT DISTINCT 고객번호 FROM 주문) AS 주문고객
SET 마일리지 = 마일리지 * 1.1
WHERE 고객.고객번호 IN (주문고객.고객번호);

-- 결과 확인
SELECT * FROM 고객
WHERE 고객번호 IN (SELECT DISTINCT 고객번호 FROM 주문);

/*예제7-14 마일리지등급이 ‘S’인 고객의 마일리지에 1000점씩 추가하세요*/
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

SET SQL_SAFE_UPDATES = 0;
SET SQL_SAFE_UPDATES = 1;

/*예제7-15 주문 테이블에는 존재하나 주문세부 테이블에는 존재하지 않는 주문번호를 주문 테이블에서 삭제*/
DELETE FROM 주문
WHERE 주문번호 NOT IN (SELECT DISTINCT 주문번호 FROM 주문세부);

SELECT *
FROM 주문
WHERE 주문번호 = 'H1077';

/*예제7-16 주문번호 ‘H0248’에 대한 내역을 주문 테이블과 주문세부 테이블에서 모두 삭제하세요. 하나의 문장으로 작업을 수행*/
SELECT *
FROM 주문
WHERE 주문번호 = 'H0248';

SELECT *
FROM 주문세부
WHERE 주문번호 = 'H0248';

/*ANSI SQL*/
DELETE 주문, 주문세부
 FROM 주문 
 INNER JOIN 주문세부
   ON 주문.주문번호 = 주문세부.주문번호
 WHERE 주문.주문번호 = 'H0248';  

/*Non-ANSI SQL*/
DELETE 주문, 주문세부
 FROM 주문, 주문세부 
 WHERE 주문.주문번호 = 주문세부.주문번호
   AND 주문.주문번호 = 'H0248';  
 
/*예제7-17 한 번도 주문한 적이 없는 고객의 정보를 삭제하세요.*/
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
 
 
 


  