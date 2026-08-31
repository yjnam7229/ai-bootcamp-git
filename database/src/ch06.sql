/*Ch06 예제*/

-- 단일행 서브쿼리
/*예제6-1 최고 마일리지를 보유한 고객의 정보를 보이세요*/
SELECT MAX(마일리지) 
  FROM 고객; 
  
 /*서브쿼리(SubQuery) : 실행의 순서는 서브쿼리문 부터 수행*/
SELECT 고객번호, 고객회사명, 담당자명, 마일리지
  FROM 고객 /*메인 SELECT문*/
 WHERE 마일리지 = (SELECT MAX(마일리지)   /*서브쿼리(SubQuery)문*/
					  FROM 고객);

/*예제6-2 주문번호 ‘H0250’을 주문한 고객에 대해 고객회사명과 담당자명을 보이세요*/
SELECT 고객회사명, 담당자명
  FROM 고객
  WHERE 고객번호 = (SELECT 고객번호 FROM 주문
					WHERE 주문번호 = 'H0250');
-- JOIN 이용
SELECT 고객회사명, 담당자명
  FROM 고객
INNER JOIN 주문
   ON 고객.고객번호 = 주문.고객번호
WHERE 주문번호 = 'H0250';  

/*SELECT 고객번호 FROM 주문 WHERE 주문번호 = 'H0250'*/

/*예제6-3 ‘부산광역시’고객의 최소 마일리지보다 더 큰 마일리지를 가진 고객 정보를 보이세요*/
SELECT 담당자명, 고객회사명 
FROM 고객
WHERE 마일리지 > (SELECT MIN(마일리지) FROM 고객
                     WHERE 도시 = '부산광역시');

-- 복수 행 서브쿼리 
/*예제6-4 ‘부산광역시’ 고객이 주문한 주문 건수를 보이세요*/
SELECT COUNT(*) AS 주문건수
 FROM 주문
WHERE 고객번호 IN (SELECT 고객번호 FROM 고객 WHERE 도시 = '부산광역시'); -- 비교연산자를 사용하면 단일행 리턴이므로 에러 발생 -> 복수행 비교연산자 사용


/*예제6-5 부산광역시’ 전체 고객의 마일리지보다 마일리지가 큰 고객의 정보를 보이세요.*/
/*ANY : 수행된 결과의 최소값*/
SELECT 담당자명, 고객회사명, 마일리지
  FROM 고객
 WHERE 마일리지 > ANY (SELECT 마일리지 FROM 고객
                        WHERE 도시 = '부산광역시');


/*예제6-6 각 지역의 어느 평균 마일리지보다도 마일리지가 큰 고객의 정보를 보이세요.*/
/*ALL : 수행된 결과의 최대값*/
SELECT 담당자명, 고객회사명, 마일리지
  FROM 고객
 WHERE 마일리지 > ALL(SELECT AVG(마일리지) FROM 고객 GROUP BY 지역); 
 
/*예제6-7 한 번이라도 주문한 적이 있는 고객의 정보를 보이세요.*/
SELECT 고객번호, 고객회사명
  FROM 고객
 WHERE EXISTS (SELECT * FROM 주문 WHERE 고객번호 = 고객.고객번호);
 
 /*EXIST와 동일한 결과*/
 SELECT 고객번호, 고객회사명
  FROM 고객
 WHERE 고객번호 IN (SELECT DISTINCT 고객번호 FROM 주문);

-- JOIN 이용 
SELECT 고객.고객번호, 고객회사명
 FROM 고객
 INNER JOIN 주문
    ON 고객.고객번호 = 주문.고객번호; 

/*예제6-8 고객 전체의 평균마일리지보다 평균마일리지가 큰 도시에 대해 도시명과 도시의 평균마일리지를 보이세요.*/
SELECT 도시, AVG(마일리지) AS 평균마일리지
 FROM 고객
GROUP BY 도시
HAVING AVG(마일리지) > (SELECT AVG(마일리지) FROM 고객);

-- 인라인 뷰 Inline View, FROM절에서도 서브쿼리 사용
/*예제6-9 담당자명, 고객회사명, 마일리지, 도시, 해당 도시의 평균마일리지를 보이세요. 그리고 고객이 위치하는 도시의 평균마일리지와 각 고객의 마일리지 간의 차이도 함께 보이세요.*/ 
 SELECT 담당자명
     , 고객회사명
     , 마일리지, 도시
     , 도시별요약.도시_평균마일리지
     , 도시별요약.도시_평균마일리지 - 마일리지 AS 차이
 FROM 고객 
     , (SELECT AVG(마일리지) AS 도시_평균마일리지 FROM 고객 GROUP BY 도시) 도시별요약;     
     
SELECT C.담당자명
     , C.고객회사명
     , C.마일리지
     , C.도시
     , (SELECT AVG(마일리지) FROM 고객 WHERE 도시 = C.도시) AS 도시_평균마일리지
     , (SELECT AVG(마일리지) FROM 고객 WHERE 도시 = C.도시) - C.마일리지 AS 차이
  FROM 고객 C;       
 
 -- 스칼라 쿼리문
 /*예제6-10 고객번호, 담당자명과 고객의 최종 주문 일을 보이세요.*/  
SELECT 고객번호
     , 담당자명
     , (SELECT MAX(주문일) 
          FROM 주문 
         WHERE 고객번호 = 고객.고객번호) AS 최종주문일
  FROM 고객;

-- CTE(Common Tabel Expression) 쿼리로 만든 임시 데이터 셋, WITH절에서 정의
/*예제6-9를 CTE를 사용하여 작성하세요*/
WITH 도시별요약 AS 
	(SELECT 도시, AVG(마일리지) AS 도시_평균마일리지 
       FROM 고객
      GROUP BY 도시 
	)
SELECT 담당자명
     , 고객회사명
     , 마일리지 
     , 도시별요약.도시_평균마일리지
     , 도시별요약.도시_평균마일리지 - 마일리지 AS 차이
 FROM 고객, 도시별요약
WHERE 고객.도시 = 도시별요약.도시;

/*예제6-12 사원 테이블에서 사원번호, 사원의 이름, 상사의 사원번호, 상사의 이름을 보이세요*/
SELECT 사원번호
	 , 이름
     , 상사번호
     , (SELECT 이름 FROM 사원 AS 상사 WHERE 상사.사원번호 = 사원.상사번호) AS 상사이름
  FROM 사원;

-- 다중 컬럼 서브쿼리(Multi-Column SubQuery)
/*예제6-13 각 도시마다 최고 마일리지를 보유한 고객의 정보를 보이세요.*/
SELECT 도시, 담당자명, 고객회사명, 마일리지
  FROM 고객
 WHERE (도시, 마일리지) IN (SELECT 도시, MAX(마일리지) 
									 FROM 고객 
									GROUP BY 도시);
  
  

