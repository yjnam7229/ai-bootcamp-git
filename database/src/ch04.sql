/*Ch04 예제*/

/*예제4-1 고객 테이블에서 고객번호, 도시, 지역의 개수를 조회*/
SELECT COUNT(*)
	, COUNT(고객번호)
    , COUNT(도시)
    , COUNT(지역)
FROM 고객;    

/*예제4-2 고객 테이블의 마일리지 컬럼에 대하여 마일리지 합과 평균 마일리지, 최소 마일리지와 최대 마일리지를 조회*/ 
SELECT SUM(마일리지)
    , AVG(마일리지)
    , MIN(마일리지)
    , MAX(마일리지)
FROM 고객;

/*예제4-3 고객 테이블에서 ‘서울특별시’ 고객에 대해 마일리지합, 평균마일리지, 최소마일리지, 최대마일리지를 조회*/
SELECT SUM(마일리지)
    , AVG(마일리지)
    , MIN(마일리지)
    , MAX(마일리지)
FROM 고객
WHERE 도시 LIKE '서울특별시%';
 
/*예제4-4 고객 테이블에서 도시별 고객의 수와 해당 도시 고객들의 평균마일리지를 조회*/
SELECT 도시
      , COUNT(*) AS 고객수
      , AVG(마일리지) AS 평균마일리지
FROM 고객
GROUP BY 도시;   /*카테고리명 그룹핑, 하나의 이름이 나옴, 해당 도시의 카운터, 평균의 출력이 가능함ALTER*/  

/*예제4-5*/
/*담당자직위별로 묶고, 같은 담당자직위에 대해서는 도시별로 묶어서 집계한 결과(고객수와 평균 마일리지)를 보이세요. (이때 담당자직위 순, 도시 순으로 정렬하기)*/
SELECT 담당자직위
      , 도시
      , COUNT(*) AS 고객수
      , AVG(마일리지) AS 평균마일리지
FROM 고객    
GROUP BY 담당자직위, 도시
ORDER BY 1, 2;  /*ORDER BY 담당자직위, 도시*/

/*예제4-6*/
/*고객 테이블에서 도시별로 그룹을 묶어서 고객수와 평균마일리지를 구하고, 이 중에서 고객수가 10명 이상인 레코드*/
SELECT 도시
	  , COUNT(*) AS 고객수  /*COUNT(*) 전체 TOTAL 레코드 갯수*/
      , AVG(마일리지) AS 평균마일리지
  FROM 고객
GROUP BY 도시
HAVING COUNT(*) >= 10; /*그룹핑 되어진 결과에 추가 조건*/
  
/*예제4-7*/
/*고객번호가 ‘T’로 시작하는 고객에 대해 도시별로 묶어서 고객의 마일리지 합을 구하시오. 이때 마일리지 합이 1,000점 이상인 레코드*/
SELECT 도시
	  , SUM(마일리지) 
  FROM 고객
 WHERE 고객번호 LIKE 'T%'
 GROUP BY 도시
HAVING SUM(마일리지) >= 1000; 

/*예제4-8*/
/*지역이 NULL인 고객에 대해 도시별로 고객수와 평균마일리지를 보이세요. 이때 맨 마지막 행에 전체 고객수와 전체 고객에 대한 평균마일리지도 함께 볼 수 있도록 작성*/
/*WITH ROLLUP 사용*/
SELECT 도시
      , COUNT(*) AS 고객수
      , SUM(마일리지) 
  FROM 고객
WHERE 지역 IS NOT NULL  
GROUP BY 도시
WITH ROLLUP; 

SELECT IFNULL(도시, '총계') AS 도시, COUNT(*) AS 고객수, AVG(마일리지) AS 평균마일지
 FROM 고객
WHERE 지역 IS NULL  
GROUP BY 도시
WITH ROLLUP;

/*예제4-9*/
/*담당자직위에 ‘마케팅’이 들어가 있는 고객에 대해 고객(담당자직위, 도시)별 고객수를 보이세요. 담당자직위별 고객수와 전체 고객수도 함께 볼 수 있도록 조회*/
SELECT 담당자직위, 도시, COUNT(*) AS 고객수
 FROM 고객
WHERE 담당자직위 LIKE '%마케팅%'
GROUP BY 담당자직위, 도시
WITH ROLLUP; 

SELECT 지역, COUNT(*) AS 고객수
FROM 고객
WHERE 담당자직위 = '대표 이사'
GROUP BY 지역
WITH ROLLUP;

SELECT 지역, COUNT(*) AS 고객수, GROUPING(지역) AS 구분
FROM 고객
WHERE 담당자직위 = '대표 이사'
GROUP BY 지역
WITH ROLLUP;

/*예제4-10*/
/*당담자직위가 ‘대표 이사’인 고객에 대하여 지역별로 묶어서 고객수를 보이고, 전체 고객수도 함께 조회*/
SELECT 지역, COUNT(*) AS 고객수
FROM 고객
WHERE 담당자직위 = '대표 이사'
GROUP BY 지역
WITH ROLLUP;

SELECT 지역, COUNT(*) AS 고객수, GROUPING(지역) AS 구분
FROM 고객
WHERE 담당자직위 = '대표 이사'
GROUP BY 지역
WITH ROLLUP;

/*예제4-11 GROUP_CONCAT( )을 사용하여 사원 테이블에 들어있는 이름을 한 행에 나열하세요*/
SELECT GROUP_CONCAT(이름)
 FROM 사원;
 
/*예제4-12 고객 테이블에 들어있는 지역을 한 행에 나열하되 중복되는 지역은 한 번씩만 보이세요*/
SELECT GROUP_CONCAT(DISTINCT(지역))
 FROM 고객;
 
/*예제4-13 고객 테이블에서 도시별로 고객회사명을 나열하세요*/
SELECT 도시, GROUP_CONCAT(고객회사명) AS 고객회사목록
  FROM 고객
GROUP BY 도시;  
 



